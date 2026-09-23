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

The environments remain isolated because PuLID and AdaFace require different
PyTorch generations.

## 3. Acquire AgeDB

Use the official AgeDB page:

```text
https://ibug.doc.ic.ac.uk/resources/agedb/
```

AgeDB is restricted to non-commercial research use and its annotations must
not be redistributed. Keep the dataset outside Git or under an ignored local
directory.

The official page provides the database download and instructs researchers to
request the zip password from the listed iBUG contact.

## 4. Materialize the private 8-source manifest

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

## 5. Materialize model assets

A convenient ignored local directory is:

```powershell
New-Item -ItemType Directory -Force .\checkpoints\EXP-001
```

Required generation assets:

```text
pulid_flux_v0.9.1.safetensors
flux1-dev.safetensors
ae.safetensors
```

Expected PuLID-FLUX-v0.9.1 SHA256:

```text
92c41c3af322b02e58e1b32842e4601e08c8f16ec1fe80089dbe957df510f51d
```

FLUX.1-dev is gated. Accept its terms using your own Hugging Face account
before downloading the model.

Identity evaluator:

```text
adaface_ir101_webface12m.ckpt
Google Drive id: 1dswnavflETcnAuplZj1IOKKP0eM8ITgT
```

Age evaluator:

```text
MiVOLO face-only age+gender checkpoint
Google Drive id: 1NlsNEVijX2tjMe8LBb1rI56WB_ADVHeP

yolov8x_person_face.pt
Google Drive id: 1CGNCkZQNj5WkP3rLpENWAOgrBQkUWRdw
```

Calculate SHA256 on Windows:

```powershell
(Get-FileHash "<FILE_PATH>" -Algorithm SHA256).Hash.ToLower()
```

Record the hashes in `experiment.yaml` before promotion to
`EXECUTABLE`.

## 6. Record text-encoder snapshots

PuLID's FLUX stack also loads:

```text
xlabs-ai/xflux_text_encoders
openai/clip-vit-large-patch14
```

Record the exact Hugging Face snapshot / commit revisions actually cached and
used by the smoke test. Do not leave these as an implicit moving main revision.

## 7. One-source generation smoke test

Pick one `sample_id` from the private manifest.

Run with the generation environment:

```powershell
& .\.venv-exp001-generation\Scripts\python.exe .\experiments\EXP-001-pulid-reaging-stress-test\scripts\run_phase_a.py --config .\experiments\EXP-001-pulid-reaging-stress-test\configs\phase_a.yaml --manifest .\data\private\EXP-001\dataset_manifest.csv --dataset-root "<AGEDB_ROOT>" --pulid-repo .\third_party\PuLID --pulid-checkpoint "<PULID_CHECKPOINT>" --flux-checkpoint "<FLUX_CHECKPOINT>" --ae-checkpoint "<AE_CHECKPOINT>" --output-dir .\experiments\EXP-001-pulid-reaging-stress-test\outputs\raw --sample-id "<SAMPLE_ID>" --age-delta 30 --id-weight 1.0 --start-step 4 --seed 17
```

This produces the matched no-PuLID baseline and selected PuLID condition.

Verify:

- two generated images exist
- `outputs\raw_manifest.jsonl` contains both matching run IDs
- recorded seed is 17
- source / output hashes are present
- FLUX / AE / PuLID hashes are present

## 8. Identity smoke evaluation

```powershell
& .\.venv-exp001-identity\Scripts\python.exe .\experiments\EXP-001-pulid-reaging-stress-test\scripts\evaluate_identity_adaface.py --adaface-repo .\third_party\AdaFace --checkpoint "<ADAFACE_CHECKPOINT>" --checkpoint-sha256 "<ADAFACE_SHA256>" --manifest .\data\private\EXP-001\dataset_manifest.csv --dataset-root "<AGEDB_ROOT>" --raw-manifest .\experiments\EXP-001-pulid-reaging-stress-test\outputs\raw_manifest.jsonl --raw-dir .\experiments\EXP-001-pulid-reaging-stress-test\outputs\raw --output .\experiments\EXP-001-pulid-reaging-stress-test\outputs\identity_metrics.jsonl
```

Both smoke rows should report `identity_status=ok`.

## 9. Age smoke evaluation

```powershell
& .\.venv-exp001-age\Scripts\python.exe .\experiments\EXP-001-pulid-reaging-stress-test\scripts\evaluate_age_mivolo.py --mivolo-repo .\third_party\MiVOLO --checkpoint "<MIVOLO_FACE_ONLY_CHECKPOINT>" --checkpoint-sha256 "<MIVOLO_SHA256>" --detector-weights "<MIVOLO_DETECTOR_CHECKPOINT>" --detector-sha256 "<DETECTOR_SHA256>" --manifest .\data\private\EXP-001\dataset_manifest.csv --dataset-root "<AGEDB_ROOT>" --raw-manifest .\experiments\EXP-001-pulid-reaging-stress-test\outputs\raw_manifest.jsonl --raw-dir .\experiments\EXP-001-pulid-reaging-stress-test\outputs\raw --output .\experiments\EXP-001-pulid-reaging-stress-test\outputs\age_metrics.jsonl
```

Both smoke rows should report `age_status=ok`.

## 10. Metric aggregation smoke test

```powershell
& .\.venv-exp001-analysis\Scripts\python.exe .\experiments\EXP-001-pulid-reaging-stress-test\scripts\evaluate.py --raw-manifest .\experiments\EXP-001-pulid-reaging-stress-test\outputs\raw_manifest.jsonl --identity-jsonl .\experiments\EXP-001-pulid-reaging-stress-test\outputs\identity_metrics.jsonl --age-jsonl .\experiments\EXP-001-pulid-reaging-stress-test\outputs\age_metrics.jsonl --output .\experiments\EXP-001-pulid-reaging-stress-test\outputs\metrics.parquet --summary-output .\experiments\EXP-001-pulid-reaging-stress-test\outputs\summary.json --pareto-output .\experiments\EXP-001-pulid-reaging-stress-test\outputs\pareto_summary.csv
```

Confirm that the PuLID row is paired with its no-PuLID baseline and
`identity_gain_vs_baseline` is populated.

## 11. Capture Windows machine state

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

## 12. Promotion gate

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
