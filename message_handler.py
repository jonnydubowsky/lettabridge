"""
Message Handler
Process ACP requests and format responses
"""

import logging
from typing import Dict, Any
from letta_client import LettaClientWrapper

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handle ACP method requests"""
    
    def __init__(self, letta_client: LettaClientWrapper):
        self.letta = letta_client
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle ACP initialize request
        Returns server capabilities
        """
        logger.info("Handling initialize request")
        
        return {
            "serverInfo": {
                "name": "letta-acp-bridge",
                "version": "0.1.0",
                "description": "Bridge between Zed and Letta agents"
            },
            "capabilities": {
                "agentProvider": True,
                "tools": [
                    "send_message",
                    "conversation_search",
                    "web_search",
                    "code_execution"
                ],
                "streaming": False,
                "persistentMemory": True
            }
        }
    
    async def handle_agent_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new Letta agent
        
        Params:
            name: Agent name
            instructions: System prompt
            tools: List of tool names (optional)
        
        Returns:
            agent_id, status, capabilities
        """
        logger.info(f"Creating agent: {params.get('name')}")
        
        name = params.get("name", "default-agent")
        instructions = params.get("instructions", "You are a helpful coding assistant.")
        tools = params.get("tools")
        
        # Create Letta agent
        agent_id = await self.letta.create_agent(
            name=name,
            instructions=instructions,
            tools=tools
        )
        
        return {
            "agent_id": agent_id,
            "status": "ready",
            "capabilities": tools or ["send_message"]
        }
    
    async def handle_agent_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send message to agent, return response
        
        Params:
            agent_id: Target agent ID
            message: User message
            context: Optional context (workspace info, etc.)
        
        Returns:
            agent_id, response messages, usage stats
        """
        agent_id = params["agent_id"]
        message = params["message"]
        
        logger.info(f"Sending message to agent {agent_id}")
        
        # Send to Letta agent
        response = await self.letta.send_message(agent_id, message)
        
        # Format for ACP
        return {
            "agent_id": agent_id,
            "response": response.get("messages", []),
            "usage": response.get("usage", {})
        }
    
    async def handle_agent_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool via agent
        
        Params:
            agent_id: Agent to use
            tool_name: Tool to execute
            arguments: Tool arguments
        
        Returns:
            tool_result
        """
        agent_id = params["agent_id"]
        tool_name = params["tool_name"]
        arguments = params["arguments"]
        
        logger.info(f"Tool call: {tool_name} via agent {agent_id}")
        
        # For now, forward as a message
        # In future, could call tools directly
        tool_message = f"Use the {tool_name} tool with these arguments: {arguments}"
        response = await self.letta.send_message(agent_id, tool_message)
        
        return {
            "tool_name": tool_name,
            "result": response.get("messages", [])
        }
    
    async def handle_agent_delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete agent
        
        Params:
            agent_id: Agent to delete
        
        Returns:
            status
        """
        agent_id = params["agent_id"]
        
        logger.info(f"Deleting agent {agent_id}")
        
        await self.letta.delete_agent(agent_id)
        
        return {
            "agent_id": agent_id,
            "status": "deleted"
        }
    
    async def handle_agent_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        List active agents
        
        Returns:
            List of agent IDs and names
        """
        logger.info("Listing agents")
        
        agents = list(self.letta.agents.keys())
        
        return {
            "agents": agents,
            "count": len(agents)
        }