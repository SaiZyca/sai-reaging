#!/usr/bin/env python3
"""Materialize reproducibility-critical EXP-001 checkpoint assets.

HF/GitHub-hosted assets are downloaded automatically at exact resolved
revisions. Google Drive evaluator checkpoints remain manual because they are
served through interactive Drive links in the upstream repositories.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import urllib.request
from pathlib import Path

import yaml
from huggingface_hub import HfApi, get_token, hf_hub_download, snapshot_download


PULID_SHA256 = "92c41c3af322b02e58e1b32842e4601e08c8f16ec1fe80089dbe957df510f51d"
ANTELOPE_REVISION = "ba0c3e10f4548361eb9a63265d87ce1140ab5a05"
ANTELOPE_GLINTR_SHA256 = "4ab1d6435d639628a6f3e5008dd4f929edf4c4124b1a7169e1048f9fef534cdf"

FACEXLIB_FILES = {
    "detection_Resnet50_Final.pth": (
        "https://github.com/xinntao/facexlib/releases/download/v0.1.0/"
        "detection_Resnet50_Final.pth"
    ),
    "parsing_bisenet.pth": (
        "https://github.com/xinntao/facexlib/releases/download/v0.2.0/"
        "parsing_bisenet.pth"
    ),
    "parsing_parsenet.pth": (
        "https://github.com/xinntao/facexlib/releases/download/v0.2.2/"
        "parsing_parsenet.pth"
    ),
}

MANUAL_ASSETS = {
    "adaface": {
        "filename": "adaface_ir101_webface12m.ckpt",
        "google_drive_id": "1dswnavflETcnAuplZj1IOKKP0eM8ITgT",
        "source_repo": "mk-minchul/AdaFace",
    },
    "mivolo_face_only": {
        "filename": "mivolo_face_only_imdb_cleaned_age_gender.pth.tar",
        "google_drive_id": "1NlsNEVijX2tjMe8LBb1rI56WB_ADVHeP",
        "source_repo": "WildChlamydia/MiVOLO",
    },
    "mivolo_detector": {
        "filename": "yolov8x_person_face.pt",
        "google_drive_id": "1CGNCkZQNj5WkP3rLpENWAOgrBQkUWRdw",
        "source_repo": "WildChlamydia/MiVOLO",
    },
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--asset-root", type=Path, default=Path("checkpoints/EXP-001"))
    return p.parse_args()


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def download_url(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_size > 0:
        print(f"reuse {dst}")
        return
    tmp = dst.with_suffix(dst.suffix + ".part")
    print(f"download {url} -> {dst}")
    urllib.request.urlretrieve(url, tmp)
    tmp.replace(dst)


def model_revision(api: HfApi, repo_id: str, token: str | None = None) -> str:
    info = api.model_info(repo_id=repo_id, token=token)
    if not info.sha:
        raise RuntimeError(f"Hugging Face did not return a revision for {repo_id}")
    return info.sha


def main() -> None:
    args = parse_args()
    root = args.asset_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    api = HfApi()
    token = get_token()

    manifest = {
        "schema_version": "0.1",
        "experiment_id": "EXP-001",
        "asset_root": str(root),
        "huggingface": {},
        "facexlib": {},
        "manual_google_drive": MANUAL_ASSETS,
    }

    # PuLID-FLUX v0.9.1
    pulid_repo = "guozinan/PuLID"
    pulid_rev = model_revision(api, pulid_repo)
    pulid_dir = root / "generation"
    pulid_path = Path(
        hf_hub_download(
            repo_id=pulid_repo,
            filename="pulid_flux_v0.9.1.safetensors",
            revision=pulid_rev,
            local_dir=pulid_dir,
        )
    )
    actual_pulid_sha = sha256_file(pulid_path)
    if actual_pulid_sha != PULID_SHA256:
        raise RuntimeError(
            f"PuLID checkpoint SHA mismatch: expected {PULID_SHA256}, got {actual_pulid_sha}"
        )
    manifest["huggingface"]["pulid"] = {
        "repo_id": pulid_repo,
        "revision": pulid_rev,
        "path": str(pulid_path),
        "sha256": actual_pulid_sha,
    }

    # FLUX.1-dev gated assets.
    flux_repo = "black-forest-labs/FLUX.1-dev"
    if not token:
        raise RuntimeError(
            "No Hugging Face token is configured. Accept the FLUX.1-dev terms "
            "in the browser, then run the generation environment's "
            "huggingface-cli login before rerunning this script."
        )
    flux_rev = model_revision(api, flux_repo, token=token)
    for key, filename in [
        ("flux", "flux1-dev.safetensors"),
        ("ae", "ae.safetensors"),
    ]:
        try:
            path = Path(
                hf_hub_download(
                    repo_id=flux_repo,
                    filename=filename,
                    revision=flux_rev,
                    local_dir=pulid_dir,
                    token=token,
                )
            )
        except Exception as e:
            raise RuntimeError(
                "Unable to download gated FLUX.1-dev assets. Confirm that the "
                "Hugging Face account associated with your token has accepted "
                "the black-forest-labs/FLUX.1-dev access terms."
            ) from e
        manifest["huggingface"][key] = {
            "repo_id": flux_repo,
            "revision": flux_rev,
            "path": str(path),
            "sha256": sha256_file(path),
        }

    # T5 text encoder repo used by PuLID's FLUX stack.
    t5_repo = "xlabs-ai/xflux_text_encoders"
    t5_rev = model_revision(api, t5_repo, token=token)
    t5_dir = root / "text_encoders" / "xflux_text_encoders"
    snapshot_download(
        repo_id=t5_repo,
        revision=t5_rev,
        local_dir=t5_dir,
        token=token,
    )
    manifest["huggingface"]["t5"] = {
        "repo_id": t5_repo,
        "revision": t5_rev,
        "path": str(t5_dir),
    }

    # CLIP text encoder. Skip alternate framework / duplicate PyTorch weights.
    clip_repo = "openai/clip-vit-large-patch14"
    clip_rev = model_revision(api, clip_repo, token=token)
    clip_dir = root / "text_encoders" / "openai_clip_vit_large_patch14"
    snapshot_download(
        repo_id=clip_repo,
        revision=clip_rev,
        local_dir=clip_dir,
        token=token,
        ignore_patterns=["*.msgpack", "*.h5", "pytorch_model.bin"],
    )
    manifest["huggingface"]["clip"] = {
        "repo_id": clip_repo,
        "revision": clip_rev,
        "path": str(clip_dir),
    }

    # EVA-CLIP visual identity backbone.
    eva_repo = "QuanSun/EVA-CLIP"
    eva_rev = model_revision(api, eva_repo, token=token)
    eva_dir = root / "pulid_aux" / "eva_clip"
    eva_path = Path(
        hf_hub_download(
            repo_id=eva_repo,
            filename="EVA02_CLIP_L_336_psz14_s6B.pt",
            revision=eva_rev,
            local_dir=eva_dir,
            token=token,
        )
    )
    manifest["huggingface"]["eva_clip"] = {
        "repo_id": eva_repo,
        "revision": eva_rev,
        "path": str(eva_path),
        "sha256": sha256_file(eva_path),
    }

    # AntelopeV2 exact pinned revision.
    antelope_root = root / "pulid_aux" / "antelope"
    antelope_dir = antelope_root / "models" / "antelopev2"
    snapshot_download(
        repo_id="DIAMONIK7777/antelopev2",
        revision=ANTELOPE_REVISION,
        local_dir=antelope_dir,
        token=token,
    )
    glintr = antelope_dir / "glintr100.onnx"
    glintr_sha = sha256_file(glintr)
    if glintr_sha != ANTELOPE_GLINTR_SHA256:
        raise RuntimeError(
            f"Antelope glintr100 SHA mismatch: expected {ANTELOPE_GLINTR_SHA256}, got {glintr_sha}"
        )
    manifest["huggingface"]["antelopev2"] = {
        "repo_id": "DIAMONIK7777/antelopev2",
        "revision": ANTELOPE_REVISION,
        "root": str(antelope_root),
        "key_file": str(glintr),
        "key_file_sha256": glintr_sha,
    }

    # FaceXLib detector + BiSeNet parsing weights used by PuLID preprocessing.
    facex_dir = root / "pulid_aux" / "facexlib"
    for filename, url in FACEXLIB_FILES.items():
        path = facex_dir / filename
        download_url(url, path)
        manifest["facexlib"][filename] = {
            "url": url,
            "path": str(path),
            "sha256": sha256_file(path),
        }

    # Create evaluator directory and make manual destinations explicit.
    eval_dir = root / "evaluators"
    eval_dir.mkdir(parents=True, exist_ok=True)
    for item in MANUAL_ASSETS.values():
        item["target_path"] = str(eval_dir / item["filename"])

    local_manifest = root / "checkpoint_manifest.local.yaml"
    local_manifest.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    print()
    print("HF/GitHub checkpoint materialization complete.")
    print(f"Local manifest: {local_manifest}")
    print()
    print("Manual Google Drive assets still required:")
    for name, item in MANUAL_ASSETS.items():
        print(
            f"- {name}: save as {eval_dir / item['filename']} "
            f"(Drive id {item['google_drive_id']})"
        )


if __name__ == "__main__":
    main()
