"""
Model Context Protocol (MCP) Client & SRE Agent Orchestrator
Module: agent_client.py
Demonstrates how an AI Agent connects to the MCP Server via JSON-RPC,
discovers tools dynamically, queries GCP telemetry, retrieves RAG runbooks,
and performs audited infrastructure remediation.
"""

import json
from typing import Dict, Any, List, Optional
from .protocol import JSONRPCRequest
from .mcp_server import GCPSREMCPServer


class MCPSREAgent:
    """Agent orchestrator interfacing with GCP and RAG via Model Context Protocol."""

    def __init__(self, mcp_server: Optional[GCPSREMCPServer] = None):
        self.server = mcp_server or GCPSREMCPServer()
        self.msg_id = 0
        self.discovered_tools: List[Dict[str, Any]] = []
        self._handshake_and_discover()

    def _send_rpc(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Sends a JSON-RPC request to the MCP Server."""
        self.msg_id += 1
        req = JSONRPCRequest(id=self.msg_id, method=method, params=params or {})
        resp = self.server.handle_request(req)
        if resp.error:
            raise RuntimeError(f"MCP RPC Error ({resp.error.get('code')}): {resp.error.get('message')}")
        return resp.result

    def _handshake_and_discover(self):
        """Step 1 & 2: MCP Handshake & Tool Discovery."""
        init_res = self._send_rpc("initialize")
        list_res = self._send_rpc("tools/list")
        self.discovered_tools = list_res.get("tools", [])

    def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Invokes a specific tool over the Model Context Protocol."""
        res = self._send_rpc("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        content_items = res.get("content", [])
        return "\n".join(item.get("text", "") for item in content_items)

    def diagnose_and_remediate(self, user_query: str, auto_remediate: bool = True) -> Dict[str, Any]:
        """
        End-to-End Diagnostic & Remediation Workflow:
        1. Parse intent & query live GCP Telemetry via MCP tool
        2. Query Enterprise RAG Runbooks via MCP tool
        3. Formulate diagnosis with exact line citations
        4. (Optional) Apply Cloud Run Scaling remediation via MCP tool
        """
        steps_log = []

        # Step 1: Detect target resource from query
        target_service = "payment-gateway" if "payment" in user_query.lower() else "order-processor"

        # MCP Tool Call 1: get_gcp_service_status
        steps_log.append(f"[MCP] Calling tool 'get_gcp_service_status' for '{target_service}'")
        raw_status = self.call_mcp_tool("get_gcp_service_status", {
            "resource_type": "cloud_run",
            "resource_id": target_service
        })
        service_telemetry = json.loads(raw_status)
        steps_log.append(
            f"[GCP Status] State: {service_telemetry.get('status')} | "
            f"P99 Latency: {service_telemetry.get('p99_latency_ms')}ms | "
            f"Min Instances: {service_telemetry.get('min_instances')}"
        )

        # MCP Tool Call 2: search_enterprise_rag
        rag_query = f"Cloud Run latency 504 timeout cold start {target_service}"
        steps_log.append(f"[MCP] Calling tool 'search_enterprise_rag' with query: '{rag_query}'")
        raw_rag = self.call_mcp_tool("search_enterprise_rag", {
            "query": rag_query,
            "top_k": 2
        })
        rag_chunks = json.loads(raw_rag)
        top_runbook = rag_chunks[0] if rag_chunks else {}
        steps_log.append(
            f"[RAG Retrieved] Doc: {top_runbook.get('doc_id')} - '{top_runbook.get('title')}' "
            f"(Score: {top_runbook.get('rrf_score', 0):.4f})"
        )

        # Step 3: Remediation Decision
        remediation_result = None
        if auto_remediate and service_telemetry.get("status") == "DEGRADED":
            steps_log.append(
                "[MCP] Applying recommended runbook remediation: update_cloud_run_scaling "
                "(min_instances=3, max_instances=30, cpu_boost=True)"
            )
            raw_remediation = self.call_mcp_tool("update_cloud_run_scaling", {
                "service_name": target_service,
                "min_instances": 3,
                "max_instances": 30,
                "container_concurrency": 20,
                "cpu_boost_enabled": True
            })
            remediation_result = json.loads(raw_remediation)
            steps_log.append(f"[GCP Remediation] {remediation_result.get('message')}")

        return {
            "target_service": target_service,
            "initial_telemetry": service_telemetry,
            "grounded_runbook": top_runbook,
            "remediation_result": remediation_result,
            "steps_log": steps_log
        }
