"""
Pytest Test Suite for GCP + MCP + RAG Enterprise Service
Verifies:
1. Model Context Protocol JSON-RPC 2.0 handshake and tool discovery
2. 2-Stage Hybrid RAG retrieval accuracy on markdown runbooks
3. GCP resource telemetry querying and scaling remediation
"""

import json
import pytest
from practical_examples.gcp_mcp_rag_service.protocol import JSONRPCRequest
from practical_examples.gcp_mcp_rag_service.mcp_server import GCPSREMCPServer
from practical_examples.gcp_mcp_rag_service.agent_client import MCPSREAgent


@pytest.fixture
def mcp_server():
    return GCPSREMCPServer()


@pytest.fixture
def agent(mcp_server):
    return MCPSREAgent(mcp_server)


def test_mcp_initialize(mcp_server):
    """MCP Handshake must return protocol 2024-11-05 and server capabilities."""
    req = JSONRPCRequest(id=1, method="initialize")
    resp = mcp_server.handle_request(req)

    assert resp.error is None
    assert resp.result["protocolVersion"] == "2024-11-05"
    assert "tools" in resp.result["capabilities"]
    assert resp.result["serverInfo"]["name"] == "gcp-sre-mcp-server"


def test_mcp_tools_list(mcp_server):
    """Server must declare 3 enterprise SRE tools with schemas."""
    req = JSONRPCRequest(id=2, method="tools/list")
    resp = mcp_server.handle_request(req)

    tools = resp.result["tools"]
    tool_names = [t["name"] for t in tools]

    assert "search_enterprise_rag" in tool_names
    assert "get_gcp_service_status" in tool_names
    assert "update_cloud_run_scaling" in tool_names


def test_mcp_rag_search(mcp_server):
    """Calling search_enterprise_rag over MCP must retrieve Cloud Run latency runbook."""
    req = JSONRPCRequest(id=3, method="tools/call", params={
        "name": "search_enterprise_rag",
        "arguments": {"query": "Cloud Run P99 latency cold starts 504 timeout", "top_k": 2}
    })
    resp = mcp_server.handle_request(req)

    assert resp.error is None
    content_text = resp.result["content"][0]["text"]
    chunks = json.loads(content_text)

    assert len(chunks) >= 1
    assert "runbook_cloud_run_latency.md" in chunks[0]["file_path"]
    assert "rrf_score" in chunks[0]


def test_mcp_telemetry_and_scaling(mcp_server):
    """Querying and updating Cloud Run scaling via MCP must remediate latency."""
    # 1. Query status
    req_status = JSONRPCRequest(id=4, method="tools/call", params={
        "name": "get_gcp_service_status",
        "arguments": {"resource_type": "cloud_run", "resource_id": "payment-gateway"}
    })
    resp_status = mcp_server.handle_request(req_status)
    data = json.loads(resp_status.result["content"][0]["text"])
    assert data["status"] == "DEGRADED"

    # 2. Update scaling via MCP
    req_scale = JSONRPCRequest(id=5, method="tools/call", params={
        "name": "update_cloud_run_scaling",
        "arguments": {
            "service_name": "payment-gateway",
            "min_instances": 3,
            "max_instances": 20,
            "container_concurrency": 20,
            "cpu_boost_enabled": True
        }
    })
    resp_scale = mcp_server.handle_request(req_scale)
    scale_res = json.loads(resp_scale.result["content"][0]["text"])

    assert scale_res["status"] == "SUCCESS"
    assert scale_res["updated_state"]["status"] == "HEALTHY"
    assert scale_res["updated_state"]["p99_latency_ms"] < 250


def test_agent_end_to_end(agent):
    """Agent orchestrator must diagnose and remediate using MCP tools."""
    report = agent.diagnose_and_remediate("payment-gateway latency issue", auto_remediate=True)

    assert report["target_service"] == "payment-gateway"
    assert report["initial_telemetry"]["status"] == "DEGRADED"
    assert report["grounded_runbook"]["doc_id"] == "GCP-RUNBOOK-001"
    assert report["remediation_result"]["status"] == "SUCCESS"
    assert len(report["steps_log"]) >= 4
