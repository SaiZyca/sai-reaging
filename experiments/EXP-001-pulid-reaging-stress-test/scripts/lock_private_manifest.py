#!/usr/bin/env python3
"""Create a license-safe repository lock for the private AgeDB manifest."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import yaml

from common import (
    load_dataset_manifest,
    normalize_gender_label,
    parse_bool,
    resolve_source_path,
    sha256_file,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--dataset-root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    return p.parse_args()


def main():
    args = parse_args()
    rows = load_dataset_manifest(args.manifest)
    if len(rows) != 8:
        raise RuntimeError(f"Expected 8 private manifest rows, found {len(rows)}")

    ages = [int(float(r["source_age"])) for r in rows]
    genders = Counter(normalize_gender_label(r["gender_label"]) for r in rows)
    subject_ids = [r["subject_id"] for r in rows]

    if len(set(subject_ids)) != 8:
        raise RuntimeError("Expected 8 distinct subject identities")
    if min(ages) < 48 or max(ages) > 52:
        raise RuntimeError(f"Source ages outside [48,52]: {sorted(ages)}")
    if genders != Counter({"M": 4, "F": 4}):
        raise RuntimeError(f"Expected 4 M / 4 F, found {dict(genders)}")

    for row in rows:
        sid = row["sample_id"]
        if not parse_bool(row["selection_gate_pass"]):
            raise RuntimeError(f"{sid}: selection_gate_pass is not true")
        yaw = float(row["yaw_deg"])
        if abs(yaw) > 20:
            raise RuntimeError(f"{sid}: |yaw_deg|={abs(yaw)} > 20")
        source = resolve_source_path(args.dataset_root, row["source_path"])
        if not source.exists():
            raise RuntimeError(f"{sid}: source file not found: {source}")
        expected = row["source_sha256"].strip().lower()
        if not expected:
            raise RuntimeError(f"{sid}: source_sha256 is empty")
        actual = sha256_file(source)
        if actual.lower() != expected:
            raise RuntimeError(
                f"{sid}: source SHA mismatch expected {expected}, got {actual}"
            )

    lock = {
        "schema_version": "0.1",
        "experiment_id": "EXP-001",
        "dataset": "AgeDB",
        "private_manifest": {
            "path": "data/private/EXP-001/dataset_manifest.csv",
            "sha256": sha256_file(args.manifest),
            "row_count": len(rows),
        },
        "selection_contract": {
            "source_age_range": [48, 52],
            "distinct_identities": len(set(subject_ids)),
            "gender_counts": {"M": genders["M"], "F": genders["F"]},
            "one_source_image_per_identity": True,
            "deterministic_selection_seed": 20260923,
        },
        "access": {
            "terms_verified_at": "2026-09-23",
            "official_page": "https://ibug.doc.ic.ac.uk/resources/agedb/",
            "use_scope": "non-commercial research only",
            "annotations_redistributable": False,
            "access_acquired": True,
        },
        "execution": {
            "manifest_validation_passed": True,
            "source_hashes_verified": True,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(lock, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"wrote license-safe manifest lock: {args.output}")


if __name__ == "__main__":
    main()
