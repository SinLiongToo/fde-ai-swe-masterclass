"""
GCP Model Context Protocol (MCP) Server
Module: mcp_server.py
Implements an executable MCP server over JSON-RPC 2.0 standard I/O (stdio).
Exposes tools for Enterprise RAG knowledge search and GCP Cloud Run / Cloud SQL telemetry.
"""

import sys
import json
import io
from typing import Dict, Any, List

from .protocol import (
    JSONRPCRequest,
    JSONRPCResponse,
    MCPToolDefinition,
    MCPToolInputSchema,
    MCPCallToolResult,
    MCPContentItem
)
from .rag_engine import EnterpriseRAGEngine
from .gcp_telemetry import GCPResourceManager

# Reconfigure stdout/stdin to UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass


class GCPSREMCPServer:
    """Enterprise MCP Server bridging LLM agents to GCP infrastructure and RAG knowledge."""

    def __init__(self):
        self.rag_engine = EnterpriseRAGEngine()
        self.gcp_manager = GCPResourceManager()
        self.tools = self._register_tools()

    def _register_tools(self) -> List[MCPToolDefinition]:
        return [
            MCPToolDefinition(
                name="search_enterprise_rag",
                description="Performs 2-stage hybrid search across enterprise GCP SRE runbooks and incident documentation.",
                inputSchema=MCPToolInputSchema(
                    properties={
                        "query": {"type": "string", "description": "The search query or symptom description"},
                        "top_k": {"type": "integer", "description": "Number of top chunks to retrieve (default: 3)"}
                    },
                    required=["query"]
                )
            ),
            MCPToolDefinition(
                name="get_gcp_service_status",
                description="Retrieves live telemetry and health metrics for a specified Google Cloud Run service or Cloud SQL database.",
                inputSchema=MCPToolInputSchema(
                    properties={
                        "resource_type": {"type": "string", "enum": ["cloud_run", "cloud_sql"], "description": "GCP resource type"},
                        "resource_id": {"type": "string", "description": "Identifier (e.g. 'payment-gateway', 'enterprise-db-primary')"}
                    },
                    required=["resource_type", "resource_id"]
                )
            ),
            MCPToolDefinition(
                name="update_cloud_run_scaling",
                description="Modifies scaling configuration on a Google Cloud Run service (min/max instances, concurrency, CPU boost).",
                inputSchema=MCPToolInputSchema(
                    properties={
                        "service_name": {"type": "string", "description": "Name of Cloud Run service"},
                        "min_instances": {"type": "integer", "description": "Minimum instances (warm containers)"},
                        "max_instances": {"type": "integer", "description": "Maximum instances"},
                        "container_concurrency": {"type": "integer", "description": "Max concurrent requests per container"},
                        "cpu_boost_enabled": {"type": "boolean", "description": "Enable CPU boost during cold startup"}
                    },
                    required=["service_name", "min_instances", "max_instances"]
                )
            )
        ]

    def handle_request(self, req: JSONRPCRequest) -> JSONRPCResponse:
        """Dispatches incoming JSON-RPC methods."""
        method = req.method

        if method == "initialize":
            return JSONRPCResponse(
                id=req.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "gcp-sre-mcp-server",
                        "version": "1.0.0"
                    }
                }
            )

        elif method == "tools/list":
            return JSONRPCResponse(
                id=req.id,
                result={"tools": [t.model_dump() for t in self.tools]}
            )

        elif method == "tools/call":
            params = req.params or {}
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = self._execute_tool(tool_name, arguments)
            return JSONRPCResponse(
                id=req.id,
                result=result.model_dump()
            )

        else:
            return JSONRPCResponse(
                id=req.id,
                error={"code": -32601, "message": f"Method '{method}' not found."}
            )

    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPCallToolResult:
        """Executes registered tool and returns standard MCPContentItem."""
        try:
            if tool_name == "search_enterprise_rag":
                query = arguments.get("query", "")
                top_k = arguments.get("top_k", 3)
                results = self.rag_engine.hybrid_search(query, top_k=top_k)
                text_out = json.dumps(results, indent=2, ensure_ascii=False)
                return MCPCallToolResult(content=[MCPContentItem(text=text_out)], isError=False)

            elif tool_name == "get_gcp_service_status":
                res_type = arguments.get("resource_type")
                res_id = arguments.get("resource_id")
                if res_type == "cloud_run":
                    data = self.gcp_manager.get_cloud_run_service(res_id)
                else:
                    data = self.gcp_manager.get_cloud_sql_instance(res_id)

                if data is None:
                    return MCPCallToolResult(
                        content=[MCPContentItem(text=f"Resource '{res_id}' ({res_type}) not found.")],
                        isError=True
                    )
                return MCPCallToolResult(content=[MCPContentItem(text=json.dumps(data, indent=2))], isError=False)

            elif tool_name == "update_cloud_run_scaling":
                service_name = arguments.get("service_name")
                min_inst = arguments.get("min_instances", 0)
                max_inst = arguments.get("max_instances", 10)
                concurrency = arguments.get("container_concurrency")
                cpu_boost = arguments.get("cpu_boost_enabled")

                res = self.gcp_manager.update_cloud_run_scaling(
                    service_name=service_name,
                    min_instances=min_inst,
                    max_instances=max_inst,
                    container_concurrency=concurrency,
                    cpu_boost_enabled=cpu_boost
                )
                return MCPCallToolResult(content=[MCPContentItem(text=json.dumps(res, indent=2))], isError=False)

            else:
                return MCPCallToolResult(
                    content=[MCPContentItem(text=f"Unknown tool name: {tool_name}")],
                    isError=True
                )
        except Exception as e:
            return MCPCallToolResult(
                content=[MCPContentItem(text=f"Tool execution failed: {str(e)}")],
                isError=True
            )

    def run_stdio(self):
        """Standard I/O event loop for MCP server."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                raw_json = json.loads(line)
                req = JSONRPCRequest(**raw_json)
                resp = self.handle_request(req)
                sys.stdout.write(resp.model_dump_json() + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_resp = JSONRPCResponse(
                    id=None,
                    error={"code": -32700, "message": f"Parse error: {str(e)}"}
                )
                sys.stdout.write(err_resp.model_dump_json() + "\n")
                sys.stdout.flush()


def main():
    server = GCPSREMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
