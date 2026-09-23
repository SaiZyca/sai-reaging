#!/usr/bin/env python3
"""Validate the materialized EXP-001 source manifest."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

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
    p.add_argument("--expected-count", type=int, default=8)
    return p.parse_args()


def main():
    args = parse_args()
    rows = load_dataset_manifest(args.manifest)
    errors = []

    if len(rows) != args.expected_count:
        errors.append(f"expected {args.expected_count} rows, found {len(rows)}")
    sample_ids = [r["sample_id"] for r in rows]
    subject_ids = [r["subject_id"] for r in rows]
    if len(set(sample_ids)) != len(sample_ids):
        errors.append("sample_id values must be unique")
    if len(set(subject_ids)) != len(subject_ids):
        errors.append("subject_id values must be unique")

    genders = Counter()
    for row in rows:
        sid = row["sample_id"]
        try:
            age = int(float(row["source_age"]))
            if not 48 <= age <= 52:
                errors.append(f"{sid}: source_age {age} outside [48,52]")
        except Exception:
            errors.append(f"{sid}: invalid source_age {row['source_age']!r}")

        try:
            genders[normalize_gender_label(row["gender_label"])] += 1
        except Exception as e:
            errors.append(f"{sid}: {e}")

        try:
            yaw = float(row["yaw_deg"])
            if abs(yaw) > 20:
                errors.append(f"{sid}: |yaw_deg|={abs(yaw)} > 20")
        except Exception:
            errors.append(f"{sid}: invalid yaw_deg {row['yaw_deg']!r}")

        if not parse_bool(row["selection_gate_pass"]):
            errors.append(f"{sid}: selection_gate_pass is not true")

        source = resolve_source_path(args.dataset_root, row["source_path"])
        if not source.exists():
            errors.append(f"{sid}: source file not found: {source}")
        else:
            expected = row["source_sha256"].strip().lower()
            if not expected:
                errors.append(f"{sid}: source_sha256 is empty")
            else:
                actual = sha256_file(source)
                if actual.lower() != expected:
                    errors.append(
                        f"{sid}: SHA mismatch expected {expected}, got {actual}"
                    )

    if genders and genders != Counter({"M": 4, "F": 4}):
        errors.append(f"expected dataset-label balance 4 M / 4 F, found {dict(genders)}")

    if errors:
        print("Manifest validation FAILED")
        for err in errors:
            print(f"- {err}")
        raise SystemExit(2)

    print(
        f"Manifest validation OK: rows={len(rows)}, "
        f"identities={len(set(subject_ids))}, genders={dict(genders)}"
    )


if __name__ == "__main__":
    main()
