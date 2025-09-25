"""
Response Envelope Middleware
"""
import json
from datetime import datetime
from typing import Callable, Any, Dict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.schemas.common import SuccessResponse, ErrorResponse


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    """Middleware for wrapping responses in standard envelope format"""
    
    def __init__(self, app: ASGIApp, exclude_paths: list[str] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/healthz",
            "/readyz",
            "/metrics"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and wrap response in envelope"""
        
        # Skip envelope for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Process request
        response = await call_next(request)
        
        # Only wrap JSON responses
        if not isinstance(response, JSONResponse):
            return response
        
        # Get response body
        response_body = response.body
        if not response_body:
            return response
        
        try:
            # Parse response body
            body_data = json.loads(response_body.decode())
            
            # Skip if already wrapped
            if isinstance(body_data, dict) and "server_time" in body_data:
                return response
            
            # Wrap in envelope
            if response.status_code < 400:
                # Success response
                envelope = SuccessResponse(
                    data=body_data,
                    request_id=getattr(request.state, "request_id", None)
                )
            else:
                # Error response - check if already in error format
                if isinstance(body_data, dict) and "error" in body_data:
                    # Already in error format, just add metadata
                    envelope_data = {
                        "server_time": datetime.utcnow().isoformat(),
                        "request_id": getattr(request.state, "request_id", None),
                        **body_data
                    }
                else:
                    # Convert to error format
                    envelope = ErrorResponse(
                        error="E_UNKNOWN_ERROR",
                        message=str(body_data) if not isinstance(body_data, dict) else "An error occurred",
                        details=body_data if isinstance(body_data, dict) else None
                    )
                    envelope_data = envelope.dict()
                    # Add server metadata
                    envelope_data["server_time"] = datetime.utcnow().isoformat()
                    envelope_data["request_id"] = getattr(request.state, "request_id", None)
                
                # Create new response with envelope
                return JSONResponse(
                    content=envelope_data,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            
            # Create new response with envelope
            return JSONResponse(
                content=envelope.dict(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
        except (json.JSONDecodeError, TypeError) as e:
            # If we can't parse the response, return as-is
            return response
