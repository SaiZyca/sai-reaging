#!/usr/bin/env python3
"""Verify EXP-001 checkpoint assets and emit a license-safe Git lock."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import yaml


PULID_SHA256 = "92c41c3af322b02e58e1b32842e4601e08c8f16ec1fe80089dbe957df510f51d"
ANTELOPE_GLINTR_SHA256 = "4ab1d6435d639628a6f3e5008dd4f929edf4c4124b1a7169e1048f9fef534cdf"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--asset-root", type=Path, default=Path("checkpoints/EXP-001"))
    p.add_argument(
        "--output",
        type=Path,
        default=Path(
            "experiments/EXP-001-pulid-reaging-stress-test/"
            "checkpoint_manifest.lock.yaml"
        ),
    )
    return p.parse_args()


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_digest(root: Path) -> dict:
    files = [
        p for p in root.rglob("*")
        if p.is_file() and ".cache" not in p.parts
    ]
    if not files:
        raise RuntimeError(f"No materialized files under {root}")
    digest = hashlib.sha256()
    total = 0
    for p in sorted(files, key=lambda x: x.relative_to(root).as_posix()):
        rel = p.relative_to(root).as_posix()
        file_sha = sha256_file(p)
        size = p.stat().st_size
        total += size
        digest.update(f"{rel}\0{size}\0{file_sha}\n".encode("utf-8"))
    return {
        "file_count": len(files),
        "total_bytes": total,
        "tree_sha256": digest.hexdigest(),
    }


def require_file(path: Path, label: str) -> dict:
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"Missing {label}: {path}")
    return {
        "filename": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def main() -> None:
    args = parse_args()
    root = args.asset_root.resolve()
    local_manifest_path = root / "checkpoint_manifest.local.yaml"
    if not local_manifest_path.exists():
        raise RuntimeError(
            f"Missing {local_manifest_path}. Run materialize_checkpoint_assets.py first."
        )
    local = yaml.safe_load(local_manifest_path.read_text(encoding="utf-8"))

    generation = root / "generation"
    evaluators = root / "evaluators"
    aux = root / "pulid_aux"

    pulid = require_file(generation / "pulid_flux_v0.9.1.safetensors", "PuLID")
    if pulid["sha256"] != PULID_SHA256:
        raise RuntimeError("PuLID v0.9.1 SHA256 does not match the canonical value")
    flux = require_file(generation / "flux1-dev.safetensors", "FLUX.1-dev")
    ae = require_file(generation / "ae.safetensors", "FLUX autoencoder")

    eva = require_file(
        aux / "eva_clip" / "EVA02_CLIP_L_336_psz14_s6B.pt",
        "EVA-CLIP",
    )
    glintr = require_file(
        aux / "antelope" / "models" / "antelopev2" / "glintr100.onnx",
        "AntelopeV2 glintr100",
    )
    if glintr["sha256"] != ANTELOPE_GLINTR_SHA256:
        raise RuntimeError("AntelopeV2 glintr100 SHA256 mismatch")

    face_det = require_file(
        aux / "facexlib" / "detection_Resnet50_Final.pth",
        "FaceXLib RetinaFace",
    )
    face_parse = require_file(
        aux / "facexlib" / "parsing_bisenet.pth",
        "FaceXLib BiSeNet",
    )
    face_parsenet = require_file(
        aux / "facexlib" / "parsing_parsenet.pth",
        "FaceXLib ParseNet",
    )

    adaface = require_file(
        evaluators / "adaface_ir101_webface12m.ckpt",
        "AdaFace R100 WebFace12M",
    )
    mivolo = require_file(
        evaluators / "mivolo_face_only_imdb_cleaned_age_gender.pth.tar",
        "MiVOLO face-only age+gender",
    )
    detector = require_file(
        evaluators / "yolov8x_person_face.pt",
        "MiVOLO face/person detector",
    )

    t5_dir = root / "text_encoders" / "xflux_text_encoders"
    clip_dir = root / "text_encoders" / "openai_clip_vit_large_patch14"
    t5_tree = tree_digest(t5_dir)
    clip_tree = tree_digest(clip_dir)

    hf = local["huggingface"]
    lock = {
        "schema_version": "0.1",
        "experiment_id": "EXP-001",
        "materialization": {
            "asset_bytes_committed_to_git": False,
            "local_asset_root": "checkpoints/EXP-001",
        },
        "generation": {
            "pulid": {
                **pulid,
                "repo_id": hf["pulid"]["repo_id"],
                "revision": hf["pulid"]["revision"],
            },
            "flux": {
                **flux,
                "repo_id": hf["flux"]["repo_id"],
                "revision": hf["flux"]["revision"],
            },
            "autoencoder": {
                **ae,
                "repo_id": hf["ae"]["repo_id"],
                "revision": hf["ae"]["revision"],
            },
            "t5": {
                "repo_id": hf["t5"]["repo_id"],
                "revision": hf["t5"]["revision"],
                **t5_tree,
            },
            "clip": {
                "repo_id": hf["clip"]["repo_id"],
                "revision": hf["clip"]["revision"],
                **clip_tree,
            },
        },
        "pulid_auxiliary": {
            "eva_clip": {
                **eva,
                "repo_id": hf["eva_clip"]["repo_id"],
                "revision": hf["eva_clip"]["revision"],
            },
            "antelopev2": {
                **glintr,
                "repo_id": hf["antelopev2"]["repo_id"],
                "revision": hf["antelopev2"]["revision"],
            },
            "facexlib_retinaface": face_det,
            "facexlib_bisenet": face_parse,
            "facexlib_parsenet": face_parsenet,
        },
        "evaluators": {
            "adaface_r100_webface12m": adaface,
            "mivolo_face_only_age_gender": mivolo,
            "mivolo_detector": detector,
        },
        "access": {
            "flux_gated_terms_required": True,
            "flux_license": "flux-1-dev-non-commercial-license",
            "google_drive_assets_from_official_upstream_links": True,
        },
        "verification": {
            "all_required_files_present": True,
            "known_pulid_sha256_verified": True,
            "known_antelope_glintr_sha256_verified": True,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(lock, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Checkpoint verification PASSED.")
    print(f"Wrote Git-safe checkpoint lock: {args.output}")


if __name__ == "__main__":
    main()
