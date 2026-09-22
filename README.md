# Sai Re-Aging

A long-running research program for building a controllable, identity-preserving,
temporally consistent, geometry-aware Re-Aging AI system.

## Canonical research state

- [Re-Aging_Research_Map.md](./Re-Aging_Research_Map.md) — canonical high-level technical state
- [Re-Aging_Research_Workflow.md](./Re-Aging_Research_Workflow.md) — canonical research operating model

The README is an entry point, not a second Research Map. Current candidate
status, architecture direction, open problems, and research priorities should be
read from `Re-Aging_Research_Map.md`.

## Research operating model

```text
ChatGPT Research Chat
        ↓
GitHub Issue
        ↓
Git Task Branch
        ↓
Evidence + Code + Config + Results
        ↓
Pull Request / Closeout
        ↓
main
        ↓
Canonical Repository State
```

`main` represents the current auditable repository state. It is not automatically
a production-ready software release.

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

Git does not preserve empty directories. Planned paths such as `src/`,
`configs/`, `scripts/`, `tests/`, or `assets/` are introduced when the
first real artifact requires them rather than being filled with placeholder
files.

## Licensing

Project-owned repository content is licensed under Apache-2.0 unless explicitly
stated otherwise. Third-party code, models, weights, datasets, figures, and other
assets retain their upstream licenses and terms.
