"""
Letta Client Wrapper
Abstracts Letta API interactions
"""

import logging
from typing import List, Dict, Any, Optional
from letta import LettaClient, create_client

logger = logging.getLogger(__name__)


class LettaClientWrapper:
    """Wrapper for Letta API with error handling"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        
        # Initialize Letta client
        if api_key:
            self.client = create_client(base_url=base_url, token=api_key)
        else:
            self.client = create_client(base_url=base_url)
            
        self.agents = {}  # Cache: agent_id -> agent_state
        
        logger.info(f"Initialized Letta client: {base_url}")
    
    async def create_agent(
        self, 
        name: str, 
        instructions: str,
        tools: Optional[List[str]] = None
    ) -> str:
        """
        Create new Letta agent
        
        Returns:
            agent_id (str)
        """
        try:
            # Default tools if none specified
            if tools is None:
                tools = ["send_message", "conversation_search"]
            
            # Create agent via Letta API
            agent_state = self.client.create_agent(
                name=name,
                system=instructions,
                tools=tools
            )
            
            agent_id = agent_state.id
            self.agents[agent_id] = agent_state
            
            logger.info(f"Created agent: {name} (ID: {agent_id})")
            return agent_id
            
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise
    
    async def send_message(
        self, 
        agent_id: str, 
        message: str
    ) -> Dict[str, Any]:
        """
        Send message to agent and get response
        
        Returns:
            {
                "messages": [...],
                "usage": {...}
            }
        """
        try:
            # Send message via Letta API
            response = self.client.send_message(
                agent_id=agent_id,
                message=message,
                role="user"
            )
            
            # Extract assistant messages
            messages = [
                msg.message
                for msg in response.messages
                if hasattr(msg, 'message')
            ]
            
            return {
                "messages": messages,
                "usage": response.usage if hasattr(response, 'usage') else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent details"""
        try:
            if agent_id in self.agents:
                return self.agents[agent_id]
            
            agent_state = self.client.get_agent(agent_id)
            self.agents[agent_id] = agent_state
            return agent_state
            
        except Exception as e:
            logger.error(f"Failed to get agent: {e}")
            return None
    
    async def delete_agent(self, agent_id: str):
        """Delete agent"""
        try:
            self.client.delete_agent(agent_id)
            if agent_id in self.agents:
                del self.agents[agent_id]
            logger.info(f"Deleted agent: {agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete agent: {e}")
            raise