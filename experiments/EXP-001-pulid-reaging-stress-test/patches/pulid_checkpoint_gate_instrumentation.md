# EXP-001 — PuLID Checkpoint-Gate Instrumentation Record

**Upstream repository:** `ToTheBeginning/PuLID`  
**Upstream commit:** `a66a6a1901729897fa1dc11d10397943caf15470`  
**Scope:** reproducibility / local-asset routing only  
**Architecture change:** none

This record documents the semantic edits applied by
`scripts/bootstrap_third_party.ps1` on Windows. The upstream working copy is
reset to the pinned commit before these edits are applied.

## 1. PuLID checkpoint

Original behavior downloads `pulid_flux_<version>.safetensors` before checking
whether a local `pretrain_path` was supplied.

EXP-001 behavior:

- if `pretrain_path` is supplied, load it directly;
- otherwise preserve upstream Hugging Face download behavior.

Purpose: prevent an unnecessary moving-network dependency when the experiment
already supplies a hashed local PuLID checkpoint.

## 2. AntelopeV2

Original behavior downloads `DIAMONIK7777/antelopev2` into
`models/antelopev2` without a revision.

EXP-001 behavior:

- pin revision to
  `ba0c3e10f4548361eb9a63265d87ce1140ab5a05`;
- route the asset root through `EXP001_ANTELOPE_ROOT`;
- when `EXP001_OFFLINE_ASSETS` is set, fail if the materialized
  `glintr100.onnx` is absent instead of downloading implicitly.

Purpose: make PuLID identity conditioning depend on an explicit local,
revision-pinned AntelopeV2 snapshot.

## 3. EVA-CLIP

Original behavior passes the pretrained tag `eva_clip` to
`create_model_and_transforms`, which triggers the EVA-CLIP pretrained download
path.

EXP-001 behavior:

- when `EXP001_EVA_CLIP_PATH` is set, pass that local checkpoint path instead;
- otherwise preserve the upstream pretrained tag.

Purpose: use the hashed local `EVA02_CLIP_L_336_psz14_s6B.pt` checkpoint.

## 4. FaceXLib detector and parsers

Original behavior lets FaceXLib download pretrained detector / parsing weights
into its package cache.

EXP-001 behavior:

- pass `EXP001_FACEXLIB_WEIGHTS` as `model_rootpath` to
  `FaceRestoreHelper`;
- pass the same root to the replacement BiSeNet parser.

Materialized files:

- `detection_Resnet50_Final.pth`
- `parsing_parsenet.pth`
- `parsing_bisenet.pth`

Purpose: eliminate implicit first-run downloads from PuLID preprocessing.

## 5. T5 / CLIP text encoders

These are not patched in the PuLID source file. The project-side
`run_phase_a.py` replaces `app_flux.load_t5` and `app_flux.load_clip`
with equivalent loaders that point to exact local Hugging Face snapshots.

Purpose: prevent the upstream repo IDs from resolving a moving `main` revision
at experiment runtime.

## Invariance boundary

The instrumentation does **not** change:

- PuLID IDFormer or cross-attention weights;
- identity injection locations;
- `id_weight`;
- `start_step`;
- FLUX transformer math;
- sampler / denoise schedule;
- experiment prompt, seed, resolution, or guidance controls.

Any future edit outside this boundary requires a separate implementation /
ablation task rather than being treated as EXP-001 Phase A instrumentation.
