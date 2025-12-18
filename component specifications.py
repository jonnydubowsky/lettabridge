#!/usr/bin/env python3
"""
ACP Bridge Server - Main entry point
Implements Agent Client Protocol over stdio
"""

import sys
import json
import asyncio
import logging
from typing import Optional, Dict, Any

from letta_client import LettaClientWrapper
from message_handler import MessageHandler
from protocol import ACP_METHODS
from config import BridgeConfig

# Configure logging to stderr (stdout is for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("letta-acp-bridge")


class StdioTransport:
    """Handle JSON-RPC over stdio with Content-Length framing"""
    
    async def read_message(self) -> Optional[Dict[str, Any]]:
        """
        Read Content-Length framed JSON-RPC message from stdin
        
        Format:
        Content-Length: 123\r

        \r

        {json message}
        """
        try:
            # Read headers
            headers = {}
            while True:
                line = sys.stdin.readline()
                if not line:
                    return None
                if line == "\r
" or line == "
":
                    break
                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.strip()] = value.strip()
            
            # Read body based on Content-Length
            content_length = int(headers.get("Content-Length", 0))
            if content_length == 0:
                return None
                
            body = sys.stdin.read(content_length)
            return json.loads(body)
            
        except Exception as e:
            logger.error(f"Error reading message: {e}")
            return None
    
    def write_message(self, message: Dict[str, Any]):
        """Write JSON-RPC message to stdout with Content-Length framing"""
        try:
            body = json.dumps(message)
            content_length = len(body.encode('utf-8'))
            
            output = f"Content-Length: {content_length}\r
\r
{body}"
            sys.stdout.write(output)
            sys.stdout.flush()
            
        except Exception as e:
            logger.error(f"Error writing message: {e}")


class ACPServer:
    """Main ACP server implementation"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.letta_client = LettaClientWrapper(
            base_url=config.letta_base_url,
            api_key=config.letta_api_key
        )
        self.message_handler = MessageHandler(self.letta_client)
        self.transport = StdioTransport()
        
    async def start(self):
        """Main event loop"""
        logger.info("Letta ACP Bridge starting...")
        logger.info(f"Connecting to Letta at {self.config.letta_base_url}")
        
        while True:
            try:
                # Read request
                request = await self.transport.read_message()
                if request is None:
                    logger.info("No more input, shutting down")
                    break
                
                logger.debug(f"Received request: {request.get('method')}")
                
                # Validate JSON-RPC
                if request.get("jsonrpc") != "2.0":
                    self.transport.write_message({
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32600,
                            "message": "Invalid Request"
                        }
                    })
                    continue
                
                # Route to handler
                method = request.get("method")
                handler_name = ACP_METHODS.get(method)
                
                if not handler_name:
                    logger.warning(f"Unknown method: {method}")
                    self.transport.write_message({
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    })
                    continue
                
                # Execute handler
                handler = getattr(self.message_handler, handler_name)
                result = await handler(request.get("params", {}))
                
                # Send response
                self.transport.write_message({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                })
                
                logger.debug(f"Sent response for {method}")
                
            except Exception as e:
                logger.error(f"Error processing request: {e}", exc_info=True)
                self.transport.write_message({
                    "jsonrpc": "2.0",
                    "id": request.get("id", 0),
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    }
                })


async def main():
    config = BridgeConfig()
    server = ACPServer(config)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())