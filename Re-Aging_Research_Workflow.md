# Re-Aging Research Workflow

**Version:** 1.4\
**Project:** Sai_研究_Re-Aging\
**Purpose:** Define how research chats, research state, context
boundaries, experiments, and the `Re-Aging_Research_Map.md` are managed
throughout the project.

------------------------------------------------------------------------

## 1. Core Operating Model

This project is treated as a continuous research program rather than a
collection of isolated conversations.

The working model is:

``` text
Project Instructions
        ↓
Research Chat
        ↓
Evidence Collection
        ↓
Technical Analysis
        ↓
Engineering Conclusion
        ↓
Research State Update
        ↓
Next Research Question
```

The three main information layers have different responsibilities:

-   **Project Instructions** --- define how the AI should research and
    reason.
-   **Research Chat** --- working context for investigation, discussion,
    comparison, and technical reasoning.
-   **Re-Aging_Research_Map.md** --- canonical high-level state of the
    research program.

**Chat = Working Research Context**\
**Research Map = Persistent / Canonical Research State**

Do not rely on chat history or project memory as the only long-term
storage of important research conclusions.

------------------------------------------------------------------------

## 2. Research Chat Scope

Each chat should represent a reasonably bounded research task.

A chat does not need to contain only one question. Multiple questions
should remain in the same chat when they belong to the same technical
investigation.

Examples that should normally remain in the same chat:

-   Paper analysis → Architecture analysis → Loss analysis
-   Paper → Official GitHub → actual implementation differences
-   Model inference → Training pipeline → Dataset requirements
-   Model architecture → Identity mechanism → Age conditioning
-   Repository setup → Training command → VRAM requirements
-   Experiment design → Results → Failure analysis, when these belong to
    the same formal Experiment task

Do not open a new chat simply because the current chat is long.

The primary criterion is **semantic / research-task boundary**, not
message count.

------------------------------------------------------------------------

## 3. Continue / Branch / New Chat Decision

Use three distinct conversation actions:

-   **Continue** --- remain in the current chat when the question is
    part of the same research task.
-   **Branch** --- create a short-lived exploratory fork when a new
    hypothesis directly depends on the current local context.
-   **New Chat** --- create a clean research workspace for a new model,
    domain, substantial research task, or context reset.

Decision rule:

``` text
Same research task?
    → Continue

Directly derived hypothesis that needs current local context?
    → Branch

New substantial task / domain / model, or context is becoming complex?
    → New Chat
```

A Branch is a tactical exploration tool, not the primary long-term
organization mechanism.

### 3.1 Branch Usage Rules

Use a Branch when:

-   a specific finding creates an alternative hypothesis worth testing
-   two or more approaches should be explored from the same established
    assumptions
-   an architectural idea should be explored without disrupting the main
    analysis
-   a side investigation benefits materially from inheriting the exact
    local conversation context

Examples:

``` text
MyTimeMachine Deep Analysis
        ↓
Personalization mechanism discovered
        ↓
Branch: Can this mechanism migrate to FLUX / DiT?
```

or:

``` text
Image Re-Aging → Video extension question
        ├─ Branch A: AnyV2V-style propagation
        ├─ Branch B: Video Diffusion fine-tuning
        └─ Branch C: Optical-flow constraint
```

### 3.2 Branch Depth / Promotion Rule

Branches should normally remain shallow.

Project convention:

``` text
Main Chat
├─ Branch A        ✓
├─ Branch B        ✓
└─ Branch C        ✓

Branch A
└─ Branch A.1      ⚠ normally avoid
      └─ A.1.1     ✗ avoid
```

Default guideline: **do not intentionally build multi-level branch
trees.**

If a Branch becomes a substantial or durable research direction:

``` text
Exploratory Branch
        ↓
Promising / substantial finding
        ↓
Research Closeout
        ↓
Update Research Map if warranted
        ↓
Start a clean New Chat
```

If a Branch itself appears to require another substantial Branch, this
is normally a signal that the topic should be promoted into a New Chat
instead.

Branching does not serve as a context reset. Do not use repeated
branching to solve context degradation.

## 4. New Chat Triggers

The AI should proactively recommend opening a new chat when a meaningful
research boundary has been reached.

Typical triggers include:

### 4.1 Model Boundary

A major model / repository has been sufficiently analyzed and research
is moving to a different major model.

Example:

``` text
Model A Paper + GitHub + Training Analysis
        ↓ complete
Model B Investigation
        ↓
Recommend New Chat
```

Exceptions are allowed when Model B is being examined specifically as a
direct comparison or dependency of Model A.

### 4.2 Domain Boundary

Research moves between substantially different technical domains.

Examples:

-   Image Re-Aging → Video Re-Aging
-   Video Re-Aging → 4D Human Representation
-   Model research → Dataset landscape
-   Dataset research → Evaluation methodology
-   Literature research → Our Architecture design

### 4.3 Implementation Boundary

A literature investigation transitions into a substantial independent
engineering task.

Examples:

-   Paper analysis → reproduction project
-   Landscape research → implementation plan
-   Architecture hypothesis → formal experiment
-   Deep Analysis → executable experiment task
-   Repository analysis → custom fork / modification strategy

### 4.4 Independent Research Branch

A side question becomes large enough to form its own research program.

Example:

``` text
Video Re-Aging
   ↓
Question about temporal consistency
   ↓
Temporal Attention vs Optical Flow vs Feature Propagation
   ↓
Independent research branch
   ↓
Use a short Branch for exploration, then promote to New Chat if substantial
```

------------------------------------------------------------------------

## 5. Context Degradation Triggers

Even when the topic has not completely changed, the AI should recommend
a new chat when context reliability is likely to degrade.

Signals include:

-   Early technical details must repeatedly be re-established.
-   Multiple versions of the same model or repository become difficult
    to distinguish.
-   Several papers, repositories, datasets, and experiments become
    interleaved.
-   References such as "the previous model", "that loss", or "the
    earlier method" become ambiguous.
-   Multiple independent research branches are active simultaneously.
-   Old assumptions conflict with newer findings and the discussion
    becomes difficult to track.
-   The current task depends heavily on distant details that should
    instead become explicit research state.

The AI should not wait for obvious answer degradation before suggesting
a new chat.

When recommending a new chat, explain briefly what the semantic boundary
is.

------------------------------------------------------------------------

## 6. When NOT to Open a New Chat

Continue the current chat when the user is:

-   asking follow-up questions about the same paper
-   inspecting the same repository
-   tracing the same training pipeline
-   investigating losses or modules belonging to the same model
-   comparing paper claims against the implementation
-   designing experiments for the same hypothesis
-   debugging or reproducing the same model

The goal is to preserve useful local context without allowing unrelated
research branches to accumulate indefinitely.

------------------------------------------------------------------------

## 7. Research Map Role

`Re-Aging_Research_Map.md` is the canonical high-level representation of
what the project currently believes is technically important.

It should answer questions such as:

-   What areas of Re-Aging have we investigated?
-   Which methods currently matter?
-   Which technologies are candidate modules?
-   What engineering conclusions have survived deeper analysis?
-   What remains unknown?
-   What architecture direction are we currently considering?

The Research Map is **decision-oriented**, not **note-oriented**.

It should not become a transcript archive or contain complete summaries
of every paper.

------------------------------------------------------------------------

## 8. Research Map Update Triggers

The AI should proactively remind the user to update the Research Map
when research produces a durable conclusion.

### Update is normally warranted when:

-   A method becomes an important candidate technology.
-   A previously promising method is ruled out.
-   Paper + code analysis produces a reliable engineering conclusion.
-   A useful module is identified for Identity, Age, Temporal, Geometry,
    Dataset, Training, or Evaluation.
-   An important limitation changes the project's technical direction.
-   A dataset becomes a serious training / evaluation candidate.
-   An architecture decision changes.
-   An experiment confirms or rejects an important assumption.
-   A major open problem is identified.
-   The priority of a research direction materially changes.

### Update is normally NOT required when:

-   A paper is merely discovered.
-   A repository is bookmarked but not analyzed.
-   A minor implementation detail is found.
-   A speculative idea has not yet survived technical analysis.
-   Information is useful only for the current debugging context.

Use the principle:

``` text
Interesting information
        ≠
Persistent research state
```

------------------------------------------------------------------------

## 9. Research Map Update Format

When suggesting an update, the AI should summarize the proposed changes
rather than rewriting unrelated sections.

Preferred structure:

``` text
Research Map Update

Section:

Add:
- ...

Modify:
- ...

Remove / Downgrade:
- ...

Reason:
- ...
```

Important conclusions should distinguish:

-   Author Claim
-   Experimental Evidence
-   Architecture Inference
-   Engineering Hypothesis

The Research Map should preferentially preserve conclusions supported by
primary sources, code inspection, experiments, or clearly labeled
engineering inference.

------------------------------------------------------------------------

## 10. Candidate Technology Lifecycle

Promising technologies should move through an explicit research
lifecycle where useful.

``` text
DISCOVERED
    ↓
SCREENING
    ↓
CANDIDATE
    ↓
DEEP ANALYSIS
    ↓
VALIDATED / REJECTED / DEFERRED
    ↓
ARCHITECTURE CANDIDATE
    ↓
EXPERIMENTAL
    ↓
ADOPTED / REJECTED
```

Suggested meanings:

-   **DISCOVERED** --- potentially relevant; not yet evaluated.
-   **SCREENING** --- undergoing initial relevance assessment.
-   **CANDIDATE** --- appears technically useful for Re-Aging.
-   **DEEP ANALYSIS** --- Paper / Code / Training / Data are being
    investigated.
-   **VALIDATED** --- evidence supports the intended technical role.
-   **REJECTED** --- unsuitable or not worth pursuing for the intended
    role.
-   **DEFERRED** --- potentially useful but currently low priority or
    blocked.
-   **ARCHITECTURE CANDIDATE** --- being considered as part of our
    system design.
-   **EXPERIMENTAL** --- actively being tested.
-   **ADOPTED** --- selected for the current architecture / training
    strategy.

Not every paper needs to go through the entire lifecycle.

------------------------------------------------------------------------

## 11. Research Chat Closeout

When a major research task reaches a natural conclusion, the AI should
offer or provide a compact closeout before moving to a new research
branch.

Recommended structure:

``` text
# Research Closeout

Topic:

Status:

Key Findings:
1.
2.
3.

Engineering Conclusion:

Re-Aging Relevance:
- Directly Usable / Backbone Candidate / Identity Module / Age Conditioning
- Temporal Module / Geometry Module / Dataset / Training Strategy
- Evaluation Method / Benchmark Only / Not Worth Pursuing

Confidence / Evidence:

Research Map Changes:
- Add:
- Modify:
- Remove / Downgrade:

Open Questions:

Recommended Next Research Task:
```

Closeouts should capture durable conclusions, not repeat the entire
conversation.

------------------------------------------------------------------------

## 12. Starting a New Chat

A new chat should begin with a clear research objective whenever
practical.

Example:

``` text
Research Task:
Analyze ConsisID as a potential Identity Preservation module for Video Re-Aging.

Questions:
1. How is identity conditioned?
2. What modules are pretrained / frozen / trainable?
3. Does the method require identity-specific training?
4. Can the identity mechanism be separated from the original generation pipeline?
5. Could it be integrated into our Re-Aging video architecture?
```

The new chat may rely on Project Instructions, Project Files, and
Project-only memory, but important assumptions should be made explicit
when precision matters.

------------------------------------------------------------------------

## 13. Chat Naming Convention

Use a consistent naming convention for formal research chats so the
Project chat list remains readable as the research program grows.

Preferred format:

``` text
[Research Type] [Sequence] — [Topic]
```

Examples:

``` text
Landscape 01 — Re-Aging Technical Landscape
Deep Analysis 01 — MyTimeMachine
Deep Analysis 02 — TimeMachine
Deep Analysis 03 — Aging Multiverse
Dataset Research 01 — Same-Identity Cross-Age Data
Module Research 01 — Identity Conditioning
Module Research 02 — Temporal Consistency
Architecture 01 — Image Re-Aging v0.1
Implementation 01 — MyTimeMachine Reproduction
Experiment 01 — PuLID Re-Aging Stress Test
Evaluation 01 — Re-Aging Evaluation Protocol
```

### 13.1 Sequence Rules

Chat sequence numbers represent the order of research tasks within a
Research Type and are independent from the numbered sections in
`Re-Aging_Research_Map.md`.

Example:

``` text
Research Map:
02 Identity Preservation

Chat:
Deep Analysis 04 — PuLID
```

`02` identifies the technical taxonomy section, while `04` identifies
the Deep Analysis sequence.

Do not intentionally reuse Research Map section numbers as chat sequence
numbers unless they happen to coincide.

### 13.2 Recommended New Chat Handoff

Whenever the AI recommends opening a New Chat, it should also provide:

``` text
Recommended New Chat

Chat Name:
[Research Type] [Sequence] — [Topic]

Research Map:
[Relevant section / candidate]

Research Type:
[Landscape / Deep Analysis / Dataset Research / Module Research /
 Architecture / Implementation / Experiment / Evaluation]

Objective:
[One concise research objective]

Start Prompt:
"[Suggested first message]"
```

The user may use the recommended Chat Name to manually rename the chat
if the ChatGPT interface generates a different title.

The AI should not claim that it can directly control or rename the
ChatGPT UI chat title unless such a capability is actually available.

### 13.3 Branch Naming

Branches are temporary exploratory forks and normally do not require
formal sequence numbers.

Preferred format:

``` text
Branch — [Hypothesis / Topic]
```

Examples:

``` text
Branch — FLUX Migration
Branch — Longitudinal Data Strategy
Branch — Optical Flow Alternative
```

If a Branch becomes important enough to require a formal numbered
research title, this is normally a signal to:

``` text
Branch
  ↓
Research Closeout
  ↓
Update Research Map if warranted
  ↓
Promote to clean New Chat
```

### 13.4 Naming Principle

Chat names should describe the research task, not merely the broad
project domain.

Prefer `Deep Analysis 01 — MyTimeMachine` over `Re-Aging Research`.

Prefer `Module Research 02 — Temporal Consistency` over a generic title.

The goal is for the Project chat list itself to function as a
lightweight research index.

------------------------------------------------------------------------

## 14. Evidence Hierarchy

Durable research conclusions should prioritize evidence in approximately
this order:

1.  Reproducible experimental result produced by this project
2.  Official source code / configuration / checkpoint behavior
3.  Original paper / supplementary material
4.  Official project page / author documentation
5.  Author statements
6.  Architecture inference
7.  Engineering hypothesis
8.  Secondary commentary

Conflicting evidence should be explicitly noted rather than silently
reconciled.

When Paper, README, and actual Code disagree, prioritize the actual
implementation for reproducibility analysis while clearly documenting
the discrepancy.

A project experiment should only be treated as top-tier evidence when its
setup and outputs are recorded well enough to reproduce or audit the
result. The minimum reproducibility record is defined in Section 19.

------------------------------------------------------------------------

## 15. Research State vs Detailed Notes

The project should avoid turning `Re-Aging_Research_Map.md` into an
oversized paper archive.

Use this separation:

``` text
Detailed Paper / Repository Analysis
              ↓
        Research Chat / Report
              ↓
       Durable Conclusions
              ↓
     Re-Aging_Research_Map.md
```

If detailed research artifacts become numerous, separate reports may
later be introduced, for example:

``` text
Model_Reports/
Dataset_Reports/
Experiment_Reports/
```

This is a logical organization convention; it does not require the
ChatGPT Project interface to support folders.

Do not introduce additional artifact layers until the research volume
justifies them.

------------------------------------------------------------------------

## 16. Architecture Decision Management

Architecture decisions require stronger evidence than paper discovery.

Before promoting a technology into `09 Our Re-Aging Architecture`,
evaluate when applicable:

-   Technical role
-   Identity impact
-   Age controllability
-   Temporal impact
-   Geometry impact
-   Data requirements
-   Training feasibility
-   Inference cost
-   Integration complexity
-   Open-source / licensing constraints
-   Reproducibility
-   Production potential

Architecture decisions should distinguish:

``` text
Candidate
→ Proposed
→ Experimental
→ Adopted
```

Rejected approaches should retain a short reason when the failure is
likely to prevent repeated investigation of the same dead end.

------------------------------------------------------------------------

## 17. AI Proactive Responsibilities

During project discussions, the AI Research Partner should proactively
but selectively provide workflow reminders.

### Branch Recommendation

Trigger when a side hypothesis directly depends on the current local
context but should not disrupt the main research line. Keep the branch
exploratory and shallow. If it becomes substantial, recommend a closeout
and promotion to a clean New Chat.

### Chat Boundary Reminder

Trigger when a meaningful semantic boundary or context degradation risk
appears.

Example:

> This has become an independent research branch. I recommend opening a
> new chat for the temporal-consistency investigation while keeping the
> current chat as the completed Model A analysis.

### Research Map Update Reminder

Trigger when a durable conclusion changes the technical map, candidate
list, architecture direction, dataset strategy, evaluation strategy, or
an important open question.

### Experiment Boundary Reminder

Trigger when literature / code analysis has reached a question that
cannot be resolved reliably without empirical testing.

When this occurs, distinguish:

``` text
Research conclusion
→ what is already supported

Experiment hypothesis
→ what still requires testing
```

State the current experiment readiness level rather than implying that
a designed experiment has already been implemented or executed.

Do not interrupt the user for every minor finding.

Workflow reminders should support research rather than dominate it.

------------------------------------------------------------------------

## 18. Research Visualization & Diagram Policy

Research visualization has two distinct roles in this project:

``` text
ASCII Research Sketch
        =
Working / Thinking Representation

Editorial Diagram
        =
Durable Communication / Architecture Validation Representation
```

The default during active research is **ASCII**. Formal diagrams should be
created selectively, after the underlying research state is sufficiently stable.

### 18.1 Default Rule — ASCII First

During active investigation, use prose plus ASCII sketches for:

-   architecture hypotheses
-   uncertain module relationships
-   Paper vs Code discrepancies
-   training-pipeline reconstruction
-   competing explanations
-   provisional integration ideas
-   experiment design
-   failure analysis

ASCII is preferred during this phase because it is fast to modify, has low
context overhead, and can represent uncertainty without forcing premature
layout or architectural certainty.

Example:

``` text
Age Representation ?
        │
        ├─ Global Age Prior
        │    └─ evidence: partial
        │
        ├─ Personalized Residual ?
        │    └─ engineering hypothesis
        │
        └─ Factorized Controls
             ├─ Texture
             ├─ Soft Tissue
             └─ Hair
```

Do not convert every useful ASCII sketch into a formal diagram.

### 18.2 When to Use diagram-design

Use `diagram-design` when a visual has durable value and the reader will learn
materially more from the visual than from prose, a table, or a lightweight ASCII
sketch.

Typical triggers include:

-   a system-level architecture has become a durable project hypothesis
-   a Research Closeout establishes a stable module relationship
-   a training / inference / dataset pipeline needs to become canonical
-   a multi-model comparison is easier to understand spatially
-   a research-state map or dependency structure will be reused across chats
-   a diagram exposes architecture gaps, missing interfaces, or conflicting paths
-   a report / presentation needs a publication-quality technical visual

Typical non-triggers include:

-   a paper was merely discovered
-   a minor implementation detail was found
-   an architecture idea remains highly speculative
-   the visual would contain only one or two obvious nodes
-   a table or paragraph communicates the same information more clearly
-   the diagram would be created only for decoration

Use the principle:

``` text
Useful research sketch
        ≠
Canonical diagram
```

### 18.3 Canonical Visualization Flow

Preferred workflow:

``` text
Research Chat
   │
   ├─ Prose reasoning
   └─ ASCII working sketch
            ↓
      Evidence stabilizes
            ↓
      Engineering Conclusion
            ↓
   Research Closeout / Research Map Update
            ↓
       diagram-design
            ↓
       Canonical Visual
```

Formal diagrams are **derived artifacts**. They do not replace the underlying
sources, evidence, Research Closeout, or `Re-Aging_Research_Map.md`.

If a diagram conflicts with verified evidence or the current Research Map, the
evidence / Research Map takes precedence and the diagram should be regenerated.

### 18.4 diagram-design Project Asset

The project may use the uploaded `diagram-design.zip` skill package as the
formal visualization system.

The package contains:

``` text
diagram-design/
├─ SKILL.md
├─ references/
├─ assets/
└─ scripts/
```

When generating a diagram, load only the minimum relevant material, normally:

``` text
SKILL.md
+
style-guide.md
+
one relevant type reference
```

Examples:

``` text
System architecture
→ type-architecture.md

Training / dataset movement
→ type-data-flow.md or type-process.md

Decision logic
→ type-flowchart.md

Hierarchical module stack
→ type-layers.md

Dependency structure
→ type-dependency.md

Research hierarchy
→ type-tree.md

Research chronology
→ type-timeline.md

Two-axis prioritization
→ type-quadrant.md
```

Do not load all reference files or example assets into research context by
default. Selective loading is preferred to minimize context and reasoning
overhead.

### 18.5 Diagram Style Gate

Before the **first formal diagram** for this project, resolve the visual style
profile required by `diagram-design`.

If the bundled style guide is still using its default tokens, ask the user to
either:

-   customize a Re-Aging project style, or
-   explicitly keep the default diagram-design style.

Do not interrupt ordinary research merely to configure diagram styling. Resolve
this gate only when the first formal diagram is actually needed.

Once a project style has been established, reuse it for later canonical diagrams
so the visual language remains consistent.

### 18.6 Diagram Epistemic Integrity

A polished diagram must not make uncertain research look more certain than the
evidence supports.

Where relevant, preserve distinctions such as:

-   **Author Claim**
-   **Experimental Evidence**
-   **Architecture Inference**
-   **Engineering Hypothesis**

Uncertain, optional, proposed, or unvalidated relationships should be visually
or textually marked as such rather than drawn as unquestioned production paths.

A diagram should not silently transform:

``` text
A may influence B
```

into:

``` text
A → B
```

without preserving the uncertainty.

### 18.7 Complexity / Density Rule

Prefer editorial clarity over completeness.

Project defaults:

-   aim for moderate information density
-   use only nodes that carry distinct technical meaning
-   highlight only the true focal element(s)
-   remove redundant connections when layout already communicates the relation
-   if a diagram grows beyond roughly 9 major nodes, consider splitting it into
    two diagrams rather than creating a single dense system map

For very large architectures, prefer:

``` text
Overview Diagram
        +
Focused Module Diagram(s)
```

rather than one all-inclusive diagram.

### 18.8 Output and Validation

The preferred canonical output is a self-contained HTML file with inline SVG,
following the `diagram-design` output specification.

PNG or other export formats may be produced when required for a report,
presentation, or external tool, but the HTML/SVG version should remain the
editable / inspectable source when practical.

When a formal diagram is generated, run the included `scripts/self_check.py`
validation where applicable before treating the artifact as complete.

### 18.9 AI Proactive Responsibility for Diagrams

The AI should recommend a formal diagram **selectively**, not routinely.

A recommendation is appropriate when:

-   an architecture-level conclusion has stabilized
-   multiple modules are becoming difficult to reason about in prose
-   a durable pipeline has emerged
-   the visual is likely to reveal missing interfaces or contradictions
-   the same conceptual structure will be reused across future research tasks

Do not pause research to beautify intermediate reasoning.

The operating rule is:

> **ASCII for thinking. diagram-design for durable understanding.**

------------------------------------------------------------------------

## 19. Research-to-Experiment Workflow

Research should move into a formal Experiment only when there is a
specific technical uncertainty that can be tested.

The purpose of an Experiment is not to generate attractive examples.
It is to convert a research hypothesis into evidence that can support,
reject, refine, or defer an architecture decision.

The canonical transition is:

``` text
Research Finding
        ↓
Testable Hypothesis
        ↓
Experiment Objective
        ↓
Variables / Controls
        ↓
Metrics / Failure Criteria
        ↓
Decision Criteria
        ↓
Experiment Handoff
        ↓
Implementation
        ↓
Execution
        ↓
Analysis
        ↓
Engineering Interpretation
        ↓
Research Map / Architecture Decision
```

Not every Deep Analysis requires an Experiment. An Experiment is
warranted when additional literature or code reading is unlikely to
resolve the uncertainty and empirical behavior is material to the
project decision.

### 19.1 Research-to-Experiment Handoff

Before opening a formal Experiment task, define at minimum:

-   the research finding that motivates the test
-   the hypothesis being tested
-   the experiment objective
-   independent variables
-   dependent variables / metrics
-   controlled variables
-   required data / inputs
-   expected implementation changes, if any
-   decision criteria
-   known confounders or evaluator bias risks

Preferred handoff structure:

``` text
# Experiment Handoff

Source Research:
[Deep Analysis / Architecture / Dataset / Module research task]

Research Finding:
[What is currently known]

Hypothesis:
[What remains to be tested]

Objective:
[What the experiment must determine]

Independent Variables:
- ...

Dependent Variables / Metrics:
- ...

Controlled Variables:
- ...

Inputs / Dataset:
- ...

Implementation Requirement:
- None / Instrumentation / Architecture Modification / Retraining

Decision Criteria:
- ...

Known Risks / Confounders:
- ...

Recommended Experiment Chat:
Experiment NN — [Topic]
```

A handoff should be specific enough that the Experiment chat does not
need to rediscover why the experiment exists.

### 19.2 Experiment Readiness Lifecycle

Use explicit experiment states rather than vague terms such as
"ready to run."

``` text
PROPOSED
    ↓
DESIGNED
    ↓
IMPLEMENTATION-READY
    ↓
EXECUTABLE
    ↓
EXECUTED
    ↓
ANALYZED
    ↓
VALIDATED / REJECTED / INCONCLUSIVE
```

Suggested meanings:

-   **PROPOSED** --- an empirical question has been identified, but the
    experiment is not yet sufficiently specified.
-   **DESIGNED** --- hypothesis, variables, controls, metrics, and
    decision criteria are defined.
-   **IMPLEMENTATION-READY** --- repository / model assumptions,
    configuration, data requirements, execution plan, and evaluation
    plan are sufficiently explicit for implementation.
-   **EXECUTABLE** --- the required code, environment, configuration,
    checkpoints, and data are in place and the experiment can actually
    be launched.
-   **EXECUTED** --- the experiment has actually been run and raw
    outputs have been preserved.
-   **ANALYZED** --- outputs have been evaluated, failure cases
    inspected, and the result has been interpreted.
-   **VALIDATED** --- evidence supports the tested hypothesis or
    intended technical role.
-   **REJECTED** --- evidence contradicts the tested hypothesis or
    shows the approach is not worth pursuing for the intended role.
-   **INCONCLUSIVE** --- the current evidence is insufficient because
    of noise, confounding, implementation uncertainty, inadequate data,
    or conflicting metrics.

Do not use **EXECUTED**, **ANALYZED**, **VALIDATED**, or **REJECTED**
unless the corresponding work has actually occurred.

An experiment design created in a Research Chat may reach **DESIGNED**
or, in some cases, **IMPLEMENTATION-READY**. It is not **EXECUTABLE**
until the code / environment / data required to launch it actually
exist.

### 19.3 Experiment vs Implementation Boundary

Use an **Experiment** task when the primary question is:

> Does hypothesis X hold under controlled conditions?

Use an **Implementation** task when the primary question is:

> How do we build, modify, reproduce, or integrate system Y?

Examples:

``` text
Sweep PuLID id_weight × ID insertion timestep
to measure Identity–Age trade-off
        ↓
Experiment
```

``` text
Modify PuLID IDFormer so biometric and visual
identity features can be controlled independently
        ↓
Implementation
```

A small amount of instrumentation, configuration, or scripting required
to execute an experiment may remain inside the Experiment chat.

Open a separate Implementation chat when:

-   the code modification becomes a substantial engineering task
-   a reusable module or fork is being created
-   architecture changes must be designed independently of the original
    experiment
-   debugging / reproduction dominates the discussion
-   multiple experiments will depend on the same new implementation

Preferred flow when both are required:

``` text
Experiment Question
        ↓
Implementation Dependency Identified
        ↓
Implementation Task
        ↓
Executable Module / Fork
        ↓
Return to Experiment
```

### 19.4 Minimum Reproducibility Record

An experiment should preserve enough information to reproduce or audit
its result.

Record, when applicable:

``` text
Repository / source
Commit / revision
Environment
Python version
PyTorch / framework version
CUDA / accelerator version
Dependencies
Model / checkpoint version
Dataset / input manifest
Preprocessing version
Configuration
Prompt / conditioning
Random seed(s)
Exact execution command
Hardware
Evaluation model(s) / version(s)
Metric implementation
Raw outputs
Aggregated results
Failure annotations
```

A result such as:

``` text
"PuLID looked better in our test"
```

is not sufficient durable evidence.

A result should instead be tied to a reproducible configuration and
observable output.

If the experiment modifies upstream source code, preserve or document:

-   the exact patch / diff
-   changed files
-   changed configuration
-   whether the change is instrumentation-only or architecture-changing

### 19.5 Experiment Design Principles

Experiments should be decision-oriented.

Prefer experiments that isolate one important uncertainty rather than
large uncontrolled demonstrations.

Where applicable, explicitly define:

-   baseline
-   treatment / candidate method
-   independent variable sweep
-   fixed controls
-   repeated seeds
-   evaluator independence
-   confounders
-   failure taxonomy
-   success / failure thresholds

Avoid circular evaluation when practical.

For example:

``` text
Conditioning / Training Encoder
        =
Evaluation Encoder
```

may create evaluator-alignment bias. Prefer at least one independent
evaluator when the experiment is making claims about Identity, Age,
Geometry, Temporal Consistency, or another learned semantic property.

For Re-Aging specifically, visual plausibility should not replace
measurement of the intended technical property.

Examples:

``` text
High Face Similarity
        ≠
Correct Target Age

Correct Target Age
        ≠
Identity Preservation

Smooth Video
        ≠
Temporally Correct Aging

Recognizable Face
        ≠
Geometry Consistency
```

### 19.6 Experiment Closeout

When an Experiment reaches **ANALYZED**, produce a compact Experiment
Closeout.

Recommended structure:

``` text
# Experiment Closeout

Experiment:

Status:
[ANALYZED / VALIDATED / REJECTED / INCONCLUSIVE]

Source Hypothesis:

Setup:
- Repository / commit:
- Checkpoint:
- Dataset / inputs:
- Variables:
- Controls:
- Metrics:
- Seeds / runs:

Primary Results:

Failure Analysis:

Hypothesis Outcome:
- Supported / Rejected / Inconclusive

Experimental Evidence:
- ...

Engineering Interpretation:
- ...

Architecture Impact:
- Promote / Modify / Downgrade / Defer / No Change

Research Map Changes:
- Add:
- Modify:
- Remove / Downgrade:

Limitations / Confounders:

Recommended Follow-up:
```

The closeout should separate observation from interpretation.

Use the distinction:

``` text
Experimental Evidence
        ≠
Architecture Inference
        ≠
Durable Engineering Conclusion
```

Example:

``` text
Experimental Evidence:
At id_weight = 1.0, realized age displacement decreased
under the tested configuration.

Architecture Inference:
Strong identity conditioning may suppress large age edits.

Not yet justified:
PuLID cannot support Re-Aging.
```

### 19.7 Experiment → Research Map Promotion Rule

Do not promote every experiment output into the Research Map.

Promotion is normally warranted when:

-   the experiment materially changes a candidate's status
-   a hypothesis is supported or rejected with adequate evidence
-   a failure mode changes architecture direction
-   a module interface is validated
-   a dataset / metric / training strategy becomes a serious project
    choice
-   repeated or sufficiently controlled evidence supports a durable
    conclusion

Promotion is normally not warranted when:

-   only a few cherry-picked examples were inspected
-   the environment or checkpoint is uncertain
-   the evaluator is known to be biased toward the tested method
-   results are highly seed-sensitive and not yet characterized
-   an implementation bug may explain the result
-   the experiment is still **INCONCLUSIVE**

Preferred evidence flow:

``` text
Raw Result
        ↓
Experiment Analysis
        ↓
Experimental Evidence
        ↓
Engineering Interpretation
        ↓
Durable Conclusion
        ↓
Research Map
```

If a single experiment produces surprising evidence that conflicts with
multiple stronger sources, record the conflict rather than immediately
overwriting the Research Map.

### 19.8 Experiment Artifact Convention

When practical, a formal experiment should produce a reusable artifact
bundle rather than scattered commands and screenshots.

Suggested logical structure:

``` text
experiments/
└─ expNN_topic/
   ├─ README.md
   ├─ configs/
   ├─ dataset_manifest.*
   ├─ scripts/
   ├─ outputs/
   │   ├─ raw/
   │   ├─ metrics.*
   │   └─ failures.*
   └─ reports/
       └─ experiment_closeout.md
```

This is a logical project convention. The exact filesystem layout may be
adapted to the repository being tested.

The important requirement is that configuration, execution, raw
outputs, metrics, and interpretation remain traceable to one another.

### 19.9 AI Proactive Responsibility for Experiments

The AI Research Partner should proactively identify when a research
question has crossed from literature / code analysis into an empirical
question.

When recommending an Experiment, the AI should:

1.  state what uncertainty requires empirical testing
2.  define the initial hypothesis
3.  indicate the current readiness state
4.  distinguish inference-only testing from retraining
5.  identify major implementation dependencies
6.  recommend a formal Experiment chat when execution becomes a
    substantial independent task

The AI should not claim an experiment was run, validated, or reproduced
unless it actually was.

The AI should also avoid prematurely expanding every architecture idea
into a large experiment program. Start with the smallest experiment
capable of changing the project decision.

------------------------------------------------------------------------

## 20. Default Research Cycle

Unless the task requires another approach, use the following research
cycle:

``` text
1. Define Research Question
        ↓
2. Discover Primary Sources
        ↓
3. Initial Relevance Screening
        ↓
4. Paper / Architecture Analysis
        ↓
5. Repository / Training Analysis
        ↓
6. Re-Aging Suitability Assessment
        ↓
7. Engineering Conclusion
        ↓
8. Is an important uncertainty empirically testable?
        │
        ├─ No
        │    ↓
        │  Decide Research Map Update
        │
        └─ Yes
             ↓
          Experiment Handoff
             ↓
          Experiment Lifecycle
             ↓
          Engineering Interpretation
             ↓
          Decide Research Map Update
        ↓
9. Decide Continue vs Branch vs New Chat
        ↓
10. Define Next Research Question
```

Not every task requires every step. The process should remain
proportional to the importance of the technology being investigated.

------------------------------------------------------------------------

## 21. Guiding Principle

The purpose of context management is not to create perfect
documentation.

It is to ensure that research progressively converges toward:

``` text
Re-Aging Technical Map
        ↓
Module Selection
        ↓
Architecture Design
        ↓
Dataset Strategy
        ↓
Training Strategy
        ↓
Experiments
        ↓
Evaluation
        ↓
Working Re-Aging Model
        ↓
Production Feasibility
```

Every workflow decision should ultimately support the project's core
question:

> **這個技術對我們建立自己的 Re-Aging 模型，到底能拿來做什麼？**