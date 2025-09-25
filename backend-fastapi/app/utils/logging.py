"""
Logging Configuration
"""
import logging
import sys
from typing import Any, Dict
import structlog
from app.config import settings


def setup_logging() -> None:
    """Setup structured logging configuration"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            _add_request_id,
            _format_log_record,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)


def _add_request_id(logger, method_name, event_dict):
    """Add request ID to log context"""
    # This will be populated by middleware
    return event_dict


def _format_log_record(logger, method_name, event_dict):
    """Format log record based on environment"""
    
    if settings.LOG_FORMAT == "json":
        return structlog.processors.JSONRenderer()(logger, method_name, event_dict)
    else:
        # Console format
        timestamp = event_dict.get("timestamp", "")
        level = event_dict.get("level", "").upper()
        logger_name = event_dict.get("logger", "")
        message = event_dict.get("event", "")
        
        # Build log line
        log_parts = [timestamp, level, logger_name, message]
        
        # Add additional fields
        for key, value in event_dict.items():
            if key not in ["timestamp", "level", "logger", "event"]:
                log_parts.append(f"{key}={value}")
        
        return " ".join(str(part) for part in log_parts if part)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger"""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class for adding logging to any class"""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class"""
        return get_logger(self.__class__.__name__)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: str = None,
    request_id: str = None,
    **kwargs
) -> None:
    """Log HTTP request"""
    
    logger = get_logger("http.request")
    
    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if request_id:
        log_data["request_id"] = request_id
    
    log_data.update(kwargs)
    
    if status_code >= 400:
        logger.warning("HTTP request completed with error", **log_data)
    else:
        logger.info("HTTP request completed", **log_data)


def log_error(
    error: Exception,
    context: Dict[str, Any] = None,
    user_id: str = None,
    request_id: str = None
) -> None:
    """Log application error"""
    
    logger = get_logger("app.error")
    
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    if context:
        log_data.update(context)
    
    if user_id:
        log_data["user_id"] = user_id
    
    if request_id:
        log_data["request_id"] = request_id
    
    logger.error("Application error occurred", **log_data, exc_info=error)


def log_security_event(
    event_type: str,
    user_id: str = None,
    ip_address: str = None,
    user_agent: str = None,
    details: Dict[str, Any] = None
) -> None:
    """Log security-related event"""
    
    logger = get_logger("security.event")
    
    log_data = {
        "event_type": event_type,
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if ip_address:
        log_data["ip_address"] = ip_address
    
    if user_agent:
        log_data["user_agent"] = user_agent
    
    if details:
        log_data.update(details)
    
    logger.warning("Security event", **log_data)


def log_business_event(
    event_type: str,
    tenant_id: str = None,
    store_id: str = None,
    user_id: str = None,
    details: Dict[str, Any] = None
) -> None:
    """Log business-related event"""
    
    logger = get_logger("business.event")
    
    log_data = {
        "event_type": event_type,
    }
    
    if tenant_id:
        log_data["tenant_id"] = tenant_id
    
    if store_id:
        log_data["store_id"] = store_id
    
    if user_id:
        log_data["user_id"] = user_id
    
    if details:
        log_data.update(details)
    
    logger.info("Business event", **log_data)


def log_performance(
    operation: str,
    duration_ms: float,
    success: bool = True,
    details: Dict[str, Any] = None
) -> None:
    """Log performance metrics"""
    
    logger = get_logger("performance")
    
    log_data = {
        "operation": operation,
        "duration_ms": duration_ms,
        "success": success,
    }
    
    if details:
        log_data.update(details)
    
    logger.info("Performance metric", **log_data)
