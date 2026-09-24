# Local Datasets

This directory defines the canonical **local-only** dataset layout for the
Sai Re-Aging research repository.

## Policy

Raw datasets and per-subject/private annotations stored under this directory
must not be committed to Git.

The repository tracks only this README so that execution paths can be
standardized across machines while licensed/restricted dataset bytes remain
local.

## EXP-001

Canonical local AgeDB path:

```text
_Datasets/AgeDB/
```

AgeDB is used only under its official access/license terms. EXP-001 keeps:

- raw AgeDB files under `_Datasets/AgeDB/` — local only;
- private candidate/review/manifest artifacts under `data/private/EXP-001/` — local only;
- only the license-safe `dataset_manifest.lock.yaml` in Git.

PowerShell:

```powershell
$AgeDBRoot = (Resolve-Path .\_Datasets\AgeDB).Path
```
