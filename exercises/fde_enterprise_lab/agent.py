"""
Blueprint 2: Cyclical State Machine Agent with Human-in-the-Loop (HITL) Gate
Implements state persistence, durable checkpointing, and deterministic mutation interrupts.
"""

from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass, field, asdict
import json
import copy

from .models import ClauseRiskAssessment
from .retrieval import execute_hybrid_search

@dataclass
class AgentState:
    session_id: str
    goal: str
    status: Literal["INIT", "PLANNING", "AWAITING_HUMAN_APPROVAL", "EXECUTING", "COMPLETED", "REJECTED", "HALTED"] = "INIT"
    step_count: int = 0
    max_steps: int = 6
    retrieved_contexts: List[Dict[str, Any]] = field(default_factory=list)
    pending_actions: List[Dict[str, Any]] = field(default_factory=list)
    executed_actions: List[Dict[str, Any]] = field(default_factory=list)
    hitl_interrupted: bool = False
    hitl_mutation_detected: bool = False
    approval_token: Optional[str] = None
    output_assessment: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    audit_trail: List[str] = field(default_factory=list)

class DurableCheckpointStore:
    """Simulates PostgreSQL durable checkpoint storage for resilient agent resumes."""
    def __init__(self):
        self._checkpoints: Dict[str, List[Dict[str, Any]]] = {}

    def save(self, session_id: str, state: AgentState):
        if session_id not in self._checkpoints:
            self._checkpoints[session_id] = []
        serialized = copy.deepcopy(asdict(state))
        self._checkpoints[session_id].append(serialized)

    def load_latest(self, session_id: str) -> Optional[AgentState]:
        history = self._checkpoints.get(session_id, [])
        if not history:
            return None
        data = copy.deepcopy(history[-1])
        return AgentState(**data)

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        return self._checkpoints.get(session_id, [])

class EnterpriseAgentStateMachine:
    """
    Cyclical Directed Acyclic Graph (DAG) State Machine with Human-in-the-Loop Safeguards.
    Graph Topology:
    [START] -> [PLANNER] -> [HYBRID_RETRIEVAL] -> [SECURITY_ANALYZER]
                                                       |
                                 +---------------------+---------------------+
                                 | (Mutating / High-Risk)                    | (Read-Only)
                                 v                                           v
                     [HITL_APPROVAL_GATE]                            [EXECUTE_ACTION]
                         |          |                                        |
              (Approved) |          | (Rejected)                             v
                         v          v                                   [EMIT_SPEC]
                   [EXECUTE_ACTION] [ABORT]                                  |
                         |          |                                        v
                         +----------+------------------------------------> [END]
    """
    def __init__(self, checkpoint_store: Optional[DurableCheckpointStore] = None):
        self.store = checkpoint_store or DurableCheckpointStore()

    def run_step(self, state: AgentState) -> AgentState:
        """Executes the next transition step in the state machine."""
        if state.step_count >= state.max_steps:
            state.status = "HALTED"
            state.error_message = f"Loop guard triggered: Max iterations ({state.max_steps}) exceeded."
            self.store.save(state.session_id, state)
            return state

        state.step_count += 1

        if state.status in ("INIT", "PLANNING"):
            state = self._node_plan_and_retrieve(state)
        elif state.status == "EXECUTING":
            state = self._node_execute_actions(state)
        elif state.status == "AWAITING_HUMAN_APPROVAL":
            state.audit_trail.append("[HITL GATE] Execution blocked pending external Human-in-the-Loop token approval.")
        
        self.store.save(state.session_id, state)
        return state

    def _node_plan_and_retrieve(self, state: AgentState) -> AgentState:
        state.audit_trail.append(f"[PLANNER] Decomposing objective: '{state.goal}'")
        
        # 1. Hybrid RAG retrieval
        retrieval_res = execute_hybrid_search(state.goal, top_n=2)
        state.retrieved_contexts = retrieval_res["hybrid_top"]
        state.audit_trail.append(
            f"[HYBRID_RAG] Retrieved {len(state.retrieved_contexts)} top clauses via RRF k=60."
        )

        # 2. Plan proposed tool actions based on goal keywords
        goal_lower = state.goal.lower()
        proposed_action = {}
        if any(term in goal_lower for term in ["drop", "truncate", "delete", "destroy", "mutation"]):
            proposed_action = {
                "action": "MUTATE_DATABASE_SCHEMA",
                "risk_category": "DESTRUCTIVE_DDL",
                "payload": "DROP TABLE audit_trail_archive_2023 CASCADE;",
                "requires_human_approval": True
            }
            state.pending_actions.append(proposed_action)
            state.audit_trail.append(
                f"[SECURITY] High-risk destructive action planned: {proposed_action['action']}"
            )
            state.status = "AWAITING_HUMAN_APPROVAL"
            state.hitl_interrupted = True
            state.hitl_mutation_detected = True
        else:
            proposed_action = {
                "action": "EVALUATE_SPEC_COMPLIANCE",
                "risk_category": "READ_ONLY_AUDIT",
                "payload": state.retrieved_contexts[0]["id"] if state.retrieved_contexts else "CLAUSE-001",
                "requires_human_approval": False
            }
            state.pending_actions.append(proposed_action)
            state.status = "EXECUTING"
            state.audit_trail.append(
                f"[SECURITY] Action deemed safe: {proposed_action['action']}. Transitioning to EXECUTING."
            )

        return state

    def resolve_hitl_interrupt(self, state: AgentState, approved: bool, approval_token: str) -> AgentState:
        """
        Resume human-in-the-loop interruption with explicit token verification.
        """
        if state.status != "AWAITING_HUMAN_APPROVAL":
            raise ValueError(f"Agent state is {state.status}, not awaiting HITL approval.")

        if not approved:
            state.status = "REJECTED"
            state.audit_trail.append(f"[HITL GATE] Mutation action REJECTED by Human Operator. Reason: Token denied.")
            state.pending_actions.clear()
            self.store.save(state.session_id, state)
            return state

        # Verify token format
        if not approval_token.startswith("AUTH-SEC-"):
            state.status = "REJECTED"
            state.audit_trail.append(f"[HITL GATE] Invalid dual-authorization token format '{approval_token}'. Rejection enforced.")
            self.store.save(state.session_id, state)
            return state

        state.approval_token = approval_token
        state.hitl_interrupted = False
        state.status = "EXECUTING"
        state.audit_trail.append(
            f"[HITL GATE] Authorized with verified token '{approval_token}'. Resuming execution DAG."
        )
        self.store.save(state.session_id, state)
        return state

    def _node_execute_actions(self, state: AgentState) -> AgentState:
        for action in list(state.pending_actions):
            state.audit_trail.append(f"[EXECUTOR] Executing verified action: {action['action']}")
            state.executed_actions.append(action)
        state.pending_actions.clear()

        # Emit typed Pydantic compliance contract
        top_clause = state.retrieved_contexts[0] if state.retrieved_contexts else {
            "id": "CLAUSE-001",
            "title": "General System SLA Compliance"
        }

        assessment = ClauseRiskAssessment(
            clause_id=top_clause["id"],
            contract_title=top_clause["title"],
            risk_level="CRITICAL" if state.hitl_mutation_detected else "MEDIUM",
            confidence_score=0.96 if state.retrieved_contexts else 0.85,
            identified_vulnerabilities=[
                "High latency SLA breach risk on P99 response webhook" 
                if "latency" in top_clause.get("tags", []) 
                else "Unverified schema mutation or compliance gap"
            ],
            actionable_mitigation=(
                "Enforce distributed trace span context propagation via OpenTelemetry "
                "and provision Redis read-through replica cache to keep P99 under 250ms."
            )
        )
        state.output_assessment = assessment.model_dump()
        state.status = "COMPLETED"
        state.audit_trail.append("[OUTPUT] Emitted validated Pydantic v2 ClauseRiskAssessment contract.")
        return state
