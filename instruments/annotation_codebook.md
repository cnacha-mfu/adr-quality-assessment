# ADR Quality Annotation Codebook

## 1. Purpose and Scope

This codebook provides detailed instructions for annotating Architectural Decision Record (ADR) quality using a validated 10-dimension quality model. The annotation produces per-dimension scores on a 4-point scale that serve as the ground truth for evaluating automated LLM-based quality assessment.

**Target corpus**: Student-written ADRs from software architecture courses (2024–2025 cohorts), following loose MADR template conventions.

**Annotation unit**: One complete ADR document = one annotation instance.

## 2. Annotator Requirements

- Software architecture expertise (graduate-level coursework or professional experience)
- Familiarity with MADR template and ADR conventions
- Completion of calibration training (minimum 2 pilot rounds)

## 3. Annotation Procedure

### 3.1 Per-ADR Workflow

1. **Read the entire ADR** from start to finish before rating any dimension. Do not rate during the first read.
2. **Rate each dimension independently** using the 4-point scale defined below. Rate dimensions in order A1→A2→B1→B2→B3→B4→B5→C1→C2→C3.
3. **Record a confidence score** (1–3) for each rating: 1 = uncertain, 2 = moderately confident, 3 = confident.
4. **Write brief notes** for any rating where you deviate from the most obvious interpretation, or where the ADR presents a boundary case.
5. **Do not** consult other annotators' ratings during independent annotation.

### 3.2 General Guidelines

- **Rate what is written, not what was intended.** If context is implied but not stated, score based on what is explicitly present.
- **Student context**: These are student assignments, not production ADRs. Calibrate expectations accordingly, but still apply the rubric consistently. A score of 4 should represent genuinely excellent work by student standards.
- **Code sections**: Sample code sections should NOT influence quality ratings (they are supplementary material, not part of the decision record itself).
- **Language quality**: Many ADRs may be written by non-native English speakers. Rate clarity of communication, not grammatical perfection. If the meaning is clear despite grammatical errors, do not penalize heavily.
- **Length**: Neither length nor brevity alone determines quality. A concise, well-structured ADR can score 4; a verbose, unfocused ADR may score 2.

## 4. Quality Dimensions and Scoring Scale

All dimensions use a **4-point anchored Likert scale** (1 = Poor, 2 = Needs Improvement, 3 = Good, 4 = Excellent). The 4-point scale (no midpoint) forces discrimination and avoids central tendency bias.

---

### A. STRUCTURAL QUALITY

#### A1 — Completeness

**Definition**: All relevant MADR sections are present and filled with substantive content.

| Score | Label | Description |
|-------|-------|-------------|
| 1 | Severely incomplete | Missing two or more mandatory sections. The record cannot function as a decision record. |
| 2 | Partially complete | All mandatory sections present but at least two are trivially short (one sentence or placeholder). Optional sections largely absent. |
| 3 | Substantially complete | All mandatory sections with substantive content. At least two optional sections included. |
| 4 | Fully complete | All mandatory and relevant optional sections present with detailed content. Nothing material missing. |

**Mandatory sections**: Context/Problem Statement, Decision, Rationale (or justification embedded in Decision)
**Optional sections**: Decision Drivers, Considered Options/Alternatives, Consequences (Pros/Cons), Confirmation, Links/References

**Boundary cases**:
- If rationale is embedded within the Decision section (e.g., "We chose X because..."), count it as present for mandatory purposes.
- A "Sample Code" section does not count toward completeness—it is supplementary.
- "TBD" or placeholder text counts as absent.

---

#### A2 — Structural Conformance

**Definition**: Adherence to a recognized ADR template format with correct headings, consistent ordering, and metadata.

| Score | Label | Description |
|-------|-------|-------------|
| 1 | No recognizable structure | Free-form text, no headings or sections. |
| 2 | Minimal structure | Some headings but inconsistent hierarchy, missing key labels, or non-standard ordering. No metadata. |
| 3 | Good structure | Recognizable template with consistent headings. Minor issues (missing metadata, slight ordering deviations). |
| 4 | Exemplary structure | Strict template adherence, correct heading hierarchy, metadata present, proper markdown formatting. |

**Boundary cases**:
- ADRs that use non-MADR but internally consistent templates (e.g., Context/Issue/Decision/Solution) can score 3 if the structure is logical and consistent.
- Inconsistent heading levels (e.g., jumping from H1 to H3) should reduce score by at least 1 point.

---

### B. CONTENT QUALITY

#### B1 — Context Adequacy

**Definition**: Clarity and sufficiency of the problem statement, including architectural significance and decision drivers.

| Score | Label | Description |
|-------|-------|-------------|
| 1 | Missing or trivial | No context section, or a single vague sentence. No drivers. |
| 2 | Generic | Problem stated generically without project-specific details. Drivers implicit or absent. |
| 3 | Adequate | Clear problem with project-specific details. At least two drivers identified. Reader understands why a decision is needed. |
| 4 | Rich | Thorough description with architectural significance, multiple prioritized drivers, and stated assumptions. |

**Boundary cases**:
- If drivers are listed in a separate "Decision Drivers" section, credit them for B1 even if the Context section itself is brief.
- Generic statements like "We need a database" score 1; "We need a database to store user profiles for our e-commerce app" scores 2.

---

#### B2 — Alternatives Coverage

**Definition**: Number, diversity, and feasibility of options considered.

| Score | Label | Description |
|-------|-------|-------------|
| 1 | No alternatives | Only one option presented with no alternatives discussed. |
| 2 | Superficial | Two or more alternatives listed but with minimal description or trivially similar. |
| 3 | Adequate | Two or more genuinely distinct alternatives with sufficient description. |
| 4 | Thorough | Three or more well-described alternatives with systematic evaluation against drivers. |

**Boundary cases**:
- If the ADR structure discusses only a "Decision" without explicit "Considered Options" but mentions why other approaches were rejected, count those as implicitly considered alternatives. Score 2 minimum.
- The "status quo" / "do nothing" counts as a valid alternative.

---

#### B3 — Rationale Depth

**Definition**: Quality of justification linking the decision to drivers and acknowledging tradeoffs.

| Score | Label | Description |
|-------|-------|-------------|
| 1 | No rationale | No reasoning, or only assertion ("it is the best"). |
| 2 | Shallow | Generic reasons not tied to project context. No tradeoff discussion. |
| 3 | Adequate | References specific drivers, acknowledges at least one tradeoff. Reader understands why this option over alternatives. |
| 4 | Exemplary | Deep tradeoff analysis, evidence cited, clear explanation of why alternatives rejected. |

**Boundary cases**:
- Listing bullet-point features of the chosen technology without explaining why they matter for the project is a score of 2.
- "Because-clauses" can be implicit if the logical connection is clear (e.g., "Driver 1 is latency; gRPC benchmarks at 8ms" implicitly connects).

---

#### B4 — Consequence Specificity

**Definition**: Concrete articulation of both positive and negative consequences.

| Score | Label | Description |
|-------|-------|-------------|
| 1 | No consequences | Consequences section absent or empty. |
| 2 | Vague | Generic consequences ("better performance", "learning curve"). Only pros or only cons. |
| 3 | Adequate | Both pros and cons with some project-specific detail. At least two concrete consequences. |
| 4 | Detailed | Comprehensive, project-specific consequences with quantified impacts and mitigation strategies. |

**Boundary cases**:
- If pros/cons are embedded within the Rationale rather than a separate section, still credit them for B4.
- Mislabeled sections (e.g., "Cros" instead of "Cons" as observed in dataset) should be interpreted charitably—rate the content, not the label.

---

#### B5 — Decision Specificity

**Definition**: How concrete, actionable, and unambiguous the chosen option is stated.

| Score | Label | Description |
|-------|-------|-------------|
| 1 | Unclear | No clear decision, or decision is ambiguous. Reader cannot determine what was decided. |
| 2 | Vague | Decision stated but without enough specificity to act on (e.g., "We will use a modern framework"). |
| 3 | Clear | Specific option identified. Scope mostly clear. |
| 4 | Precise | Specific technology/version, scope boundaries, status indicated. Developer could act immediately. |

---

### C. DOCUMENTATION QUALITY

#### C1 — Clarity and Readability

**Definition**: Language quality, logical flow, and editorial polish.

| Score | Label | Description |
|-------|-------|-------------|
| 1 | Poor | Numerous errors, unclear sentences, incoherent structure. Significant effort to understand. |
| 2 | Below average | Understandable but with noticeable issues, awkward phrasing, or disjointed flow. |
| 3 | Good | Clear, professional language. Minor issues don't impede understanding. |
| 4 | Excellent | Well-written, concise, polished. Could serve as exemplar. |

**Note**: Rate communication effectiveness, not native-speaker fluency. If meaning is clear despite grammatical imperfections, that supports a score of 3.

---

#### C2 — Consistency

**Definition**: No internal contradictions, uniform terminology, alignment between drivers and evaluation.

| Score | Label | Description |
|-------|-------|-------------|
| 1 | Significant contradictions | Clear contradictions between sections. Decision doesn't follow from analysis. |
| 2 | Minor inconsistencies | No major contradictions but some misalignment between drivers and evaluation. |
| 3 | Mostly consistent | Consistent terminology, decision follows from analysis. Minor variations acceptable. |
| 4 | Fully consistent | Perfect alignment. Drivers explicitly referenced in evaluation. Document reads as coherent whole. |

---

#### C3 — Traceability

**Definition**: Explicit links to requirements, related ADRs, and external references.

| Score | Label | Description |
|-------|-------|-------------|
| 1 | No traceability | No references to any artifacts. ADR in complete isolation. |
| 2 | Minimal | One or two generic references (e.g., link to official docs) without internal project links. |
| 3 | Adequate | External documentation references and at least one internal link. |
| 4 | Comprehensive | Rich links: related ADRs, requirements, benchmarks, affected components. |

**Note for student ADRs**: Students may have limited traceability opportunities (no existing ADR corpus to reference). Evaluate relative to what is reasonable. External documentation links and identification of affected components are achievable and should be expected.

---

## 5. Recording Format

Use the provided spreadsheet with the following columns per ADR:

| Column | Description |
|--------|-------------|
| `adr_id` | Unique identifier (filename) |
| `cohort` | Year (2024 or 2025) |
| `annotator` | Annotator identifier (A1, A2, or ADJ) |
| `A1_score` | Completeness (1-4) |
| `A1_confidence` | Confidence (1-3) |
| `A1_notes` | Free-text notes |
| ... | (Repeat for A2, B1-B5, C1-C3) |
| `overall_notes` | General observations about the ADR |
| `timestamp` | Date/time of annotation |

## 6. Calibration Protocol

### Round 1 (15-20 ADRs)
1. Both annotators independently score the calibration set
2. Compute preliminary Krippendorff's alpha (ordinal)
3. Hold calibration meeting: discuss every disagreement (≥2-point difference first, then ±1 differences)
4. Revise codebook if definitions are ambiguous
5. Target: α ≥ 0.60

### Round 2 (15-20 new ADRs)
1. Apply revised codebook independently
2. Compute Krippendorff's alpha
3. Discuss remaining disagreements
4. Target: α ≥ 0.67

### Round 3 (if needed, 15-20 new ADRs)
1. Apply final codebook
2. Target: α ≥ 0.80
3. If specific dimensions consistently produce low agreement, consider simplifying scale or merging dimensions

## 7. Disagreement Resolution

For the full annotation phase:
- Both primary annotators (A1, A2) annotate every ADR independently
- Disagreements of ≥2 points on any dimension are flagged for adjudication
- Adjudicator (ADJ) reviews the ADR and both annotations
- Final score determined by consensus discussion among all three annotators
- If no consensus, adjudicator's score is final

## 8. Inter-Rater Reliability Metrics

Report the following after full annotation:

1. **Krippendorff's alpha (ordinal)** — primary metric, per-dimension and overall
2. **Quadratic weighted Cohen's kappa** — pairwise between annotators
3. **ICC(2,1) for absolute agreement** — with 95% bootstrap CI (10,000 resamples)
4. **Exact agreement %** — percentage of identical scores
5. **Adjacent agreement %** — percentage within ±1 point
6. **Confusion matrices** — per dimension, showing score distribution patterns

## 9. Data Management

- Store annotations in CSV format (one row per ADR per annotator)
- Back up daily to shared cloud storage
- ADR content is student work: handle per institutional data policy
- De-identify ADRs before sharing outside the research team (remove student names if present)
- Maintain an audit trail of codebook revisions with dates and rationale
