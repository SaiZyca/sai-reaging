# Sai Re-Aging

A long-running research program for building a controllable, identity-preserving, temporally consistent, geometry-aware Re-Aging AI system.

## Canonical research state
- [Re-Aging_Research_Map.md](./Re-Aging_Research_Map.md) — durable technical state
- [Re-Aging_Research_Workflow.md](./Re-Aging_Research_Workflow.md) — research operating model

## Current program state
- Landscape Round 1 — completed
- DA-001 — MyTimeMachine — completed
- DA-002 — TimeMachine — completed
- DA-003 — Aging Multiverse — completed
- DA-004 — PuLID — completed
- EXP-001 — PuLID Re-Aging Stress Test — DESIGNED
- Next experiment state — IMPLEMENTATION-READY

## Research operating model
```text
ChatGPT Research Chat
        ↓
GitHub Issue
        ↓
Research / Experiment Branch
        ↓
Evidence + Code + Config + Results
        ↓
Pull Request / Closeout
        ↓
main
        ↓
Canonical Research State
```

`main` represents the current auditable research state, not automatically a production-ready software release.

## Repository roles
```text
research/       Durable research artifacts and architecture decisions
experiments/    Reproducible experiment bundles
src/            Reusable project-owned implementation
configs/        Shared configuration
scripts/        Utility and execution scripts
tests/          Tests for reusable implementation
references/     Paper / repository / dataset indexes
third_party/    Third-party dependency metadata and patches
data/           Manifests and policy; not raw datasets by default
assets/         Canonical diagrams and selected figures
```

## Licensing
Project-owned repository content is licensed under Apache-2.0 unless explicitly stated otherwise. Third-party code, models, weights, datasets, figures, and other assets retain their upstream licenses and terms.
