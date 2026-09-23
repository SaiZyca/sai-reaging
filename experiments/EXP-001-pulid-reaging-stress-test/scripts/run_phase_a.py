#!/usr/bin/env python3
"""Batch generation runner for EXP-001 Phase A.

The runner imports the pinned upstream PuLID repository and calls its
FluxGenerator directly. No PuLID architecture is modified.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image

from common import (
    append_jsonl,
    assert_file_sha256,
    assert_git_revision,
    gender_token,
    iter_planned_runs,
    load_dataset_manifest,
    load_yaml,
    output_filename,
    read_jsonl,
    resolve_source_path,
    sha256_file,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--dataset-root", required=True, type=Path)
    p.add_argument("--pulid-repo", required=True, type=Path)
    p.add_argument("--pulid-checkpoint", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--raw-manifest", type=Path, default=None)
    p.add_argument("--sample-id", default=None)
    p.add_argument("--max-runs", type=int, default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--device", default="cuda")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    config = load_yaml(args.config)
    experiment_path = args.config.parent.parent / "experiment.yaml"
    experiment = load_yaml(experiment_path)

    expected_repo = experiment["implementation"]["upstream_commit"]
    assert_git_revision(args.pulid_repo, expected_repo, "PuLID")
    expected_pulid_sha = experiment["implementation"]["model_assets"]["pulid"]["sha256"]
    pulid_sha = assert_file_sha256(
        args.pulid_checkpoint, expected_pulid_sha, "PuLID-FLUX checkpoint"
    )

    rows = load_dataset_manifest(args.manifest)
    by_sample = {r["sample_id"]: r for r in rows}
    if len(by_sample) != len(rows):
        raise ValueError("dataset manifest contains duplicate sample_id values")

    gen_cfg = config["generation"]
    prompt_template = gen_cfg["prompt_template"]

    raw_manifest = args.raw_manifest or (args.output_dir.parent / "raw_manifest.jsonl")
    completed = {r["run_id"] for r in read_jsonl(raw_manifest)}
    args.output_dir.mkdir(parents=True, exist_ok=True)

    planned = list(iter_planned_runs(config, rows, args.sample_id))
    if args.max_runs is not None:
        planned = planned[: args.max_runs]

    if args.dry_run:
        print(f"planned_runs={len(planned)} completed={len(completed)}")
        for item in planned[:20]:
            print(item)
        return

    sys.path.insert(0, str(args.pulid_repo))
    from app_flux import FluxGenerator  # type: ignore

    upstream_args = SimpleNamespace(
        fp8=bool(gen_cfg["fp8"]),
        onnx_provider=str(gen_cfg["onnx_provider"]),
        pretrained_model=str(args.pulid_checkpoint),
        version=str(config["upstream"]["pulid_version"]),
    )
    generator = FluxGenerator(
        config["upstream"]["backbone_name"],
        args.device,
        bool(gen_cfg["offload"]),
        bool(gen_cfg["aggressive_offload"]),
        upstream_args,
    )

    for idx, run in enumerate(planned, 1):
        if run["run_id"] in completed and not args.overwrite:
            print(f"[{idx}/{len(planned)}] skip completed {run['run_id']}")
            continue

        src = by_sample[run["sample_id"]]
        source_path = resolve_source_path(args.dataset_root, src["source_path"])
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        source_sha = sha256_file(source_path)
        expected_source_sha = src["source_sha256"].strip()
        if expected_source_sha and source_sha.lower() != expected_source_sha.lower():
            raise RuntimeError(
                f"source SHA mismatch for {run['sample_id']}: "
                f"expected {expected_source_sha}, got {source_sha}"
            )

        prompt = prompt_template.format(
            target_age=run["target_age"], gender_token=gender_token(src["gender_label"])
        )
        id_image = None
        if run["treatment"] == "pulid":
            id_image = np.asarray(Image.open(source_path).convert("RGB"))

        out_name = output_filename(
            run["sample_id"],
            run["requested_age_delta"],
            run["treatment"],
            run["id_weight"],
            run["start_step"],
            run["seed"],
        )
        output_path = args.output_dir / out_name

        started = time.perf_counter()
        image, used_seed, _debug = generator.generate_image(
            width=int(gen_cfg["width"]),
            height=int(gen_cfg["height"]),
            num_steps=int(gen_cfg["num_steps"]),
            start_step=int(run["start_step"] or 0),
            guidance=float(gen_cfg["guidance"]),
            seed=int(run["seed"]),
            prompt=prompt,
            id_image=id_image,
            id_weight=float(run["id_weight"] or 0.0),
            neg_prompt="",
            true_cfg=float(gen_cfg["true_cfg"]),
            timestep_to_start_cfg=int(gen_cfg["timestep_to_start_cfg"]),
            max_sequence_length=int(gen_cfg["max_sequence_length"]),
        )
        elapsed = time.perf_counter() - started
        image.save(output_path)
        output_sha = sha256_file(output_path)

        record = {
            **run,
            "gender_label": src["gender_label"],
            "source_path": src["source_path"],
            "source_sha256": source_sha,
            "prompt": prompt,
            "output_file": out_name,
            "output_sha256": output_sha,
            "used_seed": int(used_seed),
            "generation_seconds": round(elapsed, 4),
            "pulid_repository_commit": expected_repo,
            "pulid_checkpoint_sha256": pulid_sha,
            "backbone": config["upstream"]["backbone_name"],
            "precision": gen_cfg["precision"],
            "num_steps": int(gen_cfg["num_steps"]),
            "guidance": float(gen_cfg["guidance"]),
            "true_cfg": float(gen_cfg["true_cfg"]),
            "width": int(gen_cfg["width"]),
            "height": int(gen_cfg["height"]),
        }
        append_jsonl(raw_manifest, record)
        print(f"[{idx}/{len(planned)}] wrote {output_path}")


if __name__ == "__main__":
    main()
