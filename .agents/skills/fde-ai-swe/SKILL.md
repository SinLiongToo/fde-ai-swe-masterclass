---
name: fde-ai-swe
description: >-
  Forward Deployed Engineer (FDE) and AI Software Engineering playbook. Use when
  architecting, implementing, or auditing enterprise AI systems, Spec-Driven Development
  with Pydantic contracts, LangGraph state machine agents with durable checkpointing,
  PostgreSQL pgvector two-stage hybrid RAG pipelines, continuous CI/CD evaluation gates
  (Ragas/LangSmith), and authoring reusable agent skills with progressive disclosure.
---

# Forward Deployed Engineer (FDE) & AI Systems Playbook

This skill provides operational standards, architecture decision records (ADRs), and production implementation patterns for operating as an elite **Forward Deployed Engineer (FDE)** and modern **AI Systems Orchestrator**.

---

## 🏛️ 1. Core Competency Triad (40 / 35 / 25 Rule)

An elite FDE balances three distinct superpowers:
1. **Production Systems Engineering (40%)**:
   - Distributed systems, Docker/Kubernetes container orchestration, PostgreSQL (ACID), Redis caching, OAuth/OIDC identity, latency budgeting, and resilient CI/CD pipelines.
2. **Applied AI & Data Architecture (35%)**:
   - Advanced RAG (dense + sparse hybrid search), vector embeddings, DSPy teleprompter optimization, quantitative model evaluations (Evals), and token economics governance.
3. **Client Discovery & Empathy (25%)**:
   - Translating ambiguous stakeholder goals into crisp engineering SLAs, rapid prototyping (72h PoC), and production handover (45-60 days).

---

## 📐 2. The 5 Production Architectural Blueprints

### Blueprint 1: Spec-Driven Development & Schema Contracts
- **Rule**: Never rely on unconstrained natural language prompts for structured outputs.
- **Pattern**: Finite-State Machine (FSM) grammar-constrained decoding via `Instructor` or `Outlines` combined with `Pydantic v2`.
- **Validation**:
  - Strict field boundaries (`ge`, `le`, `min_length`, regex patterns).
  - Business invariant validators using `@field_validator` with prohibited lazy tokens (`"tbd"`, `"n/a"`).
  - Automatic error traceback reflection with `max_retries=3`.
- **Target SLA**: Schema parse failure rate = **0.00%**.

### Blueprint 2: Cyclical State Machine Agents (LangGraph)
- **Rule**: Avoid brittle linear DAG pipelines; model complex workflows as cyclical state graphs $(V, E)$.
- **Components**:
  - **Typed State**: Immutable state schema with typed messages, flags, and iteration counters.
  - **State Persistence**: Durable checkpointing via `PostgresSaver` / `MemorySaver` for 100% replayability.
  - **Human-in-the-Loop (HITL)**: Conditional router that intercepts destructive database mutations (`INSERT`, `UPDATE`, `DELETE`, `DROP`) and pauses execution for human authorization.
  - **Safety Valve**: Enforce `recursion_limit <= 15` to prevent runaway token spend.

### Blueprint 3: Enterprise 2-Stage Hybrid RAG Engine
- **Rule**: Pure vector (dense) search fails on exact serials, part numbers, and compliance codes. Always deploy Hybrid Search with Reciprocal Rank Fusion.
- **Pipeline**:
  1. **Dual Ingestion**: Parent-child document chunking with 1536d dense vectors + PostgreSQL `tsvector` lexemes.
  2. **Stage 1 (Parallel Coarse Retrieval, < 18ms)**:
     - HNSW index cosine similarity search ($m=16, ef\_construction=64$) for Top 30 semantic chunks.
     - GIN index BM25 search for Top 30 exact keyword chunks.
  3. **Reciprocal Rank Fusion (RRF, $k=60$)**:
     $$RRF(d) = \sum_{m \in M} \frac{1}{60 + r_m(d)}$$
  4. **Stage 2 (Cross-Encoder Re-ranking, < 45ms)**:
     - BGE-Reranker-Large or Cohere Rerank computes global query-context cross-attention to select Top 5.
- **Target SLA**: Recall@5 >= **94%**, Total retrieval latency < **85ms**.

### Blueprint 4: Continuous CI/CD Evaluation Gates
- **Rule**: Replace subjective manual "vibe checks" with automated statistical evaluation suites executed on every Pull Request.
- **Mathematical Metrics**:
  - **Faithfulness (Grounding)**: $F = \frac{|V|}{|S|} \ge 0.92$ (verified claims vs total claims).
  - **Context Recall**: $\ge 0.90$ (coverage of reference ground-truth).
  - **Answer Relevance**: $\ge 0.88$ (cosine similarity of synthesized questions).
- **Gate Enforcement**: Fail CI/CD build (`pytest.exit(1)`) if any metric regresses below SLA.

### Blueprint 5: Agent Skill Engineering & Progressive Disclosure
- **Rule**: Do not dump 50-page enterprise runbooks into system prompts. Package procedural workflows into reusable Antigravity Skills.
- **Skill Architecture**:
  - `SKILL.md` with YAML frontmatter (`name`, `description`).
  - **Progressive Disclosure**: Only the name and brief description are indexed in memory; full operational body is loaded on-demand when relevant.
  - **Deterministic Tools**: Python CLI subcommands executed via `uv run` with file-lock rate limiters.

---

## ⚡ 3. 5-Stage Production Delivery Protocol

| Stage | Timeline | Primary Objective | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **01. Discovery** | Days 1–3 | Translate vague pain points to architecture | ADR + Target SLA Contract (Latency < 2.5s, Hallucination < 1%) |
| **02. Data Hygiene** | Days 4–10 | Unstructured ETL & Golden Benchmark | Repeatable ETL pipeline + 50–100 Golden Ground-Truth Eval pairs |
| **03. Rapid PoC** | Days 11–20 | 5x speed prototype development | FastAPI + LangGraph state machine + Interactive Generative UI |
| **04. Hardening** | Days 21–35 | Observability, Guardrails & Security | LangSmith/Phoenix telemetry, PII filters, CI/CD automated eval gate |
| **05. Production** | Days 36–45 | Zero-downtime deployment & handover | Terraform/Helm Kubernetes deployment, runbooks, client enablement |

---

## 📋 4. FDE PR Verification Checklist

Before approving or merging any enterprise AI system PR:
- [ ] **Schema Conformance**: All structured LLM calls use Pydantic models with constrained decoding.
- [ ] **Rate Limiting & Retries**: All external model/API calls implement exponential backoff with jitter.
- [ ] **Observability**: Every chain/agent execution logs tokens, latency, prompt version, and model ID to an evaluation telemetry backend.
- [ ] **Guardrails**: Input PII sanitization and prompt injection checks are active at the API gateway.
- [ ] **CI Regression Test**: PR passes the automated Golden Dataset evaluation suite with zero regression.
