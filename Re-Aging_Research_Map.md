# Re-Aging Research Map

**Version:** 0.5  
**Project:** Sai_研究_Re-Aging  
**State:** First-round Technical Landscape Screening completed; four P0 Deep Analyses completed; Experiment 01 designed  
**Last Updated:** 2026-09-21

> This file is the canonical high-level research state for the project.  
> It records durable technical conclusions, candidate technologies, architecture hypotheses, and research priorities.  
> Detailed paper / repository analysis should remain in dedicated research chats or reports.

---

# Re-Aging Research Program

```text
Re-Aging Research Program
│
├─ 01 Image Re-Aging
│    ├─ Age Progression / Regression
│    ├─ Diffusion-based Age Editing
│    ├─ Personalized Aging
│    ├─ Age Conditioning
│    ├─ Factorized Aging
│    └─ Directional Aging Residuals
│
├─ 02 Identity Preservation
│    ├─ Face Embedding
│    ├─ Age-Invariant Identity Representation
│    ├─ Identity Loss
│    ├─ Identity Conditioning / Adapter
│    ├─ Identity–Editability Alignment
│    └─ Personalized Generation
│
├─ 03 Video Re-Aging
│    ├─ Video Diffusion
│    ├─ Temporal Attention
│    ├─ Feature Propagation
│    ├─ Optical Flow
│    └─ Video-to-Video
│
├─ 04 Geometry
│    ├─ Landmark
│    ├─ FLAME / 3DMM
│    └─ Geometry Constraint
│
├─ 05 3D / 4D Re-Aging
│    ├─ NeRF
│    ├─ 3DGS
│    ├─ 4DGS
│    ├─ Dynamic Human
│    └─ Neural Avatar
│
├─ 06 Dataset
│    ├─ Cross-sectional
│    ├─ Same Identity Cross-Age
│    ├─ Longitudinal
│    ├─ Video
│    ├─ Multi-view
│    └─ Cross-context Identity Pair Construction
│
├─ 07 Training
│    ├─ Data Strategy
│    ├─ Conditioning
│    ├─ Loss
│    ├─ Identity–Age Alignment
│    └─ Fine-tuning Strategy
│
├─ 08 Evaluation
│    ├─ Identity
│    ├─ Age Accuracy
│    ├─ Temporal Consistency
│    ├─ Geometry
│    ├─ Expression / Motion Preservation
│    └─ Production Robustness
│
└─ 09 Our Re-Aging Architecture
     ├─ Candidate Modules
     ├─ Architecture v0.x
     ├─ Experiments
     └─ Open Problems
```

---

# 01 Image Re-Aging

## Current Research State

The 2024–2026 landscape suggests that direct Re-Aging methods are improving, but no single public method should currently be assumed to solve identity preservation, fine-grained age control, video consistency, geometry consistency, and production requirements simultaneously.

Current project direction:

```text
Generic Aging Prior
        +
Identity-Specific Information
        +
Fine-Grained Age Conditioning
        ↓
Identity-Preserving Image Re-Aging
```


## Aging Factor Decomposition — New Architecture Hypothesis

**Status:** ENGINEERING HYPOTHESIS — HIGH PRIORITY

Aging should not necessarily be represented as one monolithic scalar / embedding.

A more controllable formulation is to decompose visible aging into partially independent factors:

```text
Age Condition
│
├─ Texture / Surface Aging
│    ├─ Wrinkles
│    ├─ Fine lines
│    ├─ Freckles / age spots / pigmentation
│    ├─ Skin roughness
│    └─ Pore / micro-texture change
│
├─ Soft-Tissue / Shape Aging
│    ├─ Skin laxity
│    ├─ Fat redistribution / volume loss
│    ├─ Cheek descent
│    ├─ Jowl formation
│    ├─ Nasolabial / marionette structural change
│    └─ Perceived facial silhouette shift
│
├─ Hair Aging
│    ├─ Graying
│    ├─ Density loss
│    └─ Hairline change
│
├─ Periocular / Oral Aging
│    ├─ Eyelid / eye-bag change
│    ├─ Lip volume change
│    └─ Teeth-related appearance change
│
└─ Optional Geometry / Skeletal Aging
     ├─ 3D facial structure constraints
     └─ age-related low-frequency shape change
```

Important distinction:

```text
Texture Aging
→ mostly high-frequency appearance change

Soft-Tissue Aging
→ low-/mid-frequency deformation and volume redistribution

Geometry Aging
→ explicit structural / 3D change
```

This distinction may allow a future Re-Aging system to control:

```text
target_age
+
texture_age_strength
+
soft_tissue_age_strength
+
hair_age_strength
+
optional_geometry_age_strength
```

rather than forcing all age effects to move together through a single age embedding.

Potential architecture direction:

```text
Target Age
   ↓
Age Representation
   │
   ├─ Texture Age Tokens
   ├─ Soft-Tissue Age Tokens
   ├─ Hair Age Tokens
   └─ Geometry Age Tokens
           ↓
Selective / Region-Aware Conditioning
           ↓
Re-Aging Backbone
```

Research implication:

- TimeMachine's single Age Codebook can be treated as a useful **v0 population age prior**.
- Aging Multiverse provides evidence that a scalable **feature-distribution aging residual** can regularize age transformation, but it does **not** provide a factorized age representation.
- A future system may replace or augment a monolithic age representation with a **factorized age representation / age manifold**.
- Geometry and soft-tissue aging should not be evaluated only by face-recognition similarity, because legitimate age transformation may require meaningful shape change.

## Candidate Technologies

### MyTimeMachine

**Status:** DEEP ANALYSIS COMPLETED — CANDIDATE  
**Potential Role:** Personalized Aging / Longitudinal Identity Modeling

Why it matters:

- Explicitly targets personalized facial aging rather than only population-average aging.
- Uses same-person cross-age photo history to adapt a global aging prior.
- Directly relevant to the question of how generic aging knowledge should be combined with identity-specific aging information.
- Provides an important reference for longitudinal / personalized aging training strategy.

Key research question:

> How much of MyTimeMachine's personalized aging mechanism can be separated from its original backbone and reused in a modern diffusion / DiT Re-Aging architecture?

---

### TimeMachine

**Status:** DEEP ANALYSIS COMPLETED → ARCHITECTURE CANDIDATE  
**Potential Role:** Primary Age Conditioning / Population-Level Age Representation Reference

Deep Analysis conclusion:

- TimeMachine is more valuable to this project as an **Age Conditioning architecture reference** than as a final Re-Aging backbone.
- Its strongest reusable contribution is the separation of age and identity into distinct conditioning paths.
- The reported ablations support **decoupled age / identity conditioning**, but do not establish complete semantic disentanglement.
- The original implementation is based on Stable Diffusion 1.5; the transferable asset is therefore the conditioning topology, not the original UNet backbone.

Primary reusable modules:

```text
Population Face Data
      ↓
Age Encoder Features
      ↓
Same-Age Aggregation
      ↓
Age Codebook
      ↓
Age Projection
      ↓
Dedicated Age Conditioning Path
```

and

```text
Image / Latent Features
        │
        ├─ Text Conditioning
        ├─ Identity Conditioning
        ├─ Age Embedding Conditioning
        └─ Explicit Target-Age Conditioning
                ↓
      Decoupled Multi-Cross-Attention
```

Key experimental evidence reported by the paper:

```text
Full model:
Age MAE = 3.840
Face Similarity = 0.67

Without Age branch:
Age MAE = 20.516

Without Identity branch:
Face Similarity = 0.06

Without ACG:
Age MAE = 3.915
```

Interpretation:

- **Age branch** is a major contributor to target-age control.
- **Identity branch** is a major contributor to identity preservation.
- **ACG** provides only a relatively small refinement in the reported ablation and should not currently be treated as a mandatory architecture component.

Important limitations:

- Stable Diffusion 1.5 backbone.
- No temporal / video mechanism.
- No explicit FLAME / 3DMM / geometry constraint.
- No multi-view consistency mechanism.
- HFFA is not established as a public production-usable dataset.
- Official training code / inference code / checkpoints were not verified as publicly available during Deep Analysis.
- MiVOLO is used both for age annotation / age representation construction and age evaluation, creating possible estimator-alignment bias.

Engineering conclusion:

> Use TimeMachine primarily as an **Age Conditioning / Age Representation module reference**, and migrate its concepts into a modern diffusion / DiT backbone rather than reproducing the original system unchanged.

Candidate module priority:

1. **HIGH VALUE** — Age Codebook / population-level age representation.
2. **HIGH VALUE** — Decoupled age / identity conditioning.
3. **HIGH VALUE** — Independent projection modules for heterogeneous conditions.
4. **MEDIUM VALUE** — Age-branch strength scaling as a controllability interface.
5. **MEDIUM / LOW VALUE** — Age Classifier Guidance (ACG).

Current architecture hypothesis:

```text
Generic Age Representation
      TimeMachine-like
             +
Personalized Age Residual
      MyTimeMachine-like
             ↓
Personalized Target-Age Condition
```

This is an **Engineering Hypothesis**, not yet experimentally validated.

---

### Aging Multiverse

**Status:** DEEP ANALYSIS COMPLETED → ARCHITECTURE / EXPERIMENT REFERENCE  
**Potential Role:** Attention-Space Aging Residual / Identity–Editability Mixing / Factorized Aging Experiment Framework

Deep Analysis conclusion:

- Aging Multiverse is more useful as an **inference-time directional residual construction reference** than as a final Re-Aging backbone or a complete age representation.
- Its “multiverse” behavior is primarily created by **condition-dependent prompts / semantic editing branches**, not by multiple explicitly disentangled learned aging directions.
- Simulated Aging Regularization (SAR) constructs an age-related residual from young / old feature distributions and injects it into FLUX attention-space features.
- The released implementation is training-free: the FLUX / text / VAE components remain pretrained and frozen; the method manipulates features during inversion / denoising rather than optimizing model weights.
- The public implementation is strongly tied to FLUX / RF-Solver behavior and includes prompt-, token-layout-, layer-, and timestep-specific assumptions; therefore its residual should **not** be treated as a portable universal Age Embedding.

Primary reusable ideas:

```text
Young Feature Distribution
          vs
Old Feature Distribution
          ↓
Feature-Space Aging Residual
          ↓
Scalable Age Transformation Regularization
```

and:

```text
Source / Inversion Features
          +
Editing Features
          ↓
K/V Mixing and Projection
          ↓
Identity Preservation ↔ Editability Trade-off
```

Important interpretation:

```text
TimeMachine
→ What should represent age?

Aging Multiverse
→ How can an age-related residual be constructed and injected during generation?
```

The two methods should therefore not be treated as equivalent Age Representation candidates.

Factorized-aging implication:

Aging Multiverse itself does **not** provide separate texture / soft-tissue / hair / geometry directions. However, its residual-construction mechanism suggests a direct experimental path:

```text
Matched Feature Distributions
        │
        ├─ Skin / Texture Contrast → ΔTexture
        ├─ Soft-Tissue Contrast   → ΔSoftTissue
        ├─ Hair Contrast          → ΔHair
        └─ Geometry Contrast      → ΔGeometry
                 ↓
       Factorized Direction Bank
```

This is an **Engineering Hypothesis**, not an author claim or validated result.

Identity assessment:

- The method improves the balance between age transformation / prompt alignment and preservation, but does not establish state-of-the-art biometric identity preservation.
- Its strongest identity-related contribution for this project is the **feature-mixing strategy for negotiating identity preservation against strong editing**, not its raw face-similarity score.

Reproducibility / production assessment:

- Core feature extraction / direction construction / editing logic is publicly available.
- The full paper pipeline is only partially reproduced by the public repository because some upstream synthetic-cluster / prompt-refinement steps remain external.
- Inference remains expensive because it operates on FLUX with inversion plus second-order solver passes.
- Production licensing / dependency constraints must be rechecked before adoption.

Engineering conclusion:

> Use Aging Multiverse as an **Age Residual Construction + Identity/Editability Mixing reference**, and use it to design experiments for factorized aging directions. Do not treat its released residual tensors as a directly portable age representation for another DiT.

Candidate module priority:

1. **HIGH VALUE** — Feature-distribution age residual construction.
2. **HIGH VALUE** — Factorized-direction experiment framework.
3. **MEDIUM / HIGH VALUE** — K/V identity–editability mixing principle.
4. **MEDIUM VALUE** — Condition-prompt expansion for controlled aging data / prototyping.
5. **LOW VALUE** — Direct production reuse of the released FLUX-specific implementation.

---

### SelfAge

**Status:** CANDIDATE — P1  
**Potential Role:** Few-Shot Personalized Aging

Why it matters:

- Provides a lower-data alternative to heavier longitudinal personalization.
- Useful for studying the trade-off between number of same-identity cross-age examples and personalized aging quality.

Important comparison:

```text
MyTimeMachine
→ richer personal history

vs

SelfAge
→ few-shot personalization
```

Research question:

> What is the minimum same-identity cross-age supervision required before aging becomes meaningfully personalized instead of generic?

---

### Identity-Aware Facial Age Editing Using Latent Diffusion

**Status:** SCREENING / P2  
**Potential Role:** Identity Loss / Biometric Loss Baseline

Primary value:

- Identity-preservation training objective.
- Useful as a baseline for biometric / identity loss design.

Current assessment:

**POTENTIALLY USEFUL**, mainly as a loss / training reference rather than primary future backbone.

---

# 02 Identity Preservation

## Current Research State

Identity preservation should be treated as an independent conditioning problem rather than assumed to emerge naturally from an age-editing backbone.

Working decomposition:

```text
Age Condition
→ controls what should change

Identity Condition
→ constrains what must remain the same
```

## Candidate Technologies

### PuLID

**Status:** DEEP ANALYSIS COMPLETED → ARCHITECTURE / EXPERIMENT CANDIDATE  
**Potential Role:** Primary Image Identity Conditioning / DiT Identity Adapter / Identity–Editability Training Reference

Deep Analysis conclusion:

- PuLID is highly relevant to Stage A as an **Identity Conditioning architecture candidate**, not as a direct Re-Aging model.
- The transferable value is broader than a face-recognition embedding: PuLID combines biometric identity information with richer visual identity features and injects them through a dedicated identity-conditioning path.
- The SDXL paper is most valuable as an **Identity Fidelity ↔ Editability training reference**.
- The FLUX implementation is most valuable as a **modern DiT identity injection reference**.
- PuLID does not provide Age Control, explicit Geometry Control, Temporal Consistency, or Multi-view Consistency by itself.

Working decomposition:

```text
Reference Face
      │
      ├─ Biometric Identity
      │
      └─ Rich Visual Identity / Appearance
                 ↓
              IDFormer
                 ↓
          Identity Tokens
                 ↓
       Dedicated Identity CA
                 ↓
           Re-Aging DiT
```

Durable architecture finding:

> Identity should remain a dedicated conditioning branch rather than being collapsed into the same prompt / embedding path as age.

Primary reusable components:

1. **HIGH VALUE** — Dedicated Identity Cross-Attention / residual injection.
2. **HIGH VALUE** — IDFormer-style identity token projection / compression.
3. **HIGH VALUE** — Biometric + rich visual identity representation.
4. **HIGH VALUE** — Identity Fidelity ↔ Editability balancing / alignment principle.
5. **MEDIUM / HIGH VALUE** — Timestep / strength-based identity injection controls.

Major Re-Aging risk:

```text
Age Branch
→ must change age-bearing appearance

PuLID Rich Visual Identity
→ may preserve source-age appearance
```

This creates a potential conflict in large age transformations.

Important evidence distinction:

- **Supported by Paper / Code:** PuLID uses rich identity conditioning and explicitly balances identity fidelity against editability.
- **Architecture Inference:** rich visual identity features may contain age-dependent appearance.
- **Experiment Hypothesis:** strong PuLID conditioning may suppress realized age displacement or Soft-Tissue / Shape Aging.

The last two are **not yet experimentally validated**.

High-priority architecture hypothesis:

```text
Identity Representation
      │
      ├─ Age-Invariant Biometric Identity
      │
      └─ Age-Bearing Visual Identity
                 ↓
        Age-Aware Identity Gating
                 ↓
           Re-Aging DiT
```

Possible behavior:

```text
Small |target_age - source_age|
→ preserve more visual identity detail

Large |target_age - source_age|
→ retain strong biometric identity
→ relax age-bearing visual identity
```

This is an **Engineering Hypothesis**, not a validated PuLID capability.

Geometry implication:

```text
High Face Similarity
        ≠
Correct Facial Geometry
```

PuLID therefore does not replace a separate Landmark / FLAME / 3DMM / future geometry branch.

Reproducibility assessment:

```text
Inference Code / Weights
→ Public

SDXL / FLUX Architecture Inspection
→ Strong

Full Official End-to-End Training Reproduction
→ Not verified

Repository Classification
→ Inference Complete / Training Incomplete / Research Prototype
```

Production assessment:

- PuLID architecture is potentially production-adaptable.
- The stock PuLID-FLUX dependency stack should not be assumed production-cleared merely from the repository license.
- Production adoption requires separate review / replacement of backbone and face-recognition dependencies where licensing demands it.

Engineering conclusion:

> Use PuLID as the current primary **Identity Conditioning architecture / experiment candidate** for Stage A. The next decision must come from a Re-Aging-specific Identity–Age stress test rather than generic personalization metrics.

Next validation task:

> **Experiment 01 — PuLID Re-Aging Stress Test**

---

### InfiniteYou

**Status:** CANDIDATE — P1  
**Potential Role:** DiT Identity Injection Candidate

Why it matters:

- Modern DiT / FLUX-oriented identity conditioning.
- Useful comparison against PuLID for architecture compatibility with a future Re-Aging DiT.

Primary comparison:

```text
PuLID
vs
InfiniteYou
```

Evaluate:

- Identity fidelity
- Editability
- DiT compatibility
- Injection location
- Training requirement
- Licensing / production feasibility

---

### InstantID

**Status:** REFERENCE / BASELINE  
**Potential Role:** Fast Identity-Conditioning Prototype

Why it matters:

- Useful zero-/low-training baseline for initial experiments.

Caution:

- Production licensing of dependent face-recognition components must be checked separately from repository license.

Current assessment:

**Useful for prototype / baseline, not yet preferred as production identity module.**

---

# 03 Video Re-Aging

## Current Research State

The first-round landscape suggests that building an end-to-end Video Re-Aging foundation model immediately is unnecessarily high-risk.

Preferred initial direction:

```text
Strong Image Re-Aging
        ↓
Temporal Propagation / Video Editing
        +
Video Identity Conditioning
        ↓
Temporally Consistent Video Re-Aging
```

This is currently an **Engineering Hypothesis**, not an experimentally validated project decision.

## Candidate Technologies

### AnyV2V

**Status:** CANDIDATE — P0 Deep Analysis  
**Potential Role:** Image Re-Aging → Video Re-Aging Bridge

Why it matters:

- Converts video editing into a first-frame / image-editing-centered workflow.
- Uses temporal / attention feature injection to propagate edits.
- Could allow rapid Level 2 prototype development without training a dedicated Re-Aging video model first.

Candidate prototype:

```text
Original Video
      ↓
Edit First Frame with Re-Aging Model
      ↓
Aged First Frame
      +
Original Video Motion / Features
      ↓
AnyV2V-like Propagation
      ↓
Aged Video
```

Key Deep Analysis questions:

- How are temporal features injected?
- Which source-video features are preserved?
- Does strong facial aging survive propagation?
- Where are face, hair, teeth, eyes, and skin texture likely to flicker?

---

### ConsisID

**Status:** CANDIDATE — P0 Deep Analysis  
**Potential Role:** Video Identity Conditioning

Why it matters:

- Directly addresses identity preservation in video generation.
- Relevant as a reusable identity branch inside a future Video Re-Aging system.

Target concept:

```text
Video Re-Aging Backbone
        +
ConsisID-like Identity Conditioning
        ↓
Lower Identity Drift Across Frames
```

Deep Analysis focus:

- Identity representation
- Injection locations
- Trainable / frozen modules
- Temporal behavior
- Whether the identity mechanism is separable from original T2V generation

---

### Phantom

**Status:** CANDIDATE — P0/P1  
**Potential Role:** Subject-Level Video Consistency / Future Full-Body Re-Aging

Why it matters:

Face embedding alone may eventually be insufficient for full-body Re-Aging.

Future subject consistency must preserve:

```text
Face
Body Shape
Hair
Clothing Relationship
Overall Subject Appearance
```

Phantom is therefore more relevant as a **subject representation / subject consistency** reference than as a direct aging model.

---

### Magic Mirror

**Status:** CANDIDATE — P1  
**Potential Role:** Face-Specific Video Identity Conditioning

Primary value:

- Alternative video identity architecture for comparison with ConsisID.

Deep Analysis comparison target:

```text
ConsisID
vs
Magic Mirror
```

Evaluate:

- Identity representation
- Structural conditioning
- Motion preservation
- Temporal stability
- Training-data construction

---

### VideoGrain

**Status:** SCREENING — P1/P2  
**Potential Role:** Localized / Part-Level Age Editing Control

Interesting Re-Aging connection:

Aging is both global and locally expressed.

Potential regions:

```text
Skin
Eye Area
Nasolabial Fold
Jaw
Hair
Forehead
```

Possible use:

- Constrain age edits to relevant regions.
- Reduce background modification and unnecessary appearance drift.

---

### UniEdit

**Status:** SCREENING — P1/P2  
**Potential Role:** Motion–Appearance Decomposition

Useful architectural observation:

```text
Spatial / Appearance Features
→ should be editable for aging

Temporal / Motion Features
→ should remain stable
```

This may become a useful design principle for Video Re-Aging.

---

### ReVideo

**Status:** REFERENCE ONLY  
**Potential Role:** Content / Motion Separation Reference

Current assessment:

Useful architectural reference, but lower priority than AnyV2V / ConsisID for current goals.

---

### TokenFlow / Ground-A-Video

**Status:** REFERENCE ONLY  
**Potential Role:** Temporal Feature Propagation / Optical-Flow Consistency Reference

Although some work falls outside the main 2024–2026 discovery window, these methods remain relevant for:

- feature propagation
- inter-frame correspondence
- latent smoothing
- optical-flow constraints
- temporal consistency loss / mechanism design

---

# 04 Geometry

## Current Research State

Geometry should not be treated as equivalent to identity.

A face can remain recognizable while still suffering:

- Face shape drift
- Landmark drift
- Expression distortion
- View inconsistency
- Pose-related deformation

Future Re-Aging should therefore consider a separate geometry constraint path.

## Candidate Technologies

### Gaussian Head Avatar

**Status:** CANDIDATE — P1  
**Potential Role:** Face Geometry / Expression / View Consistency Module

Why it matters:

- High-fidelity dynamic head representation.
- Relevant to stabilizing face geometry and expression across time / views.

Potential future integration:

```text
Original Face
      ↓
3DMM / FLAME / Gaussian Head Representation
      ↓
Geometry / Expression Constraint
      +
2D Age Appearance Editing
```

Current assessment:

**HIGHLY RELEVANT as geometry research, not a direct age-editing backbone.**

---

### SplattingAvatar

**Status:** CANDIDATE — P1  
**Potential Role:** Geometry–Appearance Decomposition / 3DGS Avatar

Important concept:

```text
Mesh
→ low-frequency geometry / motion

3D Gaussians
→ high-frequency appearance
```

Potential Re-Aging interpretation:

```text
Geometry
→ preserve or control explicitly

Appearance
→ age-edit
```

This decomposition is potentially valuable for multi-view-consistent aging.

---

# 05 3D / 4D Re-Aging

## Current Research State

No candidate should be promoted to Level 3 / Level 4 Re-Aging merely because it uses 3DGS, 4DGS, or video.

To qualify as future Re-Aging infrastructure, the representation must help preserve or control:

- Identity
- Geometry
- Expression
- Motion
- View consistency
- Age appearance

## Candidate Technologies

### ExAvatar

**Status:** CANDIDATE — P1/P2  
**Potential Role:** Future Full-Body 3D Re-Aging Representation

Why it matters:

- Combines expressive whole-body modeling with SMPL-X / Gaussian representation concepts.
- Relevant when moving from face-only Re-Aging toward full-body aging.

Possible future role:

```text
SMPL-X Geometry / Motion
       +
Age-Edited Appearance Representation
       ↓
Full-Body Re-Aging Avatar
```

---

### GaussianAvatar

**Status:** SCREENING — P2  
**Potential Role:** Dynamic Full-Body Appearance / Motion Reference

Primary relevance:

- pose-dependent appearance
- animatable human representation
- full-body consistency

Not currently considered a direct Re-Aging solution.

---

### Animatable Gaussians

**Status:** SCREENING — P2  
**Potential Role:** Pose-Dependent Garment / Appearance Modeling

Potential future value:

- Helps reason about separating body motion from high-frequency appearance changes.

Current assessment:

**POTENTIALLY USEFUL for full-body extension, not current core path.**

---

### Human-VDM

**Status:** DEFERRED / REFERENCE ONLY  
**Potential Role:** Single-Image → 3D Human Concept Reference

Reason for deferral:

- Interesting conceptual link between video diffusion and 3D human generation.
- Reproducibility / code availability must be verified before promoting it.

---

# 06 Dataset

## Current Research State

Same-identity cross-age data remains one of the highest-value data categories for identity-preserving Re-Aging.

The project should distinguish:

```text
Large Dataset + Age Label
        ≠
Same Person Across Ages
```

For personalized / identity-preserving aging, the second category may be substantially more valuable even at smaller scale.

## Candidate Dataset / Construction Directions

### Longitudinal Personal Photo Collections

**Status:** HIGH PRIORITY DATA STRATEGY

Potential uses:

- Personalized aging
- Age trajectory modeling
- Age interpolation / extrapolation
- Identity-vs-age disentanglement

Related candidates:

- MyTimeMachine
- SelfAge

---

### Fine-Grained Facial Age Data

**Status:** CANDIDATE FOR DEEP ANALYSIS

Related candidate:

- TimeMachine / HFFA

Need to verify during Deep Analysis:

- Number of identities
- Number of samples
- Age distribution
- Same-person cross-age availability
- Resolution
- Labels
- License
- Commercial restrictions

---

### Phantom-Data-Style Cross-Context Pair Construction

**Status:** CANDIDATE — P0 DATASET STRATEGY

Core idea:

```text
Large Internet Image / Video Corpus
        ↓
Face / Subject Detection
        ↓
Identity Retrieval
        ↓
Cross-Context Identity Verification
        ↓
Same-Identity Training Pairs
```

Potential Re-Aging extension:

```text
Identity Retrieval
       +
Age Estimation / Age Metadata
       ↓
Same Identity
Different Age
Different Context
       ↓
Re-Aging Training Dataset
```

Engineering hypothesis:

> Large-scale identity retrieval plus age estimation may be a more scalable route to building same-identity cross-age training data than relying only on existing aging datasets.

This requires separate analysis of:

- Identity false positives
- Age-estimation noise
- Ethical / privacy constraints
- Dataset licensing
- Commercial usage rights
- Demographic balance

---

# 07 Training

## Current Research State

The first-round landscape suggests the future training system may need separate supervision for different failure modes.

Working loss / objective taxonomy:

```text
L_identity
→ Identity Preservation

L_age
→ Target Age Accuracy

L_temporal
→ Frame Consistency

L_landmark / L_geometry
→ Facial Geometry Preservation

L_flow / correspondence
→ Motion / Temporal Alignment

L_reconstruction / source preservation
→ Non-target Region Preservation

L_age_identity_alignment
→ Prevent Identity Conditioning from suppressing target-age behavior
```

These are conceptual roles only. Final losses must be selected after candidate model Deep Analysis and experiments.

## Candidate Training Strategies

- Global aging prior + personalized adaptation
- Few-shot identity-specific fine-tuning
- Age embedding / age classifier guidance
- Factorized aging supervision: texture / soft-tissue / hair / geometry
- Feature-distribution residual construction for factor-specific aging directions
- Global age prior + personalized residual + factorized residual composition
- Identity-conditioning adapters
- Age–Identity alignment objective: preserve target-age behavior after identity injection
- Age-aware identity gating: strong biometric identity + adaptive visual identity
- Temporal feature propagation
- Identity-consistent cross-context pair training
- Optional geometry-guided training

---

# 08 Evaluation

## Current Research State

Visual quality alone is insufficient.

Every serious Re-Aging candidate should eventually be evaluated on:

1. Identity Preservation
2. Age Accuracy / Age Controllability
3. Expression Preservation
4. Pose / Motion Preservation
5. Temporal Consistency
6. Face Geometry Consistency
7. Facial Detail Quality
8. Hair Stability
9. Eye / Teeth Stability
10. Background Preservation
11. Multi-view Consistency
12. Full-body Consistency
13. Training / Inference Cost
14. Reproducibility
15. Production Feasibility

## Failure Taxonomy

Track explicitly:

- Identity Drift
- Face Shape Drift
- Expression Loss
- Temporal Flickering
- Hair Instability
- Teeth Instability
- Eye Instability
- Skin Texture Flicker
- Background Modification
- Age Leakage
- Weak Age Transformation
- Texture-Only Aging
- Soft-Tissue / Shape Aging Suppression
- Exaggerated Aging
- Inconsistent Wrinkles
- Frame-to-Frame Age Variation
- View Inconsistency
- Geometry Inconsistency

---

# 09 Our Re-Aging Architecture

## Current Architecture Direction

**Status:** ENGINEERING HYPOTHESIS — NOT YET VALIDATED

The first-round landscape suggests a staged architecture strategy may reduce technical risk.

### Stage A — Identity-Preserving Image Re-Aging

Target:

```text
Single Image
      ↓
Strong Age Control
+ Strong Identity Preservation
+ Pose / Expression Preservation
      ↓
High-Quality Aged Image
```

Possible conceptual architecture:

```text
FLUX / DiT Backbone
│
├─ Age Branch
│    ├─ Global Age Representation
│    │    └─ TimeMachine-like population age prior / Age Codebook
│    ├─ Personalized Age Residual
│    │    └─ MyTimeMachine-like longitudinal adaptation
│    ├─ Factorized Age Controls
│    │    ├─ Texture / Surface Aging
│    │    ├─ Soft-Tissue / Shape Aging
│    │    ├─ Hair Aging
│    │    └─ optional Geometry Aging
│    └─ Directional Residual Mechanism
│         └─ Aging-Multiverse-inspired feature-distribution residual
│
├─ Identity Branch
│    ├─ PuLID-like Dedicated Identity CA
│    ├─ Age-Invariant Biometric Identity
│    ├─ Rich Visual Identity
│    ├─ IDFormer-style Projection
│    ├─ Age-Aware Identity Gating [HYPOTHESIS]
│    └─ InfiniteYou as comparison candidate
│
└─ Structure / Geometry Branch
     ├─ Landmarks
     ├─ Face Parsing
     └─ optional FLAME / 3DMM
```

Preferred conditioning principle:

```text
Text
Identity
Age
Texture Aging
Soft-Tissue Aging
Geometry
    ↓
Decoupled / Selective Conditioning
```

rather than collapsing all controls into a single monolithic prompt or age embedding.

New identity-conditioning hypothesis after PuLID Deep Analysis:

```text
Age-Invariant Biometric ID
        +
Age-Bearing Visual ID
        ↓
Age-Aware Identity Gating
        +
Dedicated Identity CA
        ↓
Re-Aging DiT
```

Training-side hypothesis:

```text
Age-only behavior
        vs
Age + Identity behavior
        ↓
Age–Identity Alignment
```

Goal:

> Identity conditioning should preserve who the person is without erasing the target-age semantics established by the Age Branch.

Both are **Engineering Hypotheses** and require experiment evidence.

Important:

This is a module map, not a claim that these methods are directly compatible.
Compatibility must be tested experimentally.

---

### Stage B — Video Re-Aging

Target:

```text
Image Re-Aging
      +
Temporal Propagation / Video Diffusion
      +
Video Identity Conditioning
      ↓
Temporally Consistent Video Re-Aging
```

Candidate modules:

```text
Temporal Bridge
→ AnyV2V-like feature propagation

Video Identity
→ ConsisID / Magic Mirror

Subject Consistency
→ Phantom-like conditioning

Motion / Appearance Separation
→ UniEdit-like design principle
```

Primary objective:

> Change age-related appearance while preserving source motion, pose, expression, timing, and identity.

---

### Stage C — 3D-Aware / Full-Body Re-Aging

Potential future direction:

```text
2D / Video Re-Aging
        +
FLAME / 3DMM / Gaussian Head
        +
3DGS / SMPL-X Avatar Representation
        ↓
Geometry-Consistent Re-Aging
```

Possible candidates:

- Gaussian Head Avatar
- SplattingAvatar
- ExAvatar

This stage should remain secondary until Stage A and Stage B requirements are better understood.

---

# Candidate Priority After Landscape Screening

## P0 — Deep Analysis Completed

1. **MyTimeMachine**  
   Personalized aging / longitudinal identity modeling

2. **TimeMachine**  
   Age conditioning / population-level age representation / decoupled age–identity conditioning

3. **Aging Multiverse**  
   Attention-space aging residual / identity–editability mixing / factorized-direction experiment reference

4. **PuLID**  
   Identity-conditioning architecture / DiT identity adapter / Identity–Age experiment candidate

## P0 — Remaining Recommended Deep Analysis

5. **AnyV2V**  
   Image-to-video Re-Aging bridge

6. **ConsisID**  
   Video identity-conditioning module

7. **Phantom + Phantom-Data**  
   Subject consistency + scalable identity-pair dataset construction

## P1 — Secondary Candidates

- SelfAge
- InfiniteYou
- Magic Mirror
- VideoGrain
- UniEdit
- Gaussian Head Avatar
- SplattingAvatar
- ExAvatar

## P2 / Reference

- Identity-Aware Facial Age Editing Using Latent Diffusion
- InstantID
- ReVideo
- GaussianAvatar
- Animatable Gaussians
- Human-VDM
- TokenFlow
- Ground-A-Video

---

# Durable Engineering Conclusions — Landscape Round 1

## Conclusion 1

**Evidence Type:** Architecture Inference / Engineering Hypothesis

There is currently no reason to assume a single available model is sufficient for production-quality Re-Aging.

The stronger research direction is modular:

```text
Age Transformation
        +
Identity Conditioning
        +
Geometry / Structure Preservation
        +
Temporal Consistency
        +
optional 3D / 4D Representation
```

---

## Conclusion 2

**Evidence Type:** Engineering Hypothesis

The preferred development order is currently:

```text
Identity-Preserving Image Re-Aging
        ↓
Video Temporal / Identity Extension
        ↓
3D / 4D Geometry Extension
```

rather than beginning immediately with an end-to-end Video Re-Aging foundation model.

This hypothesis must be validated through implementation experiments.

---

## Conclusion 3

**Evidence Type:** Landscape Observation

Same-identity cross-age data should be treated as a strategic asset, not merely another dataset category.

Potential roles:

- personalized aging
- identity preservation
- age–identity disentanglement
- longitudinal trajectory modeling
- evaluation

---

## Conclusion 4

**Evidence Type:** Engineering Hypothesis

Identity preservation and age controllability should be modeled as partially independent constraints:

```text
Age Branch
→ drives intentional age transformation

Identity Branch
→ limits identity drift
```

The main experimental challenge will be preventing these constraints from suppressing each other.

---

## Conclusion 5

**Evidence Type:** Landscape Observation / Engineering Hypothesis

Video Re-Aging may be achievable initially by combining a strong image Re-Aging model with temporal feature propagation and video identity conditioning, before training a dedicated end-to-end Re-Aging video model.

Primary candidate path:

```text
Image Re-Aging
+ AnyV2V-like Temporal Propagation
+ ConsisID-like Identity Conditioning
```

---


## Conclusion 6

**Evidence Type:** Deep Analysis Result / Architecture Inference

TimeMachine should be treated primarily as an **Age Conditioning architecture reference**, not as the preferred final Re-Aging backbone.

Reusable ideas with the strongest current evidence:

```text
Population-Level Age Representation
+
Dedicated Age Projection
+
Decoupled Age / Identity Conditioning
```

Its ACG component appears secondary based on the reported ablation.

---

## Conclusion 7

**Evidence Type:** Engineering Hypothesis

Aging should be investigated as a **factorized transformation** rather than only a single scalar target-age condition.

Working decomposition:

```text
Texture / Surface Aging
+
Soft-Tissue / Shape Aging
+
Hair Aging
+
Optional Geometry Aging
```

This may improve controllability and reduce the conflict between:

```text
Strong Age Transformation
vs
Identity / Geometry Preservation
```

The hypothesis is not yet validated and requires dedicated model / dataset / evaluation research.

---

## Conclusion 8

**Evidence Type:** Deep Analysis Result / Architecture Inference

Aging Multiverse should be treated primarily as an **attention-space aging residual and feature-mixing reference**, not as a complete or portable Age Representation.

Its reusable contribution is:

```text
Young / Old Feature Distributions
        ↓
Directional Aging Residual
        +
Identity–Editability Feature Mixing
```

The released residual is layer-, timestep-, solver-, and FLUX-specific; portability to another DiT requires re-deriving the representation and injection mechanism.

---

## Conclusion 9

**Evidence Type:** Engineering Hypothesis

The current Age Branch research now supports a three-level formulation:

```text
Global Age Representation
        +
Personalized Age Residual
        +
Factor-Specific Aging Residuals
        ↓
Controllable Re-Aging Condition
```

Current conceptual references:

```text
TimeMachine
→ Global age representation

MyTimeMachine
→ Personalized aging adaptation / residual

Aging Multiverse
→ Directional residual construction / injection
```

This combined architecture is not yet experimentally validated.

---

## Conclusion 10

**Evidence Type:** Deep Analysis Result / Architecture Inference / Engineering Hypothesis

PuLID should be treated primarily as an **Identity Conditioning architecture and experiment candidate**, not as a direct Re-Aging model.

Supported reusable structure:

```text
Biometric Identity
        +
Rich Visual Identity
        ↓
Identity Token Projection
        ↓
Dedicated Identity Cross-Attention
```

Its most important Re-Aging implication is that identity conditioning itself may need to be factorized:

```text
Age-Invariant Identity
        +
Age-Bearing Visual Identity
        ↓
Age-Aware Identity Conditioning
```

The second formulation is an **Engineering Hypothesis**.

Current experiment question:

> Can strong PuLID identity conditioning preserve biometric identity under large age changes without suppressing realized age displacement, Soft-Tissue / Shape Aging, or other legitimate age transformations?

This question is now promoted from literature analysis to `Experiment 01 — PuLID Re-Aging Stress Test`.

---

# Open Problems

1. How should age and identity representations be disentangled without suppressing strong age transformation?
2. Which identity-conditioning method remains stable under large age changes?
3. How much same-identity cross-age data is required for personalized aging?
4. Can generic aging priors and identity-specific aging trajectories coexist in one architecture?
5. How should temporal information be propagated without copying first-frame artifacts across the video?
6. How should wrinkles, skin texture, hair, eyes, and teeth be stabilized frame-to-frame?
7. What geometry representation is sufficient before full 3DGS / 4DGS becomes worthwhile?
8. Can same-identity cross-age datasets be constructed at scale through retrieval + age estimation?
9. How should identity preservation be evaluated when the person's facial geometry legitimately changes with age?
10. What licensing / data restrictions will limit eventual commercial production use?
11. Can aging be factorized into texture, soft-tissue, hair, and geometry controls without creating inconsistent or biologically implausible combinations?
12. What supervision or representation is required to separate high-frequency texture aging from low-/mid-frequency soft-tissue deformation?
13. Can feature-distribution contrasts be used to derive independent ΔTexture / ΔSoftTissue / ΔHair aging directions without introducing semantic leakage between factors?
14. Should factorized aging residuals be injected as model-level condition tokens, attention-space residuals, or both?
15. Which parts of an identity-conditioning representation are truly age-invariant identity, and which parts encode the subject's current age-dependent appearance?
16. Can biometric identity remain strongly conditioned while age-bearing visual identity is selectively relaxed as `|target_age - source_age|` increases?
17. Can an Age–Identity alignment objective preserve target-age semantics after strong identity injection?

---

# Recommended Next Research Task

## Experiment 01 — PuLID Re-Aging Stress Test

**Research Type:** Experiment  
**Status:** DESIGNED  
**Source Research:** Deep Analysis 04 — PuLID

Research objective:

> Measure the Identity–Age trade-off of stock PuLID under progressively larger Re-Aging transformations and determine whether PuLID should be promoted, modified with Age-Aware Identity Conditioning, or downgraded to an architecture reference.

Primary hypotheses:

### H1 — Identity Strength vs Age Editability

```text
Identity Conditioning Strength ↑
        ↓
Identity Similarity ↑

but potentially

Realized Age Transformation ↓
```

### H2 — Identity Injection Timing

```text
Earlier / stronger Identity Injection
        ↓
Higher Identity Preservation
        +
Lower Age Editability
```

### H3 — Visual Identity Age Leakage

```text
Rich Visual Identity Features
        ↓
may carry more source-age appearance

than

Biometric Identity Features
```

H3 remains an **Experiment Hypothesis** and should not be treated as established fact.

Phase A:

```text
Inference Only
No Retraining
No Architecture Modification

No PuLID
    vs
Stock PuLID
```

Primary sweep:

```text
Age Gap
×
Identity Strength
×
Identity Insertion Start
×
Repeated Seeds
```

Primary outputs:

- Identity Preservation
- Target Age Accuracy
- Realized Age Displacement
- Identity–Age Pareto Curve
- Re-Aging Failure Tags

Key failure cases:

- Identity Drift
- Weak Age Transformation
- Texture-Only Aging
- Soft-Tissue / Shape Aging Suppression
- Face Shape Drift
- Expression Loss
- Hair Age Leakage

Experiment readiness:

```text
Current:
DESIGNED

Next:
IMPLEMENTATION-READY
```

Before execution, fix:

- repository / exact commit
- checkpoint
- environment
- dataset manifest
- parameter sweep
- independent identity evaluator(s)
- age evaluator(s)
- seeds
- exact commands
- reproducibility record

Decision outcomes:

```text
Useful Identity–Age Pareto region
→ Promote PuLID as stronger Architecture Candidate

Identity improves but Age Transformation collapses
→ Investigate Age-Aware Identity Conditioning

No useful balance after stock controls
→ Downgrade PuLID to Architecture Reference
```

---

# Current Research Lifecycle Snapshot

```text
LANDSCAPE ROUND 1
        ↓
SCREENING COMPLETED
        ↓
P0 CANDIDATES IDENTIFIED
        ↓
MyTimeMachine — DEEP ANALYSIS COMPLETED
        ↓
TimeMachine — DEEP ANALYSIS COMPLETED
        ↓
Aging Multiverse — DEEP ANALYSIS COMPLETED
        ↓
PuLID — DEEP ANALYSIS COMPLETED
        ↓
ARCHITECTURE / EXPERIMENT CANDIDATE
        ↓
Experiment 01 — PuLID Re-Aging Stress Test
        ↓
DESIGNED
        ↓
NEXT: IMPLEMENTATION-READY
```