#!/usr/bin/env python3
"""Join evaluator outputs and compute EXP-001 paired metrics."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from common import read_jsonl, write_json


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--raw-manifest", required=True, type=Path)
    p.add_argument("--identity-jsonl", required=True, type=Path)
    p.add_argument("--age-jsonl", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--summary-output", required=True, type=Path)
    p.add_argument("--pareto-output", required=True, type=Path)
    return p.parse_args()


def median_or_none(values):
    vals = [float(v) for v in values if pd.notna(v)]
    return None if not vals else float(np.median(vals))


def main():
    args = parse_args()
    raw = pd.DataFrame(read_jsonl(args.raw_manifest))
    ids = pd.DataFrame(read_jsonl(args.identity_jsonl))
    ages = pd.DataFrame(read_jsonl(args.age_jsonl))

    if raw.empty:
        raise RuntimeError("raw manifest is empty")
    if ids.empty:
        raise RuntimeError("identity evaluator output is empty")
    if ages.empty:
        raise RuntimeError("age evaluator output is empty")

    raw = raw.drop_duplicates("run_id", keep="last")
    ids = ids.drop_duplicates("run_id", keep="last")
    ages = ages.drop_duplicates("run_id", keep="last")
    df = raw.merge(ids, on=["run_id", "sample_id"], how="left")
    df = df.merge(ages, on=["run_id", "sample_id"], how="left")

    df["evaluation_success"] = (
        (df["identity_status"] == "ok") & (df["age_status"] == "ok")
    )
    df["target_age_error"] = (
        df["generated_predicted_age"].astype(float) - df["target_age"].astype(float)
    ).abs()
    df["realized_age_delta"] = (
        df["generated_predicted_age"].astype(float)
        - df["source_predicted_age"].astype(float)
    )

    def attainment(row):
        req = float(row["requested_age_delta"])
        if req == 0 or pd.isna(row["realized_age_delta"]):
            return np.nan
        return float(row["realized_age_delta"]) / req

    df["signed_age_attainment"] = df.apply(attainment, axis=1)

    key_cols = ["sample_id", "requested_age_delta", "seed"]
    baseline = df[df["treatment"] == "no_pulid"].copy()
    if baseline.duplicated(key_cols).any():
        raise RuntimeError("duplicate no-PuLID baseline for a paired-analysis key")

    baseline = baseline[
        key_cols + [
            "identity_similarity",
            "realized_age_delta",
            "evaluation_success",
        ]
    ].rename(
        columns={
            "identity_similarity": "baseline_identity_similarity",
            "realized_age_delta": "baseline_realized_age_delta",
            "evaluation_success": "baseline_evaluation_success",
        }
    )
    df = df.merge(baseline, on=key_cols, how="left")

    def baseline_editable(row):
        req = float(row["requested_age_delta"])
        realized = row["baseline_realized_age_delta"]
        if req == 0 or pd.isna(realized) or not bool(row["baseline_evaluation_success"]):
            return False
        same_sign = math.copysign(1.0, float(realized)) == math.copysign(1.0, req)
        enough = abs(float(realized)) >= 0.5 * abs(req)
        return bool(same_sign and enough)

    df["baseline_editable_pair"] = df.apply(baseline_editable, axis=1)
    df["identity_gain_vs_baseline"] = (
        df["identity_similarity"].astype(float)
        - df["baseline_identity_similarity"].astype(float)
    )

    def retention(row):
        if not bool(row["baseline_editable_pair"]):
            return np.nan
        b = float(row["baseline_realized_age_delta"])
        if abs(b) < 1e-9 or pd.isna(row["realized_age_delta"]):
            return np.nan
        return float(row["realized_age_delta"]) / b

    df["age_edit_retention_vs_baseline"] = df.apply(retention, axis=1)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.output, index=False)

    pulid = df[df["treatment"] == "pulid"].copy()
    groups = []
    for keys, g in pulid.groupby(
        ["requested_age_delta", "id_weight", "start_step"], dropna=False
    ):
        delta, weight, start = keys
        valid = g[g["evaluation_success"]]
        editable = valid[valid["baseline_editable_pair"]]
        groups.append(
            {
                "requested_age_delta": int(delta),
                "id_weight": float(weight),
                "start_step": int(start),
                "n_planned": int(len(g)),
                "n_evaluation_success": int(valid.shape[0]),
                "evaluation_success_rate": float(valid.shape[0] / len(g)) if len(g) else 0.0,
                "n_baseline_editable": int(editable.shape[0]),
                "median_identity_similarity": median_or_none(valid["identity_similarity"]),
                "median_identity_gain_vs_baseline": median_or_none(
                    valid["identity_gain_vs_baseline"]
                ),
                "median_target_age_error": median_or_none(valid["target_age_error"]),
                "median_age_edit_retention": median_or_none(
                    editable["age_edit_retention_vs_baseline"]
                ),
            }
        )

    pareto_df = pd.DataFrame(groups)
    pareto_df.to_csv(args.pareto_output, index=False)

    summary = {
        "planned_rows": int(len(df)),
        "evaluation_success_rows": int(df["evaluation_success"].sum()),
        "evaluation_success_rate": float(df["evaluation_success"].mean()),
        "baseline_editable_pairs": int(df["baseline_editable_pair"].sum()),
        "pulid_rows": int((df["treatment"] == "pulid").sum()),
        "no_pulid_rows": int((df["treatment"] == "no_pulid").sum()),
        "note": (
            "This file is descriptive experiment output. Architecture promotion/"
            "downgrade requires failure review and Experiment Closeout."
        ),
    }
    write_json(args.summary_output, summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
