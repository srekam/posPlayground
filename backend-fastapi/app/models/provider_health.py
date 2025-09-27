"""
Provider Health Models
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .core import BaseDocument


class AlertStatus(str, Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertSeverity(str, Enum):
    """Alert severity"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeviceHeartbeat(BaseDocument):
    """Device heartbeat model"""
    
    device_id: str = Field(..., description="Device ID")
    tenant_id: str = Field(..., description="Parent tenant ID")
    store_id: str = Field(..., description="Parent store ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Heartbeat timestamp")
    status: str = Field(default="online", description="Device status")
    battery_level: Optional[int] = Field(default=None, ge=0, le=100, description="Battery level percentage")
    signal_strength: Optional[int] = Field(default=None, description="Signal strength")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        collection = "device_heartbeats"


class ProviderAlert(BaseDocument):
    """Provider alert model"""
    
    alert_id: str = Field(..., description="Unique alert identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    device_id: Optional[str] = Field(default=None, description="Related device ID")
    type: str = Field(..., description="Alert type")
    severity: AlertSeverity = Field(..., description="Alert severity")
    status: AlertStatus = Field(default=AlertStatus.ACTIVE, description="Alert status")
    message: str = Field(..., description="Alert message")
    first_seen: datetime = Field(default_factory=datetime.utcnow, description="First seen timestamp")
    last_seen: datetime = Field(default_factory=datetime.utcnow, description="Last seen timestamp")
    acknowledged_by: Optional[str] = Field(default=None, description="Acknowledged by user ID")
    acknowledged_at: Optional[datetime] = Field(default=None, description="Acknowledged timestamp")
    resolved_by: Optional[str] = Field(default=None, description="Resolved by user ID")
    resolved_at: Optional[datetime] = Field(default=None, description="Resolved timestamp")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        collection = "provider_alerts"


class ProviderAudit(BaseDocument):
    """Provider audit model"""
    
    audit_id: str = Field(..., description="Unique audit identifier")
    tenant_id: str = Field(..., description="Parent tenant ID")
    action: str = Field(..., description="Audit action")
    actor_id: str = Field(..., description="Actor user ID")
    target_type: str = Field(..., description="Target type")
    target_id: str = Field(..., description="Target ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Audit timestamp")
    details: Dict[str, Any] = Field(default_factory=dict, description="Audit details")
    
    class Config:
        collection = "provider_audits"


class ProviderMetricsDaily(BaseDocument):
    """Provider daily metrics model"""
    
    tenant_id: str = Field(..., description="Parent tenant ID")
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    metrics: Dict[str, Any] = Field(..., description="Daily metrics")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    
    class Config:
        collection = "provider_metrics_daily"


class HeartbeatCreateRequest(BaseModel):
    """Heartbeat creation request"""
    
    status: str = Field(default="online", description="Device status")
    battery_level: Optional[int] = Field(default=None, ge=0, le=100, description="Battery level percentage")
    signal_strength: Optional[int] = Field(default=None, description="Signal strength")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AlertAcknowledgeRequest(BaseModel):
    """Alert acknowledge request"""
    
    notes: Optional[str] = Field(default=None, description="Acknowledgment notes")


class AlertResolveRequest(BaseModel):
    """Alert resolve request"""
    
    resolution: str = Field(..., description="Resolution details")
    notes: Optional[str] = Field(default=None, description="Resolution notes")


class ProviderOverviewResponse(BaseModel):
    """Provider overview response"""
    
    tenant_id: str = Field(..., description="Tenant ID")
    total_devices: int = Field(..., description="Total devices")
    online_devices: int = Field(..., description="Online devices")
    offline_devices: int = Field(..., description="Offline devices")
    active_alerts: int = Field(..., description="Active alerts")
    critical_alerts: int = Field(..., description="Critical alerts")
    last_updated: datetime = Field(..., description="Last updated timestamp")


class AlertResponse(BaseModel):
    """Alert response"""
    
    alert_id: str = Field(..., description="Alert ID")
    type: str = Field(..., description="Alert type")
    severity: AlertSeverity = Field(..., description="Alert severity")
    status: AlertStatus = Field(..., description="Alert status")
    message: str = Field(..., description="Alert message")
    first_seen: datetime = Field(..., description="First seen timestamp")
    last_seen: datetime = Field(..., description="Last seen timestamp")
    acknowledged_by: Optional[str] = Field(..., description="Acknowledged by user ID")
    acknowledged_at: Optional[datetime] = Field(..., description="Acknowledged timestamp")
    resolved_by: Optional[str] = Field(..., description="Resolved by user ID")
    resolved_at: Optional[datetime] = Field(..., description="Resolved timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
