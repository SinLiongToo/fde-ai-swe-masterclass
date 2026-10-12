"""
Test Suite for AI Code Reviewer & Architecture Inspector
Verifies static AST detection, rule retrieval, and Pydantic v2 contract integrity.
"""

import os
import pytest
from pydantic import ValidationError

from practical_examples.ai_code_reviewer.schemas import CodeIssue, ReviewReport
from practical_examples.ai_code_reviewer.reviewer_agent import AICodeReviewerAgent
from practical_examples.ai_code_reviewer.rule_engine import ArchitectureRuleEngine


@pytest.fixture
def agent():
    return AICodeReviewerAgent()


@pytest.fixture
def samples_dir():
    return os.path.join(os.path.dirname(__file__), "samples")


def test_vulnerable_api_detects_all_flaws(agent, samples_dir):
    """The vulnerable API sample must trigger BLOCKED verdict and catch all 5 violations."""
    target = os.path.join(samples_dir, "vulnerable_api.py")
    report = agent.review_file(target)

    assert report.verdict == "BLOCKED"
    assert report.security_score == 0
    assert len(report.issues) >= 4

    rule_ids = [i.rule_id for i in report.issues]
    assert "SEC-001" in rule_ids  # SQL Injection
    assert "SEC-002" in rule_ids  # Hardcoded API Key
    assert "PERF-001" in rule_ids # Missing Timeout
    assert "SEC-003" in rule_ids  # Dangerous eval()
    assert "ARCH-001" in rule_ids # Destructive DROP TABLE


def test_clean_api_passes_quality_gate(agent, samples_dir):
    """The clean API sample must pass with 100/100 score and zero issues."""
    target = os.path.join(samples_dir, "clean_api.py")
    report = agent.review_file(target)

    assert report.verdict == "PASSED"
    assert report.security_score == 100
    assert len(report.issues) == 0


def test_anti_lazy_validation_gate():
    """Anti-hallucination gate must reject lazy tokens in suggested fixes."""
    with pytest.raises(ValidationError) as exc:
        CodeIssue(
            file_path="src/main.py",
            line_number=10,
            rule_id="SEC-001",
            severity="CRITICAL",
            title="SQL Injection",
            description="Direct string interpolation into database query.",
            code_snippet="cursor.execute(f'SELECT {id}')",
            suggested_fix="TODO: fix later when refactoring" # Lazy token!
        )
    assert "prohibited placeholder 'todo'" in str(exc.value).lower()


def test_markdown_rule_loading(tmp_path):
    """Verifies that custom engineering rules can be loaded from markdown files."""
    rule_file = tmp_path / "custom_rules.md"
    rule_file.write_text(
        "# Custom Guidelines\n\n"
        "## UI-001: Mandatory Dark Mode\n"
        "Every UI component must support dark mode with CSS variables.\n\n"
        "## UI-002: Mandatory Bilingual Support\n"
        "All user-facing text must be defined in i18n dictionaries.\n",
        encoding="utf-8"
    )

    engine = ArchitectureRuleEngine(str(rule_file))
    rule_ids = [r.rule_id for r in engine.rules]
    assert "UI-001" in rule_ids
    assert "UI-002" in rule_ids
