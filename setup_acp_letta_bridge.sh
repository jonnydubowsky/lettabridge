#!/bin/bash
# ACP-Letta Bridge - Quick Start Setup Script
# Automates the complete setup process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "
${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}
"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main script starts here
print_header "ACP-Letta Bridge Quick Start"

echo "This script will:"
echo "  1. Check prerequisites"
echo "  2. Create project structure"
echo "  3. Generate all source files"
echo "  4. Install dependencies"
echo "  5. Test the bridge"
echo "  6. (Optional) Build binaries"
echo "  7. (Optional) Install Zed extension"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Step 1: Check Prerequisites
print_header "Step 1: Checking Prerequisites"

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check pip
if command_exists pip3; then
    print_success "pip3 found"
else
    print_error "pip3 not found. Please install pip3"
    exit 1
fi

# Check if Letta server is running
print_info "Checking if Letta server is running..."
if curl -s http://localhost:8283/health >/dev/null 2>&1; then
    print_success "Letta server is running"
else
    print_warning "Letta server not detected at http://localhost:8283"
    echo "Please start Letta server in another terminal:"
    echo "  letta server"
    read -p "Press Enter when Letta server is running..."
fi

# Check Zed (optional)
if command_exists zed; then
    print_success "Zed editor found"
    ZED_FOUND=true
else
    print_warning "Zed editor not found (optional for testing)"
    ZED_FOUND=false
fi

# Step 2: Create Project Structure
print_header "Step 2: Creating Project Structure"

PROJECT_DIR="acp-letta-bridge"
if [ -d "$PROJECT_DIR" ]; then
    print_warning "Directory $PROJECT_DIR already exists"
    read -p "Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_DIR"
        print_success "Removed existing directory"
    else
        print_error "Cannot proceed with existing directory"
        exit 1
    fi
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
print_success "Created directory: $PROJECT_DIR"

# Step 3: Generate Source Files
print_header "Step 3: Generating Source Files"

# Create requirements.txt
cat > requirements.txt << 'EOFMARKER'
letta>=0.5.0
EOFMARKER
print_success "Created requirements.txt"

# Create config.py
cat > config.py << 'EOFMARKER'
"""Configuration for ACP-Letta Bridge"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Bridge configuration"""
    letta_base_url: str = "http://localhost:8283"
    letta_api_token: Optional[str] = None
    agent_name: str = "zed_coding_assistant"
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
EOFMARKER
print_success "Created config.py"

# Create acp_protocol.py
cat > acp_protocol.py << 'EOFMARKER'
"""ACP (Agent Client Protocol) handler"""
from typing import Dict, Any, Optional

class ACPHandler:
    """Handle ACP JSON-RPC protocol"""
    
    @staticmethod
    def success_response(request_id: Optional[int], result: Dict[str, Any]) -> Dict[str, Any]:
        """Build successful JSON-RPC response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    @staticmethod
    def error_response(request_id: Optional[int], error_message: str, code: int = -32603) -> Dict[str, Any]:
        """Build error JSON-RPC response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": error_message
            }
        }
    
    @staticmethod
    def notification(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Build JSON-RPC notification"""
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
EOFMARKER
print_success "Created acp_protocol.py"

# Create letta_client_wrapper.py
cat > letta_client_wrapper.py << 'EOFMARKER'
"""Letta API client wrapper"""
import logging
from typing import Dict, Any, Optional
from letta import LettaClient
from config import Config

logger = logging.getLogger(__name__)

class LettaClientWrapper:
    """Wrapper around Letta Python SDK"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client: Optional[LettaClient] = None
        self.agents: Dict[str, str] = {}
        
    async def connect(self):
        """Connect to Letta server"""
        try:
            self.client = LettaClient(
                base_url=self.config.letta_base_url,
                token=self.config.letta_api_token
            )
            logger.info(f"Connected to Letta server: {self.config.letta_base_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Letta: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Letta server"""
        logger.info("Disconnected from Letta server")
    
    async def get_or_create_agent(self, agent_name: str, agent_config: Dict[str, Any]) -> str:
        """Get existing agent or create new one"""
        try:
            agents = self.client.list_agents()
            
            for agent in agents:
                if agent.name == agent_name:
                    logger.info(f"Found existing agent: {agent_name} ({agent.id})")
                    self.agents[agent_name] = agent.id
                    return agent.id
            
            logger.info(f"Creating new agent: {agent_name}")
            
            agent = self.client.create_agent(
                name=agent_name,
                system=agent_config.get("persona", "You are a helpful coding assistant with persistent memory."),
                tools=agent_config.get("tools", []),
            )
            
            self.agents[agent_name] = agent.id
            logger.info(f"Created agent: {agent_name} ({agent.id})")
            return agent.id
            
        except Exception as e:
            logger.error(f"Error getting/creating agent: {e}")
            raise
    
    async def send_message(self, agent_id: str, message: str) -> Dict[str, Any]:
        """Send message to Letta agent and get response"""
        try:
            response = self.client.send_message(
                agent_id=agent_id,
                message=message,
                role="user"
            )
            
            text_parts = []
            memory_updated = False
            
            for msg in response.messages:
                if hasattr(msg, 'text') and msg.text:
                    text_parts.append(msg.text)
                if hasattr(msg, 'function_call'):
                    if msg.function_call and 'memory' in msg.function_call.name:
                        memory_updated = True
            
            return {
                "text": "
".join(text_parts),
                "memory_updated": memory_updated,
                "reasoning": "",
                "raw_response": response
            }
            
        except Exception as e:
            logger.error(f"Error sending message to agent: {e}")
            raise
EOFMARKER
print_success "Created letta_client_wrapper.py"

# Create main bridge file
cat > acp_letta_bridge.py << 'EOFMARKER'
#!/usr/bin/env python3
"""ACP-to-Letta Bridge Server"""
import sys
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from acp_protocol import ACPHandler
from letta_client_wrapper import LettaClientWrapper
from config import Config

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class ACPLettaBridge:
    """Main bridge server connecting ACP to Letta"""
    
    def __init__(self, config: Config):
        self.config = config
        self.acp_handler = ACPHandler()
        self.letta_client = LettaClientWrapper(config)
        self.agent_id: Optional[str] = None
        self.running = True
        
    async def initialize(self):
        """Initialize connection to Letta server"""
        logger.info("Initializing ACP-Letta Bridge...")
        await self.letta_client.connect()
        self.agent_id = await self.letta_client.get_or_create_agent(
            agent_name=self.config.agent_name,
            agent_config={
                "persona": "You are a helpful coding assistant with persistent memory across sessions.",
                "tools": []
            }
        )
        logger.info(f"Bridge initialized with agent: {self.agent_id}")
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming ACP JSON-RPC request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.debug(f"Received request: {method}")
        
        try:
            if method == "initialize":
                result = await self._handle_initialize(params)
            elif method == "agent/complete":
                result = await self._handle_complete(params)
            elif method == "agent/edit":
                result = await self._handle_edit(params)
            elif method == "shutdown":
                result = await self._handle_shutdown(params)
                self.running = False
            else:
                raise Exception(f"Unknown method: {method}")
                
            return self.acp_handler.success_response(request_id, result)
            
        except Exception as e:
            logger.error(f"Error handling {method}: {e}", exc_info=True)
            return self.acp_handler.error_response(request_id, str(e))
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ACP initialize request"""
        return {
            "protocolVersion": "0.1.0",
            "capabilities": {
                "completion": True,
                "edit": True,
                "memory": True
            },
            "serverInfo": {
                "name": "Letta Agent",
                "version": "1.0.0"
            }
        }
    
    async def _handle_complete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code completion request"""
        prompt = params.get("prompt", "")
        context = params.get("context", {})
        
        message = f"Code completion request:
{prompt}

Context: {json.dumps(context)}"
        response = await self.letta_client.send_message(self.agent_id, message)
        
        return {
            "completion": response.get("text", ""),
            "metadata": {
                "agent_id": self.agent_id,
                "memory_updated": response.get("memory_updated", False)
            }
        }
    
    async def _handle_edit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code editing request"""
        instruction = params.get("instruction", "")
        code = params.get("code", "")
        file_path = params.get("filePath", "")
        
        message = f"""Edit request:
File: {file_path}
Instruction: {instruction}

Current code: