"""
Audit Models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class EventSeverity(str, Enum):
    """Event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventType(str, Enum):
    """Common event types"""
    # Authentication events
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    TOKEN_REFRESH = "auth.token.refresh"
    PASSWORD_CHANGE = "auth.password.change"
    PASSWORD_RESET = "auth.password.reset"
    
    # Sales events
    SALE_CREATED = "sale.created"
    SALE_CANCELLED = "sale.cancelled"
    SALE_REFUNDED = "sale.refunded"
    SALE_REPRINTED = "sale.reprinted"
    
    # Ticket events
    TICKET_GENERATED = "ticket.generated"
    TICKET_REDEEMED = "ticket.redeemed"
    TICKET_EXPIRED = "ticket.expired"
    TICKET_REFUNDED = "ticket.refunded"
    
    # Shift events
    SHIFT_OPENED = "shift.opened"
    SHIFT_CLOSED = "shift.closed"
    
    # Device events
    DEVICE_REGISTERED = "device.registered"
    DEVICE_SUSPENDED = "device.suspended"
    DEVICE_ACTIVATED = "device.activated"
    
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_SUSPENDED = "user.suspended"
    
    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    CONFIGURATION_CHANGE = "config.changed"


class AuditLog(BaseDocument):
    """Audit log model"""
    
    log_id: str = Field(..., description="Unique log identifier")
    tenant_id: Optional[str] = Field(default=None, description="Tenant ID")
    store_id: Optional[str] = Field(default=None, description="Store ID")
    event_type: EventType = Field(..., description="Event type")
    actor_id: Optional[str] = Field(default=None, description="Actor user ID")
    actor_type: str = Field(default="user", description="Actor type: user, system, device")
    device_id: Optional[str] = Field(default=None, description="Device ID")
    ip_address: Optional[str] = Field(default=None, description="IP address")
    user_agent: Optional[str] = Field(default=None, description="User agent")
    severity: EventSeverity = Field(default=EventSeverity.LOW, description="Event severity")
    message: str = Field(..., description="Event message")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    
    class Config:
        collection = "audit_logs"


class AuditLogCreate(BaseModel):
    """Audit log creation model"""
    
    tenant_id: Optional[str] = Field(default=None, description="Tenant ID")
    store_id: Optional[str] = Field(default=None, description="Store ID")
    event_type: EventType = Field(..., description="Event type")
    actor_id: Optional[str] = Field(default=None, description="Actor user ID")
    actor_type: str = Field(default="user", description="Actor type")
    device_id: Optional[str] = Field(default=None, description="Device ID")
    ip_address: Optional[str] = Field(default=None, description="IP address")
    user_agent: Optional[str] = Field(default=None, description="User agent")
    severity: EventSeverity = Field(default=EventSeverity.LOW, description="Event severity")
    message: str = Field(..., description="Event message")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AuditLogResponse(BaseModel):
    """Audit log response model"""
    
    log_id: str = Field(..., description="Log ID")
    tenant_id: Optional[str] = Field(..., description="Tenant ID")
    store_id: Optional[str] = Field(..., description="Store ID")
    event_type: EventType = Field(..., description="Event type")
    actor_id: Optional[str] = Field(..., description="Actor user ID")
    actor_type: str = Field(..., description="Actor type")
    device_id: Optional[str] = Field(..., description="Device ID")
    ip_address: Optional[str] = Field(..., description="IP address")
    user_agent: Optional[str] = Field(..., description="User agent")
    severity: EventSeverity = Field(..., description="Event severity")
    message: str = Field(..., description="Event message")
    payload: Dict[str, Any] = Field(..., description="Event payload")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")
    timestamp: datetime = Field(..., description="Event timestamp")


class AuditLogQuery(BaseModel):
    """Audit log query model"""
    
    tenant_id: Optional[str] = Field(default=None, description="Filter by tenant ID")
    store_id: Optional[str] = Field(default=None, description="Filter by store ID")
    event_type: Optional[EventType] = Field(default=None, description="Filter by event type")
    actor_id: Optional[str] = Field(default=None, description="Filter by actor ID")
    device_id: Optional[str] = Field(default=None, description="Filter by device ID")
    severity: Optional[EventSeverity] = Field(default=None, description="Filter by severity")
    start_date: Optional[datetime] = Field(default=None, description="Start date filter")
    end_date: Optional[datetime] = Field(default=None, description="End date filter")
    limit: int = Field(default=100, ge=1, le=1000, description="Result limit")
    offset: int = Field(default=0, ge=0, description="Result offset")


class AuditLogSummary(BaseModel):
    """Audit log summary model"""
    
    total_events: int = Field(..., description="Total event count")
    events_by_type: Dict[str, int] = Field(..., description="Events by type")
    events_by_severity: Dict[str, int] = Field(..., description="Events by severity")
    events_by_actor: Dict[str, int] = Field(..., description="Events by actor")
    recent_events: List[AuditLogResponse] = Field(..., description="Recent events")


class SystemSettings(BaseDocument):
    """System settings model"""
    
    setting_id: str = Field(..., description="Unique setting identifier")
    tenant_id: Optional[str] = Field(default=None, description="Tenant ID (null for global)")
    category: str = Field(..., description="Setting category")
    key: str = Field(..., description="Setting key")
    value: Any = Field(..., description="Setting value")
    description: Optional[str] = Field(default=None, description="Setting description")
    is_encrypted: bool = Field(default=False, description="Encrypted setting flag")
    updated_by: Optional[str] = Field(default=None, description="Last updater user ID")
    
    class Config:
        collection = "system_settings"


class Webhook(BaseDocument):
    """Webhook model"""
    
    webhook_id: str = Field(..., description="Unique webhook identifier")
    tenant_id: str = Field(..., description="Tenant ID")
    name: str = Field(..., description="Webhook name")
    url: str = Field(..., description="Webhook URL")
    events: List[str] = Field(..., description="Subscribed events")
    secret: str = Field(..., description="Webhook secret")
    active: bool = Field(default=True, description="Webhook active status")
    retry_count: int = Field(default=3, description="Retry count")
    timeout_seconds: int = Field(default=30, description="Timeout in seconds")
    last_triggered: Optional[datetime] = Field(default=None, description="Last trigger timestamp")
    created_by: str = Field(..., description="Creator user ID")
    
    class Config:
        collection = "webhooks"


class WebhookEvent(BaseDocument):
    """Webhook event model"""
    
    event_id: str = Field(..., description="Unique event identifier")
    webhook_id: str = Field(..., description="Webhook ID")
    event_type: str = Field(..., description="Event type")
    payload: Dict[str, Any] = Field(..., description="Event payload")
    status: str = Field(default="pending", description="Delivery status")
    response_status: Optional[int] = Field(default=None, description="HTTP response status")
    response_body: Optional[str] = Field(default=None, description="Response body")
    retry_count: int = Field(default=0, description="Retry count")
    next_retry: Optional[datetime] = Field(default=None, description="Next retry timestamp")
    delivered_at: Optional[datetime] = Field(default=None, description="Delivery timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        collection = "webhook_events"
