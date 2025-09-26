"""
PlayPark FastAPI Application Entry Point
"""
import logging
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.config import settings
from app.db.mongo import get_database, close_database
from app.middlewares.logging import LoggingMiddleware
from app.middlewares.response import ResponseEnvelopeMiddleware
from app.routers import (
    auth,
    users,
    roles,
    catalog,
    sales,
    tickets,
    shifts,
    reports,
    settings as settings_router,
    webhooks,
    sync,
    provider,
    enrollment,
    deep_link,
    stores,
)
from app.utils.errors import PlayParkException, create_error_response
from app.utils.logging import setup_logging

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    # Startup
    logger.info("Starting PlayPark API", version=settings.API_VERSION)
    
    # Initialize database connection
    await get_database()
    logger.info("Database connection established")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PlayPark API")
    await close_database()
    logger.info("Database connection closed")


# Create FastAPI application
app = FastAPI(
    title="PlayPark API",
    description="Modern FastAPI backend for PlayPark POS system",
    version=settings.API_VERSION,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# Security middleware
if settings.ALLOWED_HOSTS:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=None,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ResponseEnvelopeMiddleware)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to all requests"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Global exception handler
@app.exception_handler(PlayParkException)
async def playpark_exception_handler(request: Request, exc: PlayParkException):
    """Handle custom PlayPark exceptions"""
    return create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        status_code=exc.status_code,
        request_id=getattr(request.state, "request_id", None),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(
        "Unexpected error",
        error=str(exc),
        error_type=type(exc).__name__,
        request_id=getattr(request.state, "request_id", None),
        exc_info=exc,
    )
    
    return create_error_response(
        error_code="E_INTERNAL_ERROR",
        message="An unexpected error occurred",
        details={"error_type": type(exc).__name__},
        status_code=500,
        request_id=getattr(request.state, "request_id", None),
    )


# Health check endpoints
@app.get("/healthz")
async def health_check():
    """Kubernetes-style health check"""
    try:
        # Check database connection
        db = await get_database()
        await db.command("ping")
        
        return {"ok": True, "status": "healthy"}
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={"ok": False, "status": "unhealthy", "error": str(e)}
        )


@app.get("/readyz")
async def readiness_check():
    """Kubernetes-style readiness check"""
    try:
        # Check if all services are ready
        db = await get_database()
        await db.command("ping")
        
        return {"ok": True, "status": "ready"}
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={"ok": False, "status": "not_ready", "error": str(e)}
        )


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(enrollment.router, tags=["Enrollment"])
app.include_router(deep_link.router, tags=["Deep Links"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(stores.router, prefix="/api/v1", tags=["Stores"])
app.include_router(catalog.router, prefix="/api/v1/catalog", tags=["Catalog"])
app.include_router(sales.router, prefix="/api/v1/sales", tags=["Sales"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["Tickets"])
app.include_router(shifts.router, prefix="/api/v1/shifts", tags=["Shifts"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(sync.router, prefix="/api/v1/sync", tags=["Sync"])
app.include_router(provider.router, prefix="/provider", tags=["Provider"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
