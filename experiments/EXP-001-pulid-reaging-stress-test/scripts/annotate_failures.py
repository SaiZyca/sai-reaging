#!/usr/bin/env python3
"""Create the manual failure-annotation sheet for EXP-001."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from common import read_jsonl

FAILURE_TAGS = [
    "identity_drift",
    "weak_age_transformation",
    "texture_only_aging",
    "soft_tissue_shape_aging_suppression",
    "face_shape_drift",
    "expression_loss",
    "hair_age_leakage",
    "evaluator_face_detection_failure",
    "evaluator_alignment_failure",
    "background_or_composition_drift",
]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--raw-manifest", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    return p.parse_args()


def main():
    args = parse_args()
    rows = read_jsonl(args.raw_manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "run_id",
        "sample_id",
        "requested_age_delta",
        "treatment",
        "id_weight",
        "start_step",
        "seed",
        *FAILURE_TAGS,
        "reviewer",
        "notes",
    ]
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            out = {k: row.get(k, "") for k in fields}
            for tag in FAILURE_TAGS:
                out[tag] = ""
            writer.writerow(out)
    print(f"wrote {len(rows)} annotation rows to {args.output}")


if __name__ == "__main__":
    main()
