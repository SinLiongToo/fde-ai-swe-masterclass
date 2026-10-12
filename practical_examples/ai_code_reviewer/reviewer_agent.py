"""
AI Code Reviewer & Architecture Compliance Inspector
Module: reviewer_agent.py
Coordinates AST pre-flight scanning, rule grounding (RAG), and LLM reasoning.
Supports Google Gemini via `google-genai` and a deterministic local fallback engine.
"""

import os
import json
from typing import Optional, List
from .schemas import CodeIssue, ReviewReport
from .ast_analyzer import analyze_source_code_ast
from .rule_engine import ArchitectureRuleEngine


class AICodeReviewerAgent:
    """
    Enterprise-grade Code Reviewer Agent implementing:
    1. Static AST Invariant Pre-flight Scan
    2. Architecture Rule Grounding (RAG)
    3. LLM Structured Extraction (Gemini / Local Engine)
    4. Pydantic v2 Output Contract Validation
    """

    def __init__(self, custom_rules_file: Optional[str] = None):
        self.rule_engine = ArchitectureRuleEngine(custom_rules_file)
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def review_file(self, file_path: str) -> ReviewReport:
        """Inspects a single Python file and returns a validated ReviewReport."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Target file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()

        total_lines = len(source_code.splitlines()) or 1

        # Step 1: Pre-flight AST static check
        ast_issues = analyze_source_code_ast(file_path, source_code)

        # Step 2: Contextual Rule Retrieval (RAG)
        relevant_rules = self.rule_engine.retrieve_relevant_rules(source_code)

        # Step 3: Run LLM if API key is configured, else fallback to deterministic engine
        if self.client:
            try:
                report = self._run_gemini_review(file_path, source_code, ast_issues, relevant_rules, total_lines)
                return report
            except Exception as e:
                # Fallback to local heuristic engine if API call fails
                return self._run_local_engine(file_path, source_code, ast_issues, relevant_rules, total_lines, fallback_reason=str(e))
        else:
            return self._run_local_engine(file_path, source_code, ast_issues, relevant_rules, total_lines)

    def _run_gemini_review(
        self, 
        file_path: str, 
        source_code: str, 
        ast_issues: List[CodeIssue], 
        rules: list, 
        total_lines: int
    ) -> ReviewReport:
        """Executes LLM code review using Google Gemini with structured Pydantic decoding."""
        rules_context = "\n".join([f"- [{r.rule_id}] {r.title} ({r.severity}): {r.description}" for r in rules])
        ast_context = "\n".join([f"- Line {i.line_number} [{i.rule_id}]: {i.title}" for i in ast_issues]) or "None detected by AST."

        prompt = f"""You are an elite Forward Deployed Engineer (FDE) and Principal Security Reviewer.
Inspect the following Python source code against our enterprise engineering standards.

[PROJECT ARCHITECTURE RULES]
{rules_context}

[PRE-FLIGHT AST DETECTIONS]
{ast_context}

[SOURCE CODE: {file_path}]
```python
{source_code}
```

Instructions:
1. Examine every line for SQL injection, hardcoded credentials, missing timeouts, or architecture anti-patterns.
2. Incorporate the pre-flight AST detections into your final issues.
3. Every issue MUST specify: line_number, rule_id, severity (CRITICAL, HIGH, MEDIUM, LOW, INFO), title, description, code_snippet, suggested_fix (concrete code instructions, NO 'TBD' or 'todo'), and a unified diff_patch.
4. Calculate an overall security_score (0-100), verdict (PASSED, WARNING, BLOCKED), and executive summary.
"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ReviewReport,
            }
        )
        data = json.loads(response.text)
        data["execution_mode"] = "GEMINI_LLM"
        return ReviewReport(**data)

    def _run_local_engine(
        self, 
        file_path: str, 
        source_code: str, 
        ast_issues: List[CodeIssue], 
        rules: list, 
        total_lines: int,
        fallback_reason: Optional[str] = None
    ) -> ReviewReport:
        """Deterministic local review engine using AST analysis and pattern matching."""
        issues = list(ast_issues)

        # Check for destructive DDL keywords
        code_upper = source_code.upper()
        if "DROP TABLE" in code_upper or "TRUNCATE" in code_upper:
            # Find line number
            for idx, line in enumerate(source_code.splitlines(), start=1):
                if "DROP TABLE" in line.upper() or "TRUNCATE" in line.upper():
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=idx,
                        rule_id="ARCH-001",
                        severity="CRITICAL",
                        title="Unshielded Destructive DDL Statement",
                        description="Destructive table drops detected in application logic. This violates Rule ARCH-001.",
                        code_snippet=line.strip(),
                        suggested_fix="Move schema alterations to isolated database migration runbooks with transaction guards.",
                        diff_patch=f"- {line.strip()}\n+ # Schema migrations must be applied through Alembic or Flyway"
                    ))
                    break

        summary = (
            f"Static code audit completed for '{file_path}'. "
            f"Detected {len(issues)} security & architecture issue(s). "
        )
        if fallback_reason:
            summary += f"[Notice: Ran in local engine fallback due to: {fallback_reason[:60]}]"
        else:
            summary += "[Local Deterministic Engine: Set GEMINI_API_KEY to enable LLM semantic reasoning]"

        return ReviewReport.calculate_verdict(
            issues=issues,
            total_lines=total_lines,
            mode="STATIC_HEURISTIC_ENGINE",
            summary=summary,
            target_file=file_path
        )
