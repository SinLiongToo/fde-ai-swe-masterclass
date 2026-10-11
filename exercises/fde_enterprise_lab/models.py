"""
Blueprint 1: Spec-Driven Development & Schema Contracts
Implements strict domain validation using Pydantic v2.
"""

from typing import List, Literal
from pydantic import BaseModel, Field, field_validator
import re

class ClauseRiskAssessment(BaseModel):
    """
    Enterprise Compliance & Security Specification Contract.
    Enforces deterministic validation rules before downstream processing.
    """
    clause_id: str = Field(
        ..., 
        description="Standardized identifier (e.g. CLAUSE-001)",
        pattern=r"^CLAUSE-\d{3,4}$"
    )
    contract_title: str = Field(..., min_length=3, max_length=120)
    risk_level: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = Field(
        ..., description="Standardized severity categorization"
    )
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Calibrated model confidence bounded between 0.0 and 1.0"
    )
    identified_vulnerabilities: List[str] = Field(
        ..., 
        min_length=1, 
        description="Specific legal/compliance violations or security gaps"
    )
    actionable_mitigation: str = Field(
        ..., 
        min_length=25, 
        description="Concrete, auditable remediation instructions for SRE/Legal"
    )

    @field_validator("actionable_mitigation")
    @classmethod
    def validate_non_lazy_mitigation(cls, v: str) -> str:
        """
        Anti-Hallucination Gate: Rejects lazy, evasive model outputs like 'TBD' or 'Contact admin'.
        """
        prohibited_tokens = ["tbd", "todo", "contact admin", "look at logs", "n/a", "check later"]
        lower_v = v.lower()
        for token in prohibited_tokens:
            if token in lower_v:
                raise ValueError(
                    f"Contract Violation: Mitigation contains prohibited lazy placeholder '{token}'. "
                    "Must supply concrete technical remediation runbook."
                )
        return v

class AuditBatchSummary(BaseModel):
    """
    Aggregated enterprise audit summary contract.
    """
    total_clauses_analyzed: int = Field(..., ge=1)
    critical_risk_count: int = Field(..., ge=0)
    overall_compliance_status: Literal["PASSED", "WARNING", "BLOCKED"]
    assessments: List[ClauseRiskAssessment]
