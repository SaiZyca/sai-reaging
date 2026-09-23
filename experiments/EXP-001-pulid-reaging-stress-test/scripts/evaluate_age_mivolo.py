#!/usr/bin/env python3
"""Face-only MiVOLO age evaluation for EXP-001."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

import cv2

from common import (
    append_jsonl,
    assert_file_sha256,
    assert_git_revision,
    load_dataset_manifest,
    read_jsonl,
    resolve_source_path,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--mivolo-repo", required=True, type=Path)
    p.add_argument("--checkpoint", required=True, type=Path)
    p.add_argument("--checkpoint-sha256", default=None)
    p.add_argument("--detector-weights", required=True, type=Path)
    p.add_argument("--detector-sha256", default=None)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--dataset-root", required=True, type=Path)
    p.add_argument("--raw-manifest", required=True, type=Path)
    p.add_argument("--raw-dir", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    expected_commit = "37475e3f8818b5f22448003feec3e64b01bfb188"
    assert_git_revision(args.mivolo_repo, expected_commit, "MiVOLO")
    checkpoint_sha = assert_file_sha256(
        args.checkpoint, args.checkpoint_sha256, "MiVOLO checkpoint"
    )
    detector_sha = assert_file_sha256(
        args.detector_weights, args.detector_sha256, "MiVOLO detector"
    )

    sys.path.insert(0, str(args.mivolo_repo))
    from mivolo.predictor import Predictor  # type: ignore

    predictor_cfg = SimpleNamespace(
        detector_weights=str(args.detector_weights),
        checkpoint=str(args.checkpoint),
        device=args.device,
        with_persons=False,
        disable_faces=False,
        draw=False,
    )
    predictor = Predictor(predictor_cfg, verbose=False)

    def predict_age(path: Path) -> float:
        image = cv2.imread(str(path))
        if image is None:
            raise RuntimeError(f"cv2.imread failed: {path}")
        result, _ = predictor.recognize(image)
        face_inds = result.get_bboxes_inds("face")
        if not face_inds:
            raise RuntimeError("MiVOLO detector produced no face")

        def area(ind: int) -> float:
            x1, y1, x2, y2 = result.get_bbox_by_ind(ind).cpu().tolist()
            return max(0.0, float(x2 - x1)) * max(0.0, float(y2 - y1))

        face_ind = max(face_inds, key=area)
        age = result.ages[face_ind]
        if age is None:
            raise RuntimeError("MiVOLO produced no age for selected face")
        return float(age)

    dataset_rows = load_dataset_manifest(args.manifest)
    source_by_sample = {r["sample_id"]: r for r in dataset_rows}
    raw_rows = read_jsonl(args.raw_manifest)
    existing = {
        r["run_id"] for r in read_jsonl(args.output)
        if r.get("age_status") == "ok"
    }

    source_ages = {}
    source_errors = {}

    for i, row in enumerate(raw_rows, 1):
        run_id = row["run_id"]
        if run_id in existing and not args.overwrite:
            continue

        sample_id = row["sample_id"]
        source_info = source_by_sample[sample_id]
        source_path = resolve_source_path(args.dataset_root, source_info["source_path"])

        try:
            if sample_id not in source_ages and sample_id not in source_errors:
                try:
                    source_ages[sample_id] = predict_age(source_path)
                except Exception as e:
                    source_errors[sample_id] = f"{type(e).__name__}: {e}"

            if sample_id in source_errors:
                raise RuntimeError(f"source age evaluation failed: {source_errors[sample_id]}")

            generated_path = args.raw_dir / row["output_file"]
            generated_age = predict_age(generated_path)
            record = {
                "run_id": run_id,
                "sample_id": sample_id,
                "age_status": "ok",
                "source_predicted_age": source_ages[sample_id],
                "generated_predicted_age": generated_age,
                "age_evaluator": "MiVOLO VOLO-D1 face-only",
                "mivolo_commit": expected_commit,
                "mivolo_checkpoint_sha256": checkpoint_sha,
                "detector_checkpoint_sha256": detector_sha,
            }
        except Exception as e:
            record = {
                "run_id": run_id,
                "sample_id": sample_id,
                "age_status": "error",
                "source_predicted_age": source_ages.get(sample_id),
                "generated_predicted_age": None,
                "age_error": f"{type(e).__name__}: {e}",
                "age_evaluator": "MiVOLO VOLO-D1 face-only",
                "mivolo_commit": expected_commit,
                "mivolo_checkpoint_sha256": checkpoint_sha,
                "detector_checkpoint_sha256": detector_sha,
            }

        append_jsonl(args.output, record)
        print(f"[{i}/{len(raw_rows)}] age {record['age_status']} {run_id}")


if __name__ == "__main__":
    main()
