#!/usr/bin/env python3
"""Finalize the private 8-row EXP-001 AgeDB manifest from a reviewed pool."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "y"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--candidates",
        type=Path,
        default=Path("data/private/EXP-001/dataset_candidates.csv"),
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path("data/private/EXP-001/dataset_manifest.csv"),
    )
    p.add_argument("--per-gender", type=int, default=4)
    return p.parse_args()


def is_true(value: str) -> bool:
    return str(value).strip().lower() in TRUE_VALUES


def main() -> None:
    args = parse_args()
    with args.candidates.open("r", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise RuntimeError(f"No rows found in {args.candidates}")

    selected = []
    for gender in ("F", "M"):
        group = [
            r for r in rows
            if r["gender_label"].strip().upper() == gender
            and is_true(r.get("manual_gate_pass", ""))
        ]
        group.sort(key=lambda r: int(r["selection_rank"]))

        seen_subjects = set()
        chosen = []
        for row in group:
            subject = row["subject_id"]
            if subject in seen_subjects:
                continue
            seen_subjects.add(subject)
            chosen.append(row)
            if len(chosen) == args.per_gender:
                break

        if len(chosen) != args.per_gender:
            raise RuntimeError(
                f"Need {args.per_gender} manually approved distinct {gender} identities; "
                f"found {len(chosen)}. Approve more valid candidates or regenerate a larger review pool."
            )
        selected.extend(chosen)

    selected.sort(key=lambda r: (r["gender_label"], int(r["selection_rank"])))

    fieldnames = [
        "sample_id",
        "subject_id",
        "source_path",
        "source_sha256",
        "source_age",
        "gender_label",
        "face_bbox_xyxy",
        "yaw_deg",
        "selection_gate_pass",
        "notes",
    ]
    out_rows = []
    for idx, row in enumerate(selected, 1):
        notes = f"candidate_id={row['candidate_id']}"
        manual_notes = row.get("manual_notes", "").strip()
        if manual_notes:
            notes += f"; {manual_notes}"
        out_rows.append(
            {
                "sample_id": f"src_{idx:02d}",
                "subject_id": row["subject_id"],
                "source_path": row["source_path"],
                "source_sha256": row["source_sha256"],
                "source_age": row["source_age"],
                "gender_label": row["gender_label"],
                "face_bbox_xyxy": row["face_bbox_xyxy"],
                "yaw_deg": row["yaw_deg"],
                "selection_gate_pass": "true",
                "notes": notes,
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    print(f"Wrote private AgeDB manifest: {args.output}")
    print("rows=8 identities=8 gender_counts={'F': 4, 'M': 4}")


if __name__ == "__main__":
    main()
