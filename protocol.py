"""
ACP Protocol Definitions
Pydantic models for validation
"""

from typing import Literal, Optional, Dict, Any, List
from pydantic import BaseModel


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 Request"""
    jsonrpc: Literal["2.0"]
    id: int | str
    method: str
    params: Optional[Dict[str, Any]] = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 Response"""
    jsonrpc: Literal["2.0"]
    id: int | str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class AgentCreateParams(BaseModel):
    """Parameters for agent/create method"""
    name: str
    instructions: str
    tools: Optional[List[str]] = None
    memory_config: Optional[Dict[str, Any]] = None


class AgentMessageParams(BaseModel):
    """Parameters for agent/message method"""
    agent_id: str
    message: str
    context: Optional[Dict[str, Any]] = None


class AgentToolCallParams(BaseModel):
    """Parameters for agent/tool_call method"""
    agent_id: str
    tool_name: str
    arguments: Dict[str, Any]


# ACP Method Registry
# Maps ACP method names to handler method names
ACP_METHODS = {
    "initialize": "handle_initialize",
    "agent/create": "handle_agent_create",
    "agent/message": "handle_agent_message",
    "agent/tool_call": "handle_agent_tool_call",
    "agent/delete": "handle_agent_delete",
    "agent/list": "handle_agent_list",
}