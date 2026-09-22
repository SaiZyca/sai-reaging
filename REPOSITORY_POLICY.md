# Repository Policy

## Canonical branch

`main` represents the current auditable repository state.

## State ownership

Avoid creating multiple competing sources of truth.

- **Re-Aging_Research_Map.md** owns high-level technical conclusions, candidate
  lifecycle, architecture direction, priorities, and open problems.
- **Re-Aging_Research_Workflow.md** owns the research operating process.
- **Experiment `experiment.yaml`** owns detailed execution/readiness state for
  that experiment; the Research Map may summarize it.
- **Deep Analysis metadata** owns artifact identity and provenance, not the
  candidate's current technical status.
- **GitHub Issues / Projects** are operational indexes of work. They should not
  silently override the Research Map or an experiment's detailed record.

When a durable conclusion changes, update the canonical source rather than
copying the same mutable state into multiple files.

## Terminology boundary

The project uses two different kinds of branch:

- **Chat Branch** — a temporary exploratory fork in ChatGPT, as defined by the
  Research Workflow.
- **Git Task Branch** — a repository branch used to implement one formal task.

They are not equivalent and do not need a one-to-one mapping.

## Identifier namespaces

Keep research identifiers separate from GitHub object numbers:

- `DA-004` — durable Deep Analysis artifact ID
- `EXP-001` — durable Experiment artifact ID
- `#12` — GitHub Issue / PR number

GitHub numbers must not replace research artifact IDs. Chat names may use the
same research sequence where that improves continuity, but GitHub issue numbers
remain independent.

## Git branch convention

- `research/<task>`
- `experiment/<task>`
- `impl/<task>`
- `architecture/<task>`
- `infra/<task>`

Avoid a long-lived `develop` branch.

## Pull requests

Use pull requests as research change records, including for solo development.

Preferred merge strategy: **squash merge**.

## Research artifacts

GitHub materializes the existing research lifecycle:

- ChatGPT Research Chat = working context
- GitHub Issue = formal work unit
- Git Task Branch = repository execution context
- Research / Experiment artifact = durable evidence
- Pull Request = change record
- Research Map = canonical high-level technical state
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

Keep **Research State** and **Experiment State** separate. Project fields are an
operational index; if they disagree with a canonical research artifact, the
canonical artifact wins and the Project should be corrected.

## Wiki / Discussions

Treat both as optional, non-canonical layers. Canonical technical decisions,
reports, experiments, Research Map, and Workflow remain versioned in this
repository.
