# EXP-001 — EXECUTABLE Gate Runbook

This runbook covers the remaining **local / account-authorized** steps that the
GitHub connector cannot perform.

Do not change the experiment state to `EXECUTABLE` until the smoke test and
reproducibility records below actually exist.

## 1. Prepare pinned third-party repositories

From the sai-reaging repository root:

```bash
bash experiments/EXP-001-pulid-reaging-stress-test/scripts/bootstrap_third_party.sh
```

Expected local working copies:

```text
third_party/PuLID
third_party/AdaFace
third_party/MiVOLO
```

The bootstrap script checks out the exact revisions in
`repositories.lock.yaml` and applies only the recorded PuLID
reproducibility patch.

Do not commit these working copies.

## 2. Acquire AgeDB

Official AgeDB terms currently state:

- non-commercial research purposes only
- annotations / derived data may not be redistributed
- database download is provided by iBUG
- the zip password must be requested from the contact listed on the official
  AgeDB page

Official page:

```text
https://ibug.doc.ic.ac.uk/resources/agedb/
```

The official page lists the password-request contact as:

```text
s [dot] moschoglou [at] imperial [dot] ac [dot] uk
```

Keep AgeDB outside Git or under an ignored local data directory.

## 3. Materialize the private 8-source manifest

Create:

```text
data/private/EXP-001/dataset_manifest.csv
```

Start from:

```text
experiments/EXP-001-pulid-reaging-stress-test/dataset_manifest.template.csv
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

Do **not** commit this CSV because it contains AgeDB annotations.

Validate it:

```bash
python experiments/EXP-001-pulid-reaging-stress-test/scripts/validate_manifest.py \
  --manifest data/private/EXP-001/dataset_manifest.csv \
  --dataset-root <AGEDB_ROOT>
```

Then create the license-safe repository lock:

```bash
python experiments/EXP-001-pulid-reaging-stress-test/scripts/lock_private_manifest.py \
  --manifest data/private/EXP-001/dataset_manifest.csv \
  --output experiments/EXP-001-pulid-reaging-stress-test/dataset_manifest.lock.yaml
```

The generated lock contains no per-subject annotations and may be committed.

## 4. Materialize model assets

Create a local asset directory, for example:

```text
checkpoints/EXP-001/
```

Required assets:

### Generation

- PuLID-FLUX-v0.9.1:
  `pulid_flux_v0.9.1.safetensors`
- FLUX.1-dev:
  `flux1-dev.safetensors`
- FLUX AE:
  `ae.safetensors`

PuLID v0.9.1 expected SHA256:

```text
92c41c3af322b02e58e1b32842e4601e08c8f16ec1fe80089dbe957df510f51d
```

FLUX.1-dev is a gated model. Accept its access/license terms using your own
Hugging Face account before downloading it.

### Identity evaluator

AdaFace IR-101 WebFace12M:

```text
adaface_ir101_webface12m.ckpt
Google Drive id: 1dswnavflETcnAuplZj1IOKKP0eM8ITgT
```

### Age evaluator

MiVOLO face-only age+gender checkpoint:

```text
Google Drive id: 1NlsNEVijX2tjMe8LBb1rI56WB_ADVHeP
```

MiVOLO face/person detector:

```text
yolov8x_person_face.pt
Google Drive id: 1CGNCkZQNj5WkP3rLpENWAOgrBQkUWRdw
```

After downloading every asset:

```bash
sha256sum <FILE>
```

Record the resulting hashes in `experiment.yaml` before promotion to
`EXECUTABLE`.

## 5. Record text-encoder snapshots

PuLID's FLUX stack also loads:

```text
xlabs-ai/xflux_text_encoders
openai/clip-vit-large-patch14
```

Record the exact Hugging Face snapshot / commit revisions actually cached and
used by the smoke test. Do not leave them as an implicit moving `main`.

## 6. Create four isolated environments

See:

```text
experiments/EXP-001-pulid-reaging-stress-test/environment/README.md
```

Create four Python 3.10 environments:

```text
exp001-generation
exp001-identity
exp001-age
exp001-analysis
```

Install the corresponding `*.requirements.in` file in each environment.

After each environment works:

```bash
python -m pip check
python -m pip freeze --all > <role>.lock.txt
```

Save the four resolved locks under the experiment `environment/` directory.

## 7. One-source generation smoke test

Pick one `sample_id` from the private manifest.

In the generation environment:

```bash
python experiments/EXP-001-pulid-reaging-stress-test/scripts/run_phase_a.py \
  --config experiments/EXP-001-pulid-reaging-stress-test/configs/phase_a.yaml \
  --manifest data/private/EXP-001/dataset_manifest.csv \
  --dataset-root <AGEDB_ROOT> \
  --pulid-repo third_party/PuLID \
  --pulid-checkpoint <PULID_CHECKPOINT> \
  --flux-checkpoint <FLUX_CHECKPOINT> \
  --ae-checkpoint <AE_CHECKPOINT> \
  --output-dir experiments/EXP-001-pulid-reaging-stress-test/outputs/raw \
  --sample-id <SAMPLE_ID> \
  --age-delta 30 \
  --id-weight 1.0 \
  --start-step 4 \
  --seed 17
```

This intentionally generates the matched no-PuLID baseline plus the selected
PuLID condition.

Verify:

- two generated images exist
- `outputs/raw_manifest.jsonl` contains the two matching run IDs
- recorded seed is 17
- source/output SHA256 values are present
- FLUX / AE / PuLID checkpoint SHA256 values are recorded

## 8. Identity smoke evaluation

In the identity environment:

```bash
python experiments/EXP-001-pulid-reaging-stress-test/scripts/evaluate_identity_adaface.py \
  --adaface-repo third_party/AdaFace \
  --checkpoint <ADAFACE_CHECKPOINT> \
  --checkpoint-sha256 <ADAFACE_SHA256> \
  --manifest data/private/EXP-001/dataset_manifest.csv \
  --dataset-root <AGEDB_ROOT> \
  --raw-manifest experiments/EXP-001-pulid-reaging-stress-test/outputs/raw_manifest.jsonl \
  --raw-dir experiments/EXP-001-pulid-reaging-stress-test/outputs/raw \
  --output experiments/EXP-001-pulid-reaging-stress-test/outputs/identity_metrics.jsonl
```

Both smoke rows should have `identity_status=ok`.

## 9. Age smoke evaluation

In the age environment:

```bash
python experiments/EXP-001-pulid-reaging-stress-test/scripts/evaluate_age_mivolo.py \
  --mivolo-repo third_party/MiVOLO \
  --checkpoint <MIVOLO_FACE_ONLY_CHECKPOINT> \
  --checkpoint-sha256 <MIVOLO_SHA256> \
  --detector-weights <MIVOLO_DETECTOR_CHECKPOINT> \
  --detector-sha256 <DETECTOR_SHA256> \
  --manifest data/private/EXP-001/dataset_manifest.csv \
  --dataset-root <AGEDB_ROOT> \
  --raw-manifest experiments/EXP-001-pulid-reaging-stress-test/outputs/raw_manifest.jsonl \
  --raw-dir experiments/EXP-001-pulid-reaging-stress-test/outputs/raw \
  --output experiments/EXP-001-pulid-reaging-stress-test/outputs/age_metrics.jsonl
```

Both smoke rows should have `age_status=ok`.

## 10. Metric aggregation smoke test

In the analysis environment:

```bash
python experiments/EXP-001-pulid-reaging-stress-test/scripts/evaluate.py \
  --raw-manifest experiments/EXP-001-pulid-reaging-stress-test/outputs/raw_manifest.jsonl \
  --identity-jsonl experiments/EXP-001-pulid-reaging-stress-test/outputs/identity_metrics.jsonl \
  --age-jsonl experiments/EXP-001-pulid-reaging-stress-test/outputs/age_metrics.jsonl \
  --output experiments/EXP-001-pulid-reaging-stress-test/outputs/metrics.parquet \
  --summary-output experiments/EXP-001-pulid-reaging-stress-test/outputs/summary.json \
  --pareto-output experiments/EXP-001-pulid-reaging-stress-test/outputs/pareto_summary.csv
```

Confirm that the PuLID row is paired with its no-PuLID baseline and that
`identity_gain_vs_baseline` is populated.

## 11. Capture observed machine state

Record:

```bash
python --version
nvidia-smi
```

For every CUDA environment also record:

```bash
python -c "import torch; print(torch.__version__); print(torch.version.cuda); print(torch.cuda.get_device_name(0))"
```

## 12. Promotion gate

Only after Steps 1–11 succeed:

- update `experiment.yaml`
  - local asset SHA256 values
  - text-encoder revisions
  - environment lock paths
  - observed hardware
  - exact sai-reaging commit
  - `smoke_test_passed: true`
  - `state: EXECUTABLE`
- update Issue #3 operational summary
- change GitHub Project `Experiment State` to `EXECUTABLE`
- submit via task branch → PR → squash merge

This transition means the experiment can actually be launched. It still does
**not** mean the experiment has been executed or validated.
