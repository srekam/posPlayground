"""
Logging Middleware
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.utils.logging import log_request

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and response with logging"""
        
        # Generate request ID if not present
        if not hasattr(request.state, "request_id"):
            request.state.request_id = str(uuid.uuid4())
        
        # Get request details
        start_time = time.time()
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else ""
        user_agent = request.headers.get("user-agent", "")
        client_ip = request.client.host if request.client else "unknown"
        
        # Extract user ID if available (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        
        # Log request
        logger.info(
            "HTTP request started",
            request_id=request.state.request_id,
            method=method,
            path=path,
            query_params=query_params,
            client_ip=client_ip,
            user_agent=user_agent,
            user_id=user_id
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            log_request(
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                user_id=user_id,
                request_id=request.state.request_id
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request.state.request_id
            
            return response
            
        except Exception as e:
            # Calculate duration for error case
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                "HTTP request failed",
                request_id=request.state.request_id,
                method=method,
                path=path,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=duration_ms,
                user_id=user_id,
                exc_info=e
            )
            
            # Re-raise the exception
            raise
