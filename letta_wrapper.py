"""
Letta API client wrapper
Handles communication with Letta server
"""

import os
import logging
from typing import Dict, Any, Optional, List
from letta_client import Letta  # pip install letta-client
from config import BridgeConfig

logger = logging.getLogger(__name__)


class LettaClientWrapper:
    """Wrapper around Letta Python SDK"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.client: Optional[Letta] = None
        self.agents: Dict[str, str] = {}  # name -> agent_id
        
    async def connect(self):
        """Connect to Letta server"""
        try:
            if self.config.letta_api_token:
                self.client = Letta(
                    base_url=self.config.letta_base_url,
                    api_key=self.config.letta_api_token
                )
            else:
                self.client = Letta(base_url=self.config.letta_base_url)
            logger.info(f"Connected to Letta server: {self.config.letta_base_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Letta: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Letta server"""
        # Letta client doesn't require explicit disconnect
        logger.info("Disconnected from Letta server")
    
    async def get_or_create_agent(self, agent_name: str, agent_config: Dict[str, Any]) -> str:
        """Get existing agent or create new one"""
        try:
            # List existing agents
            agents_response = self.client.agents.list()
            
            # Check if agent exists
            for agent in agents_response:
                if hasattr(agent, 'name') and agent.name == agent_name:
                    logger.info(f"Found existing agent: {agent_name} ({agent.id})") 
                    self.agents[agent_name] = agent.id
                    return agent.id
            
            # Create new agent
            logger.info(f"Creating new agent: {agent_name}")
            
            # Build memory blocks for new API
            memory_blocks = [
                {"label": "persona", "value": agent_config.get("persona", "You are a helpful assistant.")},
                {"label": "human", "value": "The user is a software developer."}
            ]
            
            agent_state = self.client.agents.create(
                model="openai/gpt-4o-mini",
                embedding="openai/text-embedding-3-small",
                memory_blocks=memory_blocks
            )
            
            self.agents[agent_name] = agent_state.id
            logger.info(f"Created agent: {agent_name} ({agent_state.id})")
            return agent_state.id
            
        except Exception as e:
            logger.error(f"Error getting/creating agent: {e}")
            raise
    
    async def send_message(self, agent_id: str, message: str) -> Dict[str, Any]:
        """Send message to Letta agent and get response"""
        try:
            response = self.client.agents.messages.send(
                agent_id=agent_id,
                message=message,
                role="user"
            )
            
            # Extract text from response messages
            text_parts = []
            memory_updated = False
            reasoning = ""
            
            for msg in response.messages:
                if hasattr(msg, 'text') and msg.text:
                    text_parts.append(msg.text)
                if hasattr(msg, 'function_call'):
                    if msg.function_call and 'memory' in msg.function_call.name:
                        memory_updated = True
            
            return {
                "text": "\n".join(text_parts),
                "memory_updated": memory_updated,
                "reasoning": reasoning,
                "raw_response": response
            }
            
        except Exception as e:
            logger.error(f"Error sending message to agent: {e}")
            raise
    
    async def get_agent_memory(self, agent_id: str) -> Dict[str, Any]:
        """Retrieve agent's memory blocks"""
        try:
            memory = self.client.agents.memory.get(agent_id)
            return {
                "core_memory": str(memory),
                "archival_memory": []
            }
        except Exception as e:
            logger.error(f"Error retrieving agent memory: {e}")
            raise
