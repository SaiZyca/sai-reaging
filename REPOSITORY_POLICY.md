# Repository Policy

## Canonical branch
`main` represents the current auditable research state.

## Branch convention
- `research/<task>`
- `experiment/<task>`
- `impl/<task>`
- `architecture/<task>`
- `infra/<task>`

Avoid a long-lived `develop` branch.

## Pull requests
Use pull requests as research change records, including for solo development. Preferred merge strategy: **squash merge**.

## Research artifacts
GitHub materializes the existing research lifecycle:
- ChatGPT Research Chat = working context
- GitHub Issue = formal work unit
- Branch = task execution context
- Research / Experiment artifact = durable evidence
- Pull Request = change record
- Research Map = canonical technical state
- Workflow = canonical process state

## GitHub Project
Use one top-level Project: **Re-Aging Research Program**.

Recommended custom fields:
- Type
- Domain
- Priority
- Research State
- Experiment State
- Architecture Role
- Stage
- Evidence
- Decision

Keep **Research State** and **Experiment State** separate.

## Wiki / Discussions
Treat both as optional, non-canonical layers. Canonical technical decisions, reports, experiments, Research Map, and Workflow remain versioned in this repository.
