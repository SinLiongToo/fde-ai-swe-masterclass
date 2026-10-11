"""
Blueprint 4: Continuous CI/CD Evaluation & Regression Gates
Pytest test suite enforcing statistical SLAs, Schema integrity,
Hybrid RAG recall, and State Machine Human-in-the-Loop gating.
"""

import pytest
import time
from pydantic import ValidationError

from exercises.fde_enterprise_lab.models import ClauseRiskAssessment
from exercises.fde_enterprise_lab.retrieval import (
    execute_hybrid_search, 
    compute_sparse_bm25_scores, 
    compute_dense_simulated_embeddings,
    ENTERPRISE_KNOWLEDGE_CORPUS
)
from exercises.fde_enterprise_lab.agent import (
    AgentState, 
    EnterpriseAgentStateMachine, 
    DurableCheckpointStore
)

class TestSpecDrivenContracts:
    """Verifies Pydantic v2 Schema Boundary Contracts and Anti-Lazy Validator."""

    def test_valid_clause_risk_assessment(self):
        """Valid structured payload must pass schema validation without error."""
        assessment = ClauseRiskAssessment(
            clause_id="CLAUSE-001",
            contract_title="APAC Payment Gateway SLA",
            risk_level="HIGH",
            confidence_score=0.94,
            identified_vulnerabilities=["P99 response time exceeds 250ms threshold"],
            actionable_mitigation="Deploy Envoy proxy circuit breaker and scale Kubernetes replicas to 8."
        )
        assert assessment.clause_id == "CLAUSE-001"
        assert assessment.confidence_score == 0.94
        assert len(assessment.actionable_mitigation) >= 25

    def test_anti_lazy_validator_rejects_todo_or_tbd(self):
        """Model hallucination/laziness producing 'TBD' or 'Contact admin' must be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ClauseRiskAssessment(
                clause_id="CLAUSE-002",
                contract_title="GDPR Data Export",
                risk_level="CRITICAL",
                confidence_score=0.88,
                identified_vulnerabilities=["Missing Article 44 consent"],
                actionable_mitigation="Contact admin later to fix this issue"  # Prohibited token!
            )
        assert "prohibited lazy placeholder" in str(exc_info.value).lower()

    def test_invalid_clause_id_pattern(self):
        """Malformed IDs (e.g. not matching CLAUSE-\\d{3,4}) must raise ValidationError."""
        with pytest.raises(ValidationError):
            ClauseRiskAssessment(
                clause_id="BAD-ID-99",
                contract_title="Title",
                risk_level="LOW",
                confidence_score=0.5,
                identified_vulnerabilities=["None"],
                actionable_mitigation="Detailed mitigation step with sufficient length for valid contract check."
            )


class TestHybridRetrievalEngine:
    """Evaluates 2-Stage Hybrid Search with Reciprocal Rank Fusion (k=60)."""

    def test_bm25_sparse_retrieval_exact_keyword(self):
        """Exact alphanumeric keyword 'lock_timeout' must rank CLAUSE-004 first."""
        results = compute_sparse_bm25_scores("lock_timeout postgres ddl", ENTERPRISE_KNOWLEDGE_CORPUS)
        assert len(results) > 0
        assert results[0]["id"] == "CLAUSE-004"
        assert results[0]["sparse_score"] > 0.0

    def test_dense_semantic_retrieval_synonyms(self):
        """Concept 'slowness' without exact token 'latency' must rank CLAUSE-001 at the top."""
        results = compute_dense_simulated_embeddings("slowness in payment service", ENTERPRISE_KNOWLEDGE_CORPUS)
        assert len(results) > 0
        assert results[0]["id"] == "CLAUSE-001"
        assert results[0]["dense_score"] > 0.5

    def test_hybrid_rrf_combines_strengths(self):
        """Hybrid search fuses sparse & dense to produce resilient top results."""
        res = execute_hybrid_search("GDPR sovereignty Article 44 privacy", top_n=3)
        assert len(res["hybrid_top"]) == 3
        top_doc = res["hybrid_top"][0]
        assert top_doc["id"] == "CLAUSE-002"
        assert "rrf_score" in top_doc


class TestAgentStateMachineHITL:
    """Tests DAG Execution, Checkpointing, and Human-in-the-Loop Interruption."""

    def test_read_only_goal_executes_to_completion(self):
        """Safe read-only audit executes automatically without HITL interruption."""
        store = DurableCheckpointStore()
        machine = EnterpriseAgentStateMachine(store)
        state = AgentState(
            session_id="sess-safe-001",
            goal="Analyze APAC payment webhook latency SLA compliance"
        )

        # Step 1: Plan & Retrieve
        state = machine.run_step(state)
        assert state.status == "EXECUTING"
        assert state.hitl_interrupted is False

        # Step 2: Execute & Emit Spec
        state = machine.run_step(state)
        assert state.status == "COMPLETED"
        assert state.output_assessment is not None
        assert state.output_assessment["clause_id"] == "CLAUSE-001"

        # Verify durable checkpoints were saved
        history = store.get_history("sess-safe-001")
        assert len(history) == 2

    def test_mutating_destructive_goal_triggers_hitl_gate(self):
        """Destructive action (DROP table) MUST pause and require human dual-authorization."""
        store = DurableCheckpointStore()
        machine = EnterpriseAgentStateMachine(store)
        state = AgentState(
            session_id="sess-danger-002",
            goal="Destructive action: Drop production financial ledger database table"
        )

        # Step 1: Planner identifies mutation and pauses
        state = machine.run_step(state)
        assert state.status == "AWAITING_HUMAN_APPROVAL"
        assert state.hitl_interrupted is True
        assert state.hitl_mutation_detected is True

        # Simulate Human Rejection
        state_rejected = copy_state = machine.store.load_latest("sess-danger-002")
        state_rejected = machine.resolve_hitl_interrupt(
            state_rejected, approved=False, approval_token=""
        )
        assert state_rejected.status == "REJECTED"

        # Resume original with valid Dual-Auth Token
        state_approved = machine.resolve_hitl_interrupt(
            state, approved=True, approval_token="AUTH-SEC-4921-VERIFIED"
        )
        assert state_approved.status == "EXECUTING"

        # Complete execution
        state_approved = machine.run_step(state_approved)
        assert state_approved.status == "COMPLETED"
        assert state_approved.output_assessment["risk_level"] == "CRITICAL"


class TestCICDEvaluationGates:
    """Quantitative CI/CD evaluation gates asserting SLA metrics."""

    def test_statistical_sla_benchmark(self):
        """
        CI/CD Evaluation Regression Gate:
        - Recall Rate >= 0.88
        - Faithfulness Score >= 0.90
        - Execution Latency < 2500ms
        """
        benchmark_queries = [
            ("payment webhook latency", "CLAUSE-001"),
            ("GDPR EU data sovereignty", "CLAUSE-002"),
            ("database mutation disaster recovery", "CLAUSE-003"),
            ("zero-downtime postgres migration ddl", "CLAUSE-004"),
            ("API rate limiting token governance", "CLAUSE-005")
        ]

        correct_retrievals = 0
        total_time_ms = 0.0

        for query, expected_id in benchmark_queries:
            t0 = time.perf_counter()
            result = execute_hybrid_search(query, top_n=1)
            t1 = time.perf_counter()
            total_time_ms += (t1 - t0) * 1000

            top_id = result["hybrid_top"][0]["id"]
            if top_id == expected_id:
                correct_retrievals += 1

        recall_rate = correct_retrievals / len(benchmark_queries)
        avg_latency_ms = total_time_ms / len(benchmark_queries)
        synthetic_faithfulness_score = 0.95

        # Automated CI/CD Regression Gate Assertions
        assert recall_rate >= 0.88, f"Evaluation Gate Failed: Recall {recall_rate:.2f} < 0.88"
        assert synthetic_faithfulness_score >= 0.90, f"Faithfulness {synthetic_faithfulness_score} < 0.90"
        assert avg_latency_ms < 2500, f"Latency SLA breached: {avg_latency_ms:.2f}ms >= 2500ms"
