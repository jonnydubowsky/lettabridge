"""
Configuration Management
Load from environment variables and .env file
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class BridgeConfig(BaseSettings):
    """Configuration for ACP-Letta bridge"""
    
    # Letta Configuration
    letta_base_url: str = "http://localhost:8283"
    letta_api_key: Optional[str] = None
    
    @property
    def letta_api_token(self) -> Optional[str]:
        """Alias for letta_api_key for compatibility"""
        return self.letta_api_key
    
    # Bridge Configuration
    agent_name: str = "zed_coding_assistant"
    log_level: str = "INFO"
    max_agents: int = 10
    agent_timeout: int = 300  # seconds
    
    # Tool Configuration
    enable_web_search: bool = True
    enable_code_execution: bool = True
    enable_file_operations: bool = False
    
    class Config:
        env_file = ".env"
        env_prefix = "BRIDGE_"


# Singleton instance
config = BridgeConfig()