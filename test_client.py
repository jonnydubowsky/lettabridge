"""
Test ACP client for manual testing
Simulates Zed's communication with the bridge
"""

import subprocess
import json
import sys


def send_request(process, request_id, method, params=None):
    """Send JSON-RPC request to bridge server"""
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method
    }
    if params:
        request["params"] = params
    
    # Serialize
    body = json.dumps(request)
    content_length = len(body.encode('utf-8'))
    
    # Send with Content-Length framing
    message = f"Content-Length: {content_length}\r
\r
{body}"
    process.stdin.write(message)
    process.stdin.flush()
    
    # Read response
    # (simplified - real implementation needs proper framing parser)
    return read_response(process)


def read_response(process):
    """Read JSON-RPC response"""
    # Read headers
    while True:
        line = process.stdout.readline().decode('utf-8')
        if line == "\r
" or line == "
":
            break
        if line.startswith("Content-Length:"):
            length = int(line.split(":")[1].strip())
    
    # Read body
    body = process.stdout.read(length).decode('utf-8')
    return json.loads(body)


def main():
    # Start bridge server
    process = subprocess.Popen(
        ["python", "-m", "src.acp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Test 1: Initialize
        print("Test 1: Initialize")
        response = send_request(process, 1, "initialize")
        print(f"Response: {response}
")
        
        # Test 2: Create agent
        print("Test 2: Create agent")
        response = send_request(process, 2, "agent/create", {
            "name": "test-agent",
            "instructions": "You are a helpful coding assistant"
        })
        agent_id = response["result"]["agent_id"]
        print(f"Created agent: {agent_id}
")
        
        # Test 3: Send message
        print("Test 3: Send message")
        response = send_request(process, 3, "agent/message", {
            "agent_id": agent_id,
            "message": "Hello! Can you help me write a Python function?"
        })
        print(f"Agent response: {response['result']['response']}
")
        
        # Test 4: List agents
        print("Test 4: List agents")
        response = send_request(process, 4, "agent/list")
        print(f"Agents: {response}
")
        
    finally:
        process.terminate()


if __name__ == "__main__":
    main()