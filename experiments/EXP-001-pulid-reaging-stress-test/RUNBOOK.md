# EXP-001 — Windows EXECUTABLE Gate Runbook

Primary platform: **Windows 10/11 x64 + PowerShell + Python 3.10 + NVIDIA GPU**

Do not change EXP-001 to `EXECUTABLE` until the local smoke test and
reproducibility records actually exist.

## 0. PowerShell session

Open PowerShell in the sai-reaging repository root.

Allow project scripts for the current PowerShell process only:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

Confirm prerequisites:

```powershell
git --version
py -3.10 --version
nvidia-smi
```

## 1. Prepare pinned third-party repositories

```powershell
.\experiments\EXP-001-pulid-reaging-stress-test\scripts\bootstrap_third_party.ps1
```

Expected local working copies:

```text
third_party\PuLID
third_party\AdaFace
third_party\MiVOLO
```

The PowerShell bootstrap checks out the exact revisions in
`repositories.lock.yaml` and applies only the two recorded PuLID
reproducibility edits. On Windows these edits are applied through exact,
marker-verified text replacement rather than `git apply`, avoiding
line-ending / patch-parser differences. The committed patch file remains the
audit diff for the same semantic change. These local working copies are
ignored by Git.

If a previous interrupted bootstrap left modified third-party files, run:

```powershell
.\experiments\EXP-001-pulid-reaging-stress-test\scripts\bootstrap_third_party.ps1 -ForceReset
```

## 2. Create isolated Windows environments

```powershell
.\experiments\EXP-001-pulid-reaging-stress-test\scripts\setup_windows_envs.ps1
```

This creates:

```text
.venv-exp001-generation
.venv-exp001-identity
.venv-exp001-age
.venv-exp001-analysis
```

The environments remain isolated to prevent transitive dependency drift.
On the observed RTX 5080 / Blackwell sm_120 machine, all three CUDA stages use
PyTorch 2.7.1 + torchvision 0.22.1 + CUDA 12.8 wheels. This replaces the
historical upstream Torch versions only at the runtime layer; model
architectures and checkpoints remain unchanged.

## 3. Verify and capture Windows environments

Run the import / CUDA verification:

```powershell
.\experiments\EXP-001-pulid-reaging-stress-test\scripts\verify_windows_envs.ps1
```

This verifies:

- CUDA is available
- the installed PyTorch binary explicitly contains sm_120 / compute_120 support
- a real CUDA tensor kernel executes and synchronizes
- generation: PuLID core imports
- identity: AdaFace IR-101 construction
- age: MiVOLO core imports
- analysis: NumPy / pandas / pyarrow imports

If it passes, capture the resolved environment locks and observed machine state:

```powershell
.\experiments\EXP-001-pulid-reaging-stress-test\scripts\capture_windows_environment.ps1
```

The four resolved lock files are written to the canonical experiment
`environment\*.lock.txt` paths. Observed Windows / GPU / Python / Torch
information is written under `environment\observed\`.

## 4. Acquire AgeDB

Use the official AgeDB page:

```text
https://ibug.doc.ic.ac.uk/resources/agedb/
```

AgeDB is restricted to non-commercial research use and its annotations must
not be redistributed. Keep the dataset outside Git or under an ignored local
directory.

The official page provides the database download and instructs researchers to
request the zip password from the listed iBUG contact.

## 5. Materialize the private 8-source manifest

Create:

```text
data\private\EXP-001\dataset_manifest.csv
```

Start from:

```text
experiments\EXP-001-pulid-reaging-stress-test\dataset_manifest.template.csv
```

Selection contract:

- exactly 8 distinct identities
- source age 48–52
- one source image per identity
- 4 M / 4 F using dataset-provided labels only
- |yaw| <= 20 degrees
- no heavy face occlusion
- no extreme expression
- sufficient face resolution for identity evaluation

Do not commit the private CSV.

Validate it with the analysis environment:

```powershell
& .\.venv-exp001-analysis\Scripts\python.exe .\experiments\EXP-001-pulid-reaging-stress-test\scripts\validate_manifest.py --manifest .\data\private\EXP-001\dataset_manifest.csv --dataset-root "<AGEDB_ROOT>"
```

Create the license-safe repository lock:

```powershell
& .\.venv-exp001-analysis\Scripts\python.exe .\experiments\EXP-001-pulid-reaging-stress-test\scripts\lock_private_manifest.py --manifest .\data\private\EXP-001\dataset_manifest.csv --dataset-root "<AGEDB_ROOT>" --output .\experiments\EXP-001-pulid-reaging-stress-test\dataset_manifest.lock.yaml
```

The generated lock contains no per-subject AgeDB annotations and may be
committed.

## 6. Checkpoint Gate — access and automatic materialization

The checkpoint gate uses an ignored local root:

```text
checkpoints\EXP-001\
```

First open the gated FLUX page and the three official Google Drive evaluator
checkpoint pages:

```powershell
.\experiments\EXP-001-pulid-reaging-stress-test\scripts\open_checkpoint_access_pages.ps1
```

For FLUX.1-dev:

1. Sign in to Hugging Face using the account intended for this experiment.
2. Accept the `black-forest-labs/FLUX.1-dev` access conditions.
3. Authenticate the generation environment without putting a token in the
   command line:

```powershell
& .\.venv-exp001-generation\Scripts\huggingface-cli.exe login
```

Confirm the authenticated account:

```powershell
& .\.venv-exp001-generation\Scripts\python.exe -c "from huggingface_hub import whoami; print(whoami()['name'])"
```

Then materialize all Hugging Face / GitHub-hosted assets:

```powershell
& .\.venv-exp001-generation\Scripts\python.exe .\experiments\EXP-001-pulid-reaging-stress-test\scripts\materialize_checkpoint_assets.py --asset-root .\checkpoints\EXP-001
```

The script resolves the current repository SHA **before** each Hugging Face
download and downloads at that exact revision. It automatically materializes:

- PuLID-FLUX-v0.9.1
- FLUX.1-dev
- FLUX autoencoder
- `xlabs-ai/xflux_text_encoders` T5 snapshot
- `openai/clip-vit-large-patch14` CLIP snapshot
- EVA02-CLIP-L-14-336 visual identity checkpoint
- AntelopeV2 at the pinned revision
- FaceXLib RetinaFace
- FaceXLib BiSeNet
- FaceXLib ParseNet

A local, ignored record is written to:

```text
checkpoints\EXP-001\checkpoint_manifest.local.yaml
```

Do not commit this local manifest because it contains absolute local paths.

The expected PuLID-FLUX-v0.9.1 SHA256 is:

```text
92c41c3af322b02e58e1b32842e4601e08c8f16ec1fe80089dbe957df510f51d
```

AntelopeV2 `glintr100.onnx` is also verified against the canonical hash
recorded in `experiment.yaml`.

FLUX.1-dev is gated and uses the FLUX.1-dev non-commercial license. Phase A is
therefore a research experiment; success does not establish commercial
production clearance.

## 7. Checkpoint Gate — manual evaluator assets and verification

Download the three evaluator files from the official pages opened in Step 6
and save them with these exact local names:

```text
checkpoints\EXP-001\evaluators\adaface_ir101_webface12m.ckpt
checkpoints\EXP-001\evaluators\mivolo_face_only_imdb_cleaned_age_gender.pth.tar
checkpoints\EXP-001\evaluators\yolov8x_person_face.pt
```

Official sources:

```text
AdaFace R100 WebFace12M
Google Drive id: 1dswnavflETcnAuplZj1IOKKP0eM8ITgT

MiVOLO VOLO-D1 face-only age+gender / IMDB-cleaned
Google Drive id: 1NlsNEVijX2tjMe8LBb1rI56WB_ADVHeP

MiVOLO face/person detector
Google Drive id: 1CGNCkZQNj5WkP3rLpENWAOgrBQkUWRdw
```

Do not rename arbitrary checkpoints into these filenames. The file must come
from the corresponding upstream link above.

After all automatic and manual assets are present, run:

```powershell
& .\.venv-exp001-generation\Scripts\python.exe .\experiments\EXP-001-pulid-reaging-stress-test\scripts\verify_checkpoint_assets.py --asset-root .\checkpoints\EXP-001
```

A successful verification writes the Git-safe lock:

```text
experiments\EXP-001-pulid-reaging-stress-test\checkpoint_manifest.lock.yaml
```

The lock contains:

- exact Hugging Face repository revisions
- SHA256 + size for direct checkpoint files
- aggregate tree digests for T5 / CLIP local snapshots
- evaluator checkpoint hashes
- FaceXLib / EVA / Antelope auxiliary hashes

The actual checkpoint bytes remain under ignored `checkpoints/EXP-001/` and
must never be committed.

Before using the assets for generation, rerun the third-party bootstrap after
pulling the checkpoint-gate implementation:

```powershell
.\experiments\EXP-001-pulid-reaging-stress-test\scripts\bootstrap_third_party.ps1
```

This applies the reproducibility-only local-asset instrumentation so PuLID uses
the materialized EVA-CLIP / FaceXLib / Antelope assets rather than performing
implicit first-run downloads.

## 8. One-source generation smoke test

Pick one `sample_id` from the private manifest.

Run with the generation environment:

```powershell
& .\.venv-exp001-generation\Scripts\python.exe .\experiments\EXP-001-pulid-reaging-stress-test\scripts\run_phase_a.py --config .\experiments\EXP-001-pulid-reaging-stress-test\configs\phase_a.yaml --manifest .\data\private\EXP-001\dataset_manifest.csv --dataset-root "<AGEDB_ROOT>" --pulid-repo .\third_party\PuLID --pulid-checkpoint .\checkpoints\EXP-001\generation\pulid_flux_v0.9.1.safetensors --flux-checkpoint .\checkpoints\EXP-001\generation\flux1-dev.safetensors --ae-checkpoint .\checkpoints\EXP-001\generation\ae.safetensors --t5-snapshot .\checkpoints\EXP-001\text_encoders\xflux_text_encoders --clip-snapshot .\checkpoints\EXP-001\text_encoders\openai_clip_vit_large_patch14 --eva-clip-checkpoint .\checkpoints\EXP-001\pulid_aux\eva_clip\EVA02_CLIP_L_336_psz14_s6B.pt --facexlib-weights .\checkpoints\EXP-001\pulid_aux\facexlib --antelope-root .\checkpoints\EXP-001\pulid_aux\antelope --output-dir .\experiments\EXP-001-pulid-reaging-stress-test\outputs\raw --sample-id "<SAMPLE_ID>" --age-delta 30 --id-weight 1.0 --start-step 4 --seed 17
```

This produces the matched no-PuLID baseline and selected PuLID condition.

Verify:

- two generated images exist
- `outputs\raw_manifest.jsonl` contains both matching run IDs
- recorded seed is 17
- source / output hashes are present
- FLUX / AE / PuLID hashes are present

## 9. Identity smoke evaluation

```powershell
& .\.venv-exp001-identity\Scripts\python.exe .\experiments\EXP-001-pulid-reaging-stress-test\scripts\evaluate_identity_adaface.py --adaface-repo .\third_party\AdaFace --checkpoint "<ADAFACE_CHECKPOINT>" --checkpoint-sha256 "<ADAFACE_SHA256>" --manifest .\data\private\EXP-001\dataset_manifest.csv --dataset-root "<AGEDB_ROOT>" --raw-manifest .\experiments\EXP-001-pulid-reaging-stress-test\outputs\raw_manifest.jsonl --raw-dir .\experiments\EXP-001-pulid-reaging-stress-test\outputs\raw --output .\experiments\EXP-001-pulid-reaging-stress-test\outputs\identity_metrics.jsonl
```

Both smoke rows should report `identity_status=ok`.

## 10. Age smoke evaluation

```powershell
& .\.venv-exp001-age\Scripts\python.exe .\experiments\EXP-001-pulid-reaging-stress-test\scripts\evaluate_age_mivolo.py --mivolo-repo .\third_party\MiVOLO --checkpoint "<MIVOLO_FACE_ONLY_CHECKPOINT>" --checkpoint-sha256 "<MIVOLO_SHA256>" --detector-weights "<MIVOLO_DETECTOR_CHECKPOINT>" --detector-sha256 "<DETECTOR_SHA256>" --manifest .\data\private\EXP-001\dataset_manifest.csv --dataset-root "<AGEDB_ROOT>" --raw-manifest .\experiments\EXP-001-pulid-reaging-stress-test\outputs\raw_manifest.jsonl --raw-dir .\experiments\EXP-001-pulid-reaging-stress-test\outputs\raw --output .\experiments\EXP-001-pulid-reaging-stress-test\outputs\age_metrics.jsonl
```

Both smoke rows should report `age_status=ok`.

## 11. Metric aggregation smoke test

```powershell
& .\.venv-exp001-analysis\Scripts\python.exe .\experiments\EXP-001-pulid-reaging-stress-test\scripts\evaluate.py --raw-manifest .\experiments\EXP-001-pulid-reaging-stress-test\outputs\raw_manifest.jsonl --identity-jsonl .\experiments\EXP-001-pulid-reaging-stress-test\outputs\identity_metrics.jsonl --age-jsonl .\experiments\EXP-001-pulid-reaging-stress-test\outputs\age_metrics.jsonl --output .\experiments\EXP-001-pulid-reaging-stress-test\outputs\metrics.parquet --summary-output .\experiments\EXP-001-pulid-reaging-stress-test\outputs\summary.json --pareto-output .\experiments\EXP-001-pulid-reaging-stress-test\outputs\pareto_summary.csv
```

Confirm that the PuLID row is paired with its no-PuLID baseline and
`identity_gain_vs_baseline` is populated.

## 12. Re-capture Windows machine state after smoke test

```powershell
.\experiments\EXP-001-pulid-reaging-stress-test\scripts\capture_windows_environment.ps1
```

This records:

- Windows edition / version / architecture
- `nvidia-smi`
- Python versions
- PyTorch versions
- CUDA runtime reported by PyTorch
- GPU name
- `pip freeze --all` for all four environments

Review the generated files before committing any reproducibility record.

## 13. Promotion gate

Only after Steps 1–11 succeed:

- update `experiment.yaml`
  - local asset SHA256 values
  - text-encoder revisions
  - environment lock paths
  - observed Windows / GPU hardware
  - exact sai-reaging commit
  - `smoke_test_passed: true`
  - `state: EXECUTABLE`
- update Issue #3
- change GitHub Project `Experiment State` to `EXECUTABLE`
- merge through task branch → PR → squash merge

`EXECUTABLE` means the experiment can actually be launched. It does not mean
the experiment has already been executed or validated.
