"""
Configuration for ACP-Letta Bridge
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Bridge configuration"""
    
    # Letta connection
    letta_base_url: str = "http://localhost:8283"
    letta_api_token: Optional[str] = None
    
    # Agent configuration
    agent_name: str = "zed_coding_assistant"
    
    # Logging
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        return cls(
            letta_base_url=os.getenv("LETTA_BASE_URL", "http://localhost:8283"),
            letta_api_token=os.getenv("LETTA_API_TOKEN"),
            agent_name=os.getenv("AGENT_NAME", "zed_coding_assistant"),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )