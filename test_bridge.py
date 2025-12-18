#!/usr/bin/env python3
"""
Test utilities for ACP-Letta Bridge
"""

import json
import subprocess
import sys


def send_request(process, method: str, params: dict = None, request_id: int = 1):
    """Send JSON-RPC request to bridge"""
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": request_id
    }
    
    # Send to stdin
    process.stdin.write(json.dumps(request) + '
')
    process.stdin.flush()
    
    # Read response from stdout
    response_line = process.stdout.readline()
    return json.loads(response_line)


def test_initialize():
    """Test initialize request"""
    print("Testing initialize...")
    
    # Start bridge process
    process = subprocess.Popen(
        ['python3', 'acp_letta_bridge.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Send initialize
        response = send_request(process, "initialize", {
            "processId": 12345,
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        })
        
        print("Initialize response:", json.dumps(response, indent=2))
        
        # Send completion request
        response = send_request(process, "agent/complete", {
            "prompt": "def factorial(n):",
            "context": {"language": "python"}
        }, request_id=2)
        
        print("Completion response:", json.dumps(response, indent=2))
        
        # Shutdown
        response = send_request(process, "shutdown", {}, request_id=3)
        print("Shutdown response:", json.dumps(response, indent=2))
        
    finally:
        process.terminate()
        process.wait()


if __name__ == "__main__":
    test_initialize()