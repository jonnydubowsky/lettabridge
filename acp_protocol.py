"""
ACP (Agent Client Protocol) handler
Implements JSON-RPC protocol for Zed editor communication
"""

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
        """Build JSON-RPC notification (no response expected)"""
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }