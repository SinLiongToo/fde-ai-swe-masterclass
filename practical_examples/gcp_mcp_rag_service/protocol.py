"""
Model Context Protocol (MCP) JSON-RPC 2.0 Specification Contracts
Module: protocol.py
Defines typed Pydantic v2 schemas for MCP stdio / SSE communication:
- tools/list
- tools/call
- resources/list
- initialize
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class MCPToolInputSchema(BaseModel):
    type: str = "object"
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)


class MCPToolDefinition(BaseModel):
    name: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Human and LLM-readable description of tool capability")
    inputSchema: MCPToolInputSchema = Field(default_factory=MCPToolInputSchema)


class MCPContentItem(BaseModel):
    type: str = "text"
    text: str


class MCPCallToolResult(BaseModel):
    content: List[MCPContentItem] = Field(default_factory=list)
    isError: bool = False


class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
