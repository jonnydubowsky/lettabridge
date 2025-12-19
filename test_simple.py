#!/usr/bin/env python3
"""Simple test to verify bridge can initialize"""

import asyncio
import sys
from config import BridgeConfig
from letta_wrapper import LettaClientWrapper

async def test_connection():
    """Test basic connection to Letta"""
    print("Testing Letta connection...")
    
    config = BridgeConfig()
    print(f"Config: {config.letta_base_url}")
    
    client = LettaClientWrapper(config)
    
    try:
        await client.connect()
        print("✓ Connected to Letta server")
        
        # Try to get/create agent
        agent_id = await client.get_or_create_agent(
            agent_name="test_agent",
            agent_config={
                "persona": "You are a test agent",
                "tools": []
            }
        )
        print(f"✓ Agent created/retrieved: {agent_id}")
        
        # Send test message
        response = await client.send_message(
            agent_id=agent_id,
            message="Hello, this is a test message"
        )
        print(f"✓ Message sent, response: {response.get('text', '')[:100]}...")
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    sys.exit(0 if result else 1)
