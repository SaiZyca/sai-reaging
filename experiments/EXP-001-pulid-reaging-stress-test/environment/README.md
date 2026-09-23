# EXP-001 Environment Strategy

EXP-001 uses **isolated environments** rather than one monolithic environment.

The primary execution platform for this experiment is **Windows 10/11 x64 with PowerShell and Python 3.10**.

This is intentional:

- PuLID pins PyTorch 2.0.1.
- AdaFace's official requirements constrain PyTorch to <=1.13.1.
- MiVOLO brings its own timm / ultralytics dependency set.
- Metric aggregation does not need CUDA or model dependencies.

Keeping the stages isolated prevents evaluator installation from changing the
generation baseline.

## Environment roles

### 1. generation

Input:
- dataset manifest
- source images
- FLUX.1-dev
- PuLID-FLUX-v0.9.1

Produces:
- outputs/raw/*.png
- outputs/raw_manifest.jsonl

Input specification:
- generation.requirements.in

### 2. identity

Input:
- raw images
- raw manifest
- AdaFace IR-101 WebFace12M checkpoint

Produces:
- outputs/identity_metrics.jsonl

Input specification:
- identity.requirements.in

### 3. age

Input:
- raw images
- raw manifest
- MiVOLO face-only checkpoint
- MiVOLO YOLO face/person detector checkpoint

Produces:
- outputs/age_metrics.jsonl

Input specification:
- age.requirements.in

### 4. analysis

Input:
- raw manifest
- identity metrics
- age metrics

Produces:
- outputs/metrics.parquet
- outputs/pareto_summary.csv
- outputs/summary.json

Input specification:
- analysis.requirements.in

## Locking rule

The *.requirements.in files are implementation inputs, **not final locks**.
Before EXP-001 can move to EXECUTABLE, create each environment on the actual
execution machine, verify imports / CUDA behavior, then preserve:

    generation.lock.txt
    identity.lock.txt
    age.lock.txt
    analysis.lock.txt

Each lock must be the resolved environment actually used for the smoke test.
Do not promote the experiment to EXECUTABLE based only on these input specs.

A simple capture after successful installation is:

    python -m pip freeze --all > <role>.lock.txt
    python -m pip check

Also record:

    python --version
    python -c "import torch; print(torch.__version__); print(torch.version.cuda)"
    nvidia-smi

## Third-party repositories

Run:

    bash experiments/EXP-001-pulid-reaging-stress-test/scripts/bootstrap_third_party.sh

This clones the exact revisions recorded in repositories.lock.yaml into
third_party/. The cloned repositories are local execution dependencies and
must not be committed into the sai-reaging repository.


## Windows setup

From the repository root in PowerShell:

    Set-ExecutionPolicy -Scope Process Bypass
    .\experiments\EXP-001-pulid-reaging-stress-test\scripts\bootstrap_third_party.ps1
    .\experiments\EXP-001-pulid-reaging-stress-test\scripts\setup_windows_envs.ps1

The setup script creates:

    .venv-exp001-generation
    .venv-exp001-identity
    .venv-exp001-age
    .venv-exp001-analysis

The Windows setup intentionally uses historical PyTorch CUDA wheels compatible
with the pinned evaluator/generation stacks:

- generation / age: PyTorch 2.0.1 + torchvision 0.15.2 + cu118
- identity: PyTorch 1.13.1 + torchvision 0.14.1 + cu117

Before promotion to EXECUTABLE, capture the observed Windows environment:

    .\experiments\EXP-001-pulid-reaging-stress-test\scripts\capture_windows_environment.ps1
