# 🧪 FDE Enterprise Hands-on Exercise Lab
> **Real-world Hands-on Implementation of Forward Deployed Engineering (FDE) & AI Software Engineering Blueprints**

Welcome to the **FDE Enterprise Lab**. This laboratory project provides complete, self-contained, enterprise-grade Python implementations for the four cornerstone disciplines of modern AI Software Engineering:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FDE ENTERPRISE LAB ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Spec-Driven Contracts ──▶ 2. 2-Stage Hybrid RAG ──▶ 3. State Machine DAG │
│    (Pydantic v2 Models)        (BM25 + Dense + RRF)       (HITL Mutation)   │
│                                                                   │         │
│ 4. CI/CD Evaluation Gates ◀───────────────────────────────────────┘         │
│    (Pytest Statistical SLA Verification)                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```text
exercises/fde_enterprise_lab/
├── __init__.py
├── models.py           # Milestone 1: Pydantic v2 Spec Contracts & Anti-Lazy Gate
├── retrieval.py        # Milestone 2: 2-Stage Hybrid RAG (Dense + BM25 + RRF k=60)
├── agent.py            # Milestone 3: Cyclical State Machine DAG with Checkpoints & HITL
├── test_eval_gate.py   # Milestone 4: Continuous CI/CD Automated Evaluation Suite
├── main.py             # Interactive CLI Terminal Exercise Runner
└── README.md           # This comprehensive exercise guide
```

---

## 🚀 Quickstart: Running the Exercise

### 1. Run the Interactive CLI Exercise Runner
Experience all 4 milestones sequentially in your terminal with formatted tables, inspection logs, and state transitions:

```bash
python -m exercises.fde_enterprise_lab.main
```

### 2. Run the Automated CI/CD Evaluation Test Gates
Verify regression gates, quantitative statistical SLAs, and state machine transitions using `pytest`:

```bash
python -m pytest exercises/fde_enterprise_lab/test_eval_gate.py -v
```

---

## 🎯 The 4 Lab Milestones & Concepts

### Milestone 1: Spec-Driven Development & Anti-Lazy Contracts (`models.py`)
* **Core Philosophy**: Large Language Models must never output freeform, untyped strings to downstream enterprise APIs or database drivers.
* **Implementation Details**:
  * `ClauseRiskAssessment`: Pydantic v2 model with regex patterns (`^CLAUSE-\d{3,4}$`), bounded confidence scores (`0.0 <= score <= 1.0`), and non-empty list constraints.
  * `@field_validator("actionable_mitigation")`: **Anti-Hallucination Gate**. Intercepts lazy and evasive placeholders (such as `"TBD"`, `"TODO"`, `"contact admin"`) at runtime before they can pollute audit ledgers.

### Milestone 2: 2-Stage Hybrid Retrieval Engine (`retrieval.py`)
* **Core Philosophy**: Dense semantic embeddings excel at synonym concepts (e.g., *"slowness"* $\rightarrow$ *"latency"*) but fail on exact technical identifiers (e.g., `"Article 44"`, `"lock_timeout"`). BM25 lexical search provides exact keyword precision.
* **Implementation Details**:
  * Parallel sparse BM25 scoring + dense semantic vector matching.
  * **Reciprocal Rank Fusion (RRF $k=60$)**: Combines reciprocal ranks across modalities to deliver robust retrieval precision:
    $$\text{RRF}(d) = \sum_{m \in M} \frac{1}{k + \text{rank}_m(d)}$$

### Milestone 3: Cyclical State Machine & Human-in-the-Loop Gate (`agent.py`)
* **Core Philosophy**: Never deploy autonomous agents that can execute irreversible database mutations (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`) without human oversight and durable state recovery.
* **Implementation Details**:
  * `AgentState`: Explicit typed execution state with durable checkpointing (simulating PostgreSQL checkpoint stores).
  * `EnterpriseAgentStateMachine`: Cyclical DAG with a security analyzer node.
  * **HITL Interrupt Gate**: Automatically suspends execution when mutating SQL or destructive actions are proposed (`AWAITING_HUMAN_APPROVAL`), requiring a cryptographically formatted dual-authorization token (`AUTH-SEC-...`) to resume.

### Milestone 4: CI/CD Quantitative Evaluation & Regression Gates (`test_eval_gate.py`)
* **Core Philosophy**: AI systems require continuous statistical evaluation gates in pull-request pipelines to prevent model drift and accuracy regression.
* **Implementation Details**:
  * `test_statistical_sla_benchmark`: Asserts quantitative thresholds on a golden evaluation dataset:
    * **Retrieval Recall**: $\ge 88.0\%$
    * **Faithfulness Score**: $\ge 90.0\%$
    * **P99 Latency SLA**: $< 2,500\text{ ms}$

---

## 🛠️ Hands-on Challenges for You

Try modifying the code to complete these real-world exercises:

1. **Challenge 1 (Schema Defense)**: Open `models.py` and add a new validator that requires `actionable_mitigation` to contain at least one concrete SRE keyword (such as `"replica"`, `"cache"`, `"circuit breaker"`, or `"timeout"`).
2. **Challenge 2 (Retrieval Expansion)**: Open `retrieval.py`, add a new policy document for *"PCI-DSS Tokenization Standard"*, and verify that both BM25 and Hybrid RRF correctly retrieve it.
3. **Challenge 3 (Custom HITL Gate)**: Open `agent.py` and add an auto-quarantine rule that blocks queries attempting cross-border EU personal data transfers without explicit GDPR Article 49 derogation.
4. **Challenge 4 (CI/CD Regression Guard)**: Add a test case in `test_eval_gate.py` that verifies the agent halts gracefully when `max_steps` is exceeded, preventing runaway token expenditure loops.
