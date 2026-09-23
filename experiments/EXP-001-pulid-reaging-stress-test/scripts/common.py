#!/usr/bin/env python3
"""Shared helpers for EXP-001.

This module intentionally contains only experiment orchestration logic. It does
not modify PuLID, AdaFace, or MiVOLO model behavior.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, Optional

import yaml

REQUIRED_MANIFEST_COLUMNS = [
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


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_file_sha256(path: Path, expected: Optional[str], label: str) -> str:
    actual = sha256_file(path)
    if expected and actual.lower() != expected.lower():
        raise RuntimeError(
            f"{label} SHA256 mismatch: expected {expected}, got {actual} ({path})"
        )
    return actual


def git_head(repo_path: Path) -> str:
    out = subprocess.check_output(
        ["git", "-C", str(repo_path), "rev-parse", "HEAD"], text=True
    )
    return out.strip()


def assert_git_revision(repo_path: Path, expected: str, label: str) -> str:
    actual = git_head(repo_path)
    if actual != expected:
        raise RuntimeError(
            f"{label} revision mismatch: expected {expected}, got {actual} ({repo_path})"
        )
    return actual


def load_dataset_manifest(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Manifest has no header: {path}")
        missing = [c for c in REQUIRED_MANIFEST_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Manifest missing columns {missing}: {path}")
        return [dict(row) for row in reader]


def normalize_gender_label(value: str) -> str:
    v = value.strip().lower()
    if v in {"m", "male", "man"}:
        return "M"
    if v in {"f", "female", "woman"}:
        return "F"
    raise ValueError(f"Unsupported gender_label {value!r}; expected dataset-provided M/F")


def gender_token(value: str) -> str:
    return "man" if normalize_gender_label(value) == "M" else "woman"


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def resolve_source_path(dataset_root: Path, source_path: str) -> Path:
    p = Path(source_path)
    return p if p.is_absolute() else dataset_root / p


def run_id(
    sample_id: str,
    age_delta: int,
    treatment: str,
    id_weight: Optional[float],
    start_step: Optional[int],
    seed: int,
) -> str:
    w = "na" if id_weight is None else f"{id_weight:g}"
    s = "na" if start_step is None else str(start_step)
    return f"{sample_id}|d={age_delta:+d}|{treatment}|w={w}|s={s}|seed={seed}"


def output_filename(
    sample_id: str,
    age_delta: int,
    treatment: str,
    id_weight: Optional[float],
    start_step: Optional[int],
    seed: int,
) -> str:
    w = "na" if id_weight is None else f"{id_weight:g}"
    s = "na" if start_step is None else str(start_step)
    return (
        f"{sample_id}__d{age_delta:+03d}__{treatment}"
        f"__w{w}__s{s}__seed{seed}.png"
    )


def iter_planned_runs(
    config: Mapping,
    rows: Iterable[Mapping[str, str]],
    sample_id_filter: Optional[str] = None,
    seeds_override: Optional[Iterable[int]] = None,
) -> Iterator[dict]:
    sweep = config["sweep"]
    deltas = [int(x) for x in sweep["requested_age_delta_years"]]
    weights = [float(x) for x in sweep["id_weight"]]
    starts = [int(x) for x in sweep["start_step"]]
    seeds = (
        [int(x) for x in seeds_override]
        if seeds_override is not None
        else [int(x) for x in sweep["seeds"]]
    )

    for row in rows:
        sample_id = row["sample_id"]
        if sample_id_filter and sample_id != sample_id_filter:
            continue
        source_age = int(float(row["source_age"]))
        for delta in deltas:
            target_age = source_age + delta
            for seed in seeds:
                yield {
                    "run_id": run_id(sample_id, delta, "no_pulid", None, None, seed),
                    "sample_id": sample_id,
                    "source_age": source_age,
                    "target_age": target_age,
                    "requested_age_delta": delta,
                    "seed": seed,
                    "treatment": "no_pulid",
                    "id_weight": None,
                    "start_step": None,
                }
                for weight in weights:
                    for start in starts:
                        yield {
                            "run_id": run_id(
                                sample_id, delta, "pulid", weight, start, seed
                            ),
                            "sample_id": sample_id,
                            "source_age": source_age,
                            "target_age": target_age,
                            "requested_age_delta": delta,
                            "seed": seed,
                            "treatment": "pulid",
                            "id_weight": weight,
                            "start_step": start,
                        }


def read_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        return []
    rows: List[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSONL {path}:{line_no}: {e}") from e
    return rows


def append_jsonl(path: Path, row: Mapping) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, data: Mapping) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(dict(data), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)
