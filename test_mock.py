#!/usr/bin/env python3
"""
Mock test for bridge - tests our code without needing Letta server
"""

import sys
import json
from unittest.mock import Mock, AsyncMock, patch
from config import BridgeConfig
from letta_wrapper import LettaClientWrapper
from acp_letta_bridge import ACPLettaBridge

def test_config():
    """Test configuration loads"""
    print("Testing configuration...")
    config = BridgeConfig()
    assert config.letta_base_url == "http://localhost:8283"
    assert config.agent_name == "zed_coding_assistant"
    print("✓ Config loaded correctly")

def test_imports():
    """Test all modules import without errors"""
    print("\nTesting imports...")
    try:
        import acp_protocol
        import protocol
        import message_handler
        print("✓ All modules import successfully")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

async def test_bridge_initialization():
    """Test bridge can be initialized"""
    print("\nTesting bridge initialization...")
    
    config = BridgeConfig()
    
    # Mock the Letta client
    with patch('letta_wrapper.Letta') as MockLetta:
        mock_client = Mock()
        mock_client.agents = Mock()
        mock_client.agents.list = Mock(return_value=[])
        mock_client.agents.create = Mock(return_value=Mock(id="test-agent-123"))
        MockLetta.return_value = mock_client
        
        # Create bridge
        bridge = ACPLettaBridge(config)
        assert bridge is not None
        print("✓ Bridge object created")
        
        # Initialize bridge (with mocked Letta)
        await bridge.initialize()
        assert bridge.agent_id == "test-agent-123"
        print(f"✓ Bridge initialized with agent: {bridge.agent_id}")
        
        return True

async def test_request_handling():
    """Test bridge can handle JSON-RPC requests"""
    print("\nTesting request handling...")
    
    config = BridgeConfig()
    
    with patch('letta_wrapper.Letta') as MockLetta:
        mock_client = Mock()
        mock_client.agents = Mock()
        mock_client.agents.list = Mock(return_value=[])
        mock_client.agents.create = Mock(return_value=Mock(id="test-agent-123"))
        mock_client.agents.messages = Mock()
        mock_client.agents.messages.send = Mock(return_value=Mock(
            messages=[Mock(text="Hello from Letta!")]
        ))
        MockLetta.return_value = mock_client
        
        bridge = ACPLettaBridge(config)
        await bridge.initialize()
        
        # Test initialize request
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {},
            "id": 1
        }
        response = await bridge.handle_request(request)
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        print("✓ Initialize request handled")
        
        # Test completion request
        request = {
            "jsonrpc": "2.0",
            "method": "agent/complete",
            "params": {
                "prompt": "def hello():",
                "context": {"language": "python"}
            },
            "id": 2
        }
        response = await bridge.handle_request(request)
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        assert "result" in response
        print("✓ Completion request handled")
        
        return True

async def run_tests():
    """Run all tests"""
    print("=" * 50)
    print("Mock Testing - ACP-Letta Bridge")
    print("=" * 50)
    
    # Sync tests
    test_config()
    if not test_imports():
        return False
    
    # Async tests
    if not await test_bridge_initialization():
        return False
    
    if not await test_request_handling():
        return False
    
    print("\n" + "=" * 50)
    print("✓ All tests passed!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(run_tests())
    sys.exit(0 if result else 1)
