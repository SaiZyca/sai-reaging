#!/usr/bin/env python3
"""Independent AdaFace identity evaluation for EXP-001."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image

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
    p.add_argument("--adaface-repo", required=True, type=Path)
    p.add_argument("--checkpoint", required=True, type=Path)
    p.add_argument("--checkpoint-sha256", default=None)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--dataset-root", required=True, type=Path)
    p.add_argument("--raw-manifest", required=True, type=Path)
    p.add_argument("--raw-dir", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def to_input(pil_rgb_image: Image.Image) -> torch.Tensor:
    np_img = np.array(pil_rgb_image)
    bgr_img = ((np_img[:, :, ::-1] / 255.0) - 0.5) / 0.5
    arr = np.ascontiguousarray(bgr_img.transpose(2, 0, 1))
    return torch.from_numpy(arr).float().unsqueeze(0)


def main():
    args = parse_args()
    expected_commit = "c60eaa786a42c03444f3df7096dbaf9d57ae010d"
    assert_git_revision(args.adaface_repo, expected_commit, "AdaFace")
    checkpoint_sha = assert_file_sha256(
        args.checkpoint, args.checkpoint_sha256, "AdaFace checkpoint"
    )

    sys.path.insert(0, str(args.adaface_repo))
    import net  # type: ignore
    from face_alignment import mtcnn  # type: ignore

    device = torch.device(args.device)
    aligner = mtcnn.MTCNN(device=args.device, crop_size=(112, 112))

    model = net.build_model("ir_101")
    state = torch.load(args.checkpoint, map_location="cpu")
    state_dict = state["state_dict"]
    model_state = {
        key[6:]: value for key, value in state_dict.items() if key.startswith("model.")
    }
    model.load_state_dict(model_state, strict=True)
    model.to(device).eval()

    def embed(path: Path) -> np.ndarray:
        image = Image.open(path).convert("RGB")
        _boxes, faces = aligner.align_multi(image, limit=1)
        if not faces:
            raise RuntimeError("AdaFace MTCNN alignment produced no face")
        tensor = to_input(faces[0]).to(device)
        with torch.no_grad():
            feature, _norm = model(tensor)
        return feature[0].detach().cpu().numpy().astype(np.float32)

    dataset_rows = load_dataset_manifest(args.manifest)
    source_by_sample = {r["sample_id"]: r for r in dataset_rows}
    raw_rows = read_jsonl(args.raw_manifest)
    existing = {
        r["run_id"] for r in read_jsonl(args.output)
        if r.get("identity_status") == "ok"
    }

    source_embeddings = {}
    source_errors = {}

    for i, row in enumerate(raw_rows, 1):
        run_id = row["run_id"]
        if run_id in existing and not args.overwrite:
            continue

        sample_id = row["sample_id"]
        source_info = source_by_sample[sample_id]
        source_path = resolve_source_path(args.dataset_root, source_info["source_path"])

        try:
            if sample_id not in source_embeddings and sample_id not in source_errors:
                try:
                    source_embeddings[sample_id] = embed(source_path)
                except Exception as e:
                    source_errors[sample_id] = f"{type(e).__name__}: {e}"

            if sample_id in source_errors:
                raise RuntimeError(f"source alignment/embedding failed: {source_errors[sample_id]}")

            generated_path = args.raw_dir / row["output_file"]
            gen_emb = embed(generated_path)
            src_emb = source_embeddings[sample_id]
            similarity = float(np.dot(src_emb, gen_emb))
            record = {
                "run_id": run_id,
                "sample_id": sample_id,
                "identity_status": "ok",
                "identity_similarity": similarity,
                "identity_evaluator": "AdaFace IR-101 WebFace12M",
                "adaface_commit": expected_commit,
                "adaface_checkpoint_sha256": checkpoint_sha,
            }
        except Exception as e:
            record = {
                "run_id": run_id,
                "sample_id": sample_id,
                "identity_status": "error",
                "identity_similarity": None,
                "identity_error": f"{type(e).__name__}: {e}",
                "identity_evaluator": "AdaFace IR-101 WebFace12M",
                "adaface_commit": expected_commit,
                "adaface_checkpoint_sha256": checkpoint_sha,
            }

        append_jsonl(args.output, record)
        print(f"[{i}/{len(raw_rows)}] identity {record['identity_status']} {run_id}")


if __name__ == "__main__":
    main()
