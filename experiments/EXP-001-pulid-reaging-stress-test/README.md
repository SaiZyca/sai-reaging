# EXP-001 — PuLID Re-Aging Stress Test

**State:** IMPLEMENTATION-READY  
**Source Research:** DA-004 — PuLID  
**GitHub Issue:** #3

## Objective

Measure the Identity–Age trade-off of **stock PuLID-FLUX-v0.9.1** under
progressively larger Re-Aging transformations and determine whether PuLID
should be promoted, modified with Age-Aware Identity Conditioning, or
downgraded to an architecture reference.

## Phase A boundary

Phase A is inference-only:

- no retraining
- no architecture modification
- stock PuLID-FLUX-v0.9.1 behavior
- project-side batching / reproducibility instrumentation is allowed
- H1 and H2 are directly testable
- H3 is **not** causally testable because stock PuLID does not expose
  biometric-vs-rich-visual identity branches independently

## Fixed upstream baseline

- Repository: `ToTheBeginning/PuLID`
- Commit: `a66a6a1901729897fa1dc11d10397943caf15470`
- PuLID checkpoint: `pulid_flux_v0.9.1.safetensors`
- PuLID checkpoint SHA256:
  `92c41c3af322b02e58e1b32842e4601e08c8f16ec1fe80089dbe957df510f51d`
- Backbone: `black-forest-labs/FLUX.1-dev`
- Precision: bf16
- Primary runtime mode: `--offload`
- FP8: excluded from the primary experiment

## Fixed source cohort

Preferred source dataset: **AgeDB**.

Phase A uses **8 distinct identities aged 48–52**, one image per identity.
This narrow mid-life source band allows symmetric target deltas without
crossing the adult boundary:

```text
requested age delta
-30  -15   0  +15  +30
```

The manifest is deterministic and must contain source file hashes. Raw face
data is not committed to this repository.

## Primary sweep

```text
8 source faces
× 5 age deltas
× 2 seeds
× [1 no-PuLID baseline + (4 id_weight × 3 start_step)]
= 1040 generated images
```

Fixed sweep:

- `id_weight = [0.5, 1.0, 1.5, 2.0]`
- `start_step = [0, 4, 8]`
- seeds `[17, 101]`
- conditional confirmation seed `1009`

The no-PuLID baseline is implemented with `id_image=None`, not
`id_weight=0`.

## Controlled generation configuration

- FLUX name: `flux-dev`
- 20 inference steps
- guidance 4.0
- true CFG 1.0
- 896 × 1152
- T5 max sequence length 128
- fixed photorealistic target-age prompt template
- stock PuLID preprocessing

## Evaluation

Primary identity metric:

- **AdaFace R100 WebFace12M**
- independent from PuLID's AntelopeV2 conditioning representation

Diagnostic identity metric:

- AntelopeV2 / `glintr100`
- intentionally treated as **aligned / non-independent**
- never used as the sole architecture-decision metric

Primary age metric:

- MiVOLO face-only VOLO-D1 age model

Critical guardrail:

> PuLID age suppression is only measured on source/target/seed pairs where the
> matched no-PuLID FLUX baseline moves age in the requested direction and
> achieves at least 50% of the requested age displacement.

This prevents a weak prompt/backbone aging response from being misattributed
to PuLID.

## Decision-oriented outputs

- AdaFace identity similarity
- identity gain vs no-PuLID baseline
- target-age error
- realized age displacement
- age-edit retention vs no-PuLID baseline
- Identity–Age Pareto curve
- evaluator success/failure rate
- predefined Re-Aging failure tags

## IMPLEMENTATION-READY does not mean EXECUTABLE

The experiment is now sufficiently specified for implementation, but it cannot
be launched yet. Before promotion to `EXECUTABLE`, the task must still:

1. implement the batch runner and evaluator wrappers
2. acquire AgeDB and materialize the 8-row manifest
3. materialize and hash all checkpoints / auxiliary assets
4. resolve the dependency lock and save the environment freeze
5. run a one-source smoke test
6. record the exact project commit and observed hardware

The detailed canonical experiment state is in `experiment.yaml`.
