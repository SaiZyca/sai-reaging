#!/usr/bin/env python3
"""Prepare a private, deterministic AgeDB review pool for EXP-001.

This script parses AgeDB filename annotations locally, applies automatic
face/pose/resolution gates with the already materialized AntelopeV2 models,
and writes a private review CSV + contact sheet. Neither output belongs in Git.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import random
import re
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from insightface.app import FaceAnalysis


FILENAME_RE = re.compile(
    r"^(?P<image_id>\d+)_(?P<identity>.+)_(?P<age>\d+)_(?P<gender>[fm])\.(?P<ext>jpe?g|png)$",
    re.IGNORECASE,
)
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset-root", required=True, type=Path)
    p.add_argument("--antelope-root", required=True, type=Path)
    p.add_argument(
        "--output",
        type=Path,
        default=Path("data/private/EXP-001/dataset_candidates.csv"),
    )
    p.add_argument(
        "--contact-sheet",
        type=Path,
        default=Path("data/private/EXP-001/dataset_candidates_review.jpg"),
    )
    p.add_argument("--review-count-per-gender", type=int, default=12)
    p.add_argument("--minimum-per-gender", type=int, default=4)
    p.add_argument("--seed", type=int, default=20260923)
    p.add_argument("--age-min", type=int, default=48)
    p.add_argument("--age-max", type=int, default=52)
    p.add_argument("--max-yaw", type=float, default=20.0)
    p.add_argument("--min-face-side", type=float, default=112.0)
    p.add_argument("--det-size", type=int, default=640)
    p.add_argument("--provider", choices=["cuda", "cpu"], default="cpu")
    return p.parse_args()


def sha256_file(path: Path, chunk_size: int = 4 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def decode_image(path: Path) -> np.ndarray | None:
    data = np.fromfile(path, dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def parse_filename(path: Path) -> dict | None:
    m = FILENAME_RE.match(path.name)
    if not m:
        return None
    g = m.groupdict()
    return {
        "image_id": int(g["image_id"]),
        "subject_id": g["identity"],
        "source_age": int(g["age"]),
        "gender_label": g["gender"].upper(),
    }


def bbox_string(bbox: np.ndarray) -> str:
    vals = [round(float(x), 2) for x in bbox[:4]]
    return "[" + ",".join(f"{x:.2f}" for x in vals) + "]"


def make_contact_sheet(rows: list[dict], dataset_root: Path, output: Path) -> None:
    thumb = 256
    label_h = 44
    cols = 4
    rows_n = (len(rows) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * thumb, rows_n * (thumb + label_h)), "white")
    draw = ImageDraw.Draw(canvas)

    for idx, row in enumerate(rows):
        src = dataset_root / row["source_path"]
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            tile = ImageOps.fit(im, (thumb, thumb))
        x = (idx % cols) * thumb
        y = (idx // cols) * (thumb + label_h)
        canvas.paste(tile, (x, y))
        label = (
            f"{row['candidate_id']} age={row['source_age']} "
            f"{row['gender_label']} yaw={float(row['yaw_deg']):.1f}\n"
            f"face_min={float(row['face_min_side_px']):.0f}px"
        )
        draw.multiline_text((x + 4, y + thumb + 3), label, fill="black", spacing=2)

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, quality=92)


def main() -> None:
    args = parse_args()
    dataset_root = args.dataset_root.resolve()
    antelope_root = args.antelope_root.resolve()

    if not dataset_root.is_dir():
        raise FileNotFoundError(f"AgeDB root not found: {dataset_root}")
    if not (antelope_root / "models" / "antelopev2" / "glintr100.onnx").is_file():
        raise FileNotFoundError(
            "AntelopeV2 materialization not found under "
            f"{antelope_root / 'models' / 'antelopev2'}"
        )

    parsed = []
    parse_failures = 0
    for path in sorted(dataset_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        meta = parse_filename(path)
        if meta is None:
            parse_failures += 1
            continue
        if not args.age_min <= meta["source_age"] <= args.age_max:
            continue
        meta["path"] = path
        parsed.append(meta)

    if not parsed:
        raise RuntimeError(
            "No AgeDB files matching the expected "
            "<image_id>_<identity>_<age>_<gender> filename pattern "
            f"were found in age range [{args.age_min},{args.age_max}]."
        )

    providers = (
        ["CUDAExecutionProvider", "CPUExecutionProvider"]
        if args.provider == "cuda"
        else ["CPUExecutionProvider"]
    )
    app = FaceAnalysis(name="antelopev2", root=str(antelope_root), providers=providers)
    app.prepare(ctx_id=0 if args.provider == "cuda" else -1, det_size=(args.det_size, args.det_size))

    eligible = []
    reject = Counter()

    for idx, item in enumerate(parsed, 1):
        path = item["path"]
        img = decode_image(path)
        if img is None:
            reject["decode_failure"] += 1
            continue

        faces = app.get(img)
        if len(faces) != 1:
            reject[f"face_count_{len(faces)}"] += 1
            continue

        face = faces[0]
        bbox = np.asarray(face.bbox, dtype=np.float32)
        min_side = float(min(bbox[2] - bbox[0], bbox[3] - bbox[1]))
        if min_side < args.min_face_side:
            reject["face_too_small"] += 1
            continue

        pose = getattr(face, "pose", None)
        if pose is None or len(pose) < 2:
            reject["pose_unavailable"] += 1
            continue
        yaw = float(pose[1])
        if abs(yaw) > args.max_yaw:
            reject["yaw"] += 1
            continue

        rel = path.relative_to(dataset_root).as_posix()
        eligible.append(
            {
                "image_id": item["image_id"],
                "subject_id": item["subject_id"],
                "source_path": rel,
                "source_sha256": sha256_file(path),
                "source_age": item["source_age"],
                "gender_label": item["gender_label"],
                "face_bbox_xyxy": bbox_string(bbox),
                "yaw_deg": round(yaw, 4),
                "face_min_side_px": round(min_side, 2),
            }
        )
        if idx % 100 == 0:
            print(f"processed={idx}/{len(parsed)} eligible={len(eligible)}")

    review_rows = []
    for gender in ("F", "M"):
        group = sorted(
            (r for r in eligible if r["gender_label"] == gender),
            key=lambda r: (
                r["subject_id"].casefold(),
                int(r["image_id"]),
                r["source_path"],
            ),
        )
        rng = random.Random(args.seed)
        order = list(range(len(group)))
        rng.shuffle(order)

        chosen = []
        seen_subjects = set()
        for pos in order:
            row = group[pos]
            if row["subject_id"] in seen_subjects:
                continue
            seen_subjects.add(row["subject_id"])
            chosen.append(dict(row))
            if len(chosen) >= args.review_count_per_gender:
                break

        if len(chosen) < args.minimum_per_gender:
            raise RuntimeError(
                f"Only {len(chosen)} distinct automatically eligible {gender} "
                f"identities; need at least {args.minimum_per_gender} for the "
                "final cohort. Review the automatic gate contract before relaxing it."
            )
        if len(chosen) < args.review_count_per_gender:
            print(
                f"WARNING: requested {args.review_count_per_gender} {gender} review "
                f"candidates but only {len(chosen)} distinct automatically eligible "
                "identities are available; using all available candidates."
            )

        for rank, row in enumerate(chosen, 1):
            row["selection_rank"] = rank
            row["candidate_id"] = f"{gender}{rank:02d}"
            row["manual_gate_pass"] = ""
            row["manual_notes"] = ""
            review_rows.append(row)

    fieldnames = [
        "candidate_id",
        "selection_rank",
        "image_id",
        "subject_id",
        "source_path",
        "source_sha256",
        "source_age",
        "gender_label",
        "face_bbox_xyxy",
        "yaw_deg",
        "face_min_side_px",
        "manual_gate_pass",
        "manual_notes",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(review_rows)

    make_contact_sheet(review_rows, dataset_root, args.contact_sheet)

    print()
    print("AgeDB private review pool prepared.")
    print(f"parsed_age_range_files={len(parsed)}")
    print(f"automatically_eligible={len(eligible)}")
    print(f"review_rows={len(review_rows)}")
    print(
        "review_gender_counts="
        + str(dict(Counter(r["gender_label"] for r in review_rows)))
    )
    print(f"parse_failures_outside_expected_filename_pattern={parse_failures}")
    print(f"automatic_rejections={dict(reject)}")
    print(f"private_review_csv={args.output}")
    print(f"private_contact_sheet={args.contact_sheet}")
    print()
    print(
        "Next: inspect the contact sheet / source images and set manual_gate_pass "
        "to true only for candidates with no heavy occlusion, no sunglasses "
        "covering the eyes, and no extreme expression."
    )


if __name__ == "__main__":
    main()
