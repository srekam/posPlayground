"""
Provider Health Repository
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .base import BaseRepository
from app.models.provider_health import (
    DeviceHeartbeat, ProviderAlert, ProviderAudit, ProviderMetricsDaily
)


class DeviceHeartbeatRepository(BaseRepository[DeviceHeartbeat]):
    """Device heartbeat repository"""
    
    def __init__(self):
        super().__init__("device_heartbeats", DeviceHeartbeat)
    
    async def record_heartbeat(
        self,
        device_id: str,
        tenant_id: str,
        store_id: str,
        status: str = "online",
        battery_level: Optional[int] = None,
        signal_strength: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> DeviceHeartbeat:
        """Record device heartbeat"""
        now = datetime.utcnow()
        heartbeat_data = {
            "device_id": device_id,
            "tenant_id": tenant_id,
            "store_id": store_id,
            "timestamp": now,
            "status": status,
            "battery_level": battery_level,
            "signal_strength": signal_strength,
            "meta": meta or {},
            "created_at": now,
            "updated_at": now
        }
        
        result = await self.collection.insert_one(heartbeat_data)
        heartbeat_data["_id"] = result.inserted_id
        return DeviceHeartbeat(**heartbeat_data)
    
    async def get_latest_heartbeat(self, device_id: str) -> Optional[DeviceHeartbeat]:
        """Get latest heartbeat for device"""
        query = {"device_id": device_id}
        sort = [("timestamp", -1)]
        results = await self.get_many(query, limit=1, sort=sort)
        return results[0] if results else None
    
    async def get_offline_devices(self, timeout_minutes: int = 120) -> List[DeviceHeartbeat]:
        """Get devices that haven't sent heartbeat within timeout"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        
        # Get latest heartbeat for each device
        pipeline = [
            {"$sort": {"device_id": 1, "timestamp": -1}},
            {"$group": {
                "_id": "$device_id",
                "latest_heartbeat": {"$first": "$$ROOT"}
            }},
            {"$match": {
                "latest_heartbeat.timestamp": {"$lt": cutoff_time}
            }},
            {"$replaceRoot": {"newRoot": "$latest_heartbeat"}}
        ]
        
        results = await self.aggregate(pipeline)
        return [DeviceHeartbeat(**result) for result in results]
    
    async def cleanup_old_heartbeats(self, days: int = 30) -> int:
        """Clean up old heartbeats"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = {"timestamp": {"$lt": cutoff_date}}
        
        result = await self.collection.delete_many(query)
        return result.deleted_count


class ProviderAlertRepository(BaseRepository[ProviderAlert]):
    """Provider alert repository"""
    
    def __init__(self):
        super().__init__("provider_alerts", ProviderAlert)
    
    async def create_alert(
        self,
        alert_id: str,
        tenant_id: str,
        alert_type: str,
        severity: str,
        message: str,
        device_id: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> ProviderAlert:
        """Create provider alert"""
        now = datetime.utcnow()
        alert_data = {
            "alert_id": alert_id,
            "tenant_id": tenant_id,
            "device_id": device_id,
            "type": alert_type,
            "severity": severity,
            "status": "active",
            "message": message,
            "first_seen": now,
            "last_seen": now,
            "meta": meta or {},
            "created_at": now,
            "updated_at": now
        }
        
        result = await self.collection.insert_one(alert_data)
        alert_data["_id"] = result.inserted_id
        return ProviderAlert(**alert_data)
    
    async def get_active_alerts(
        self,
        tenant_id: Optional[str] = None,
        severity: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProviderAlert]:
        """Get active alerts"""
        query = {"status": "active"}
        if tenant_id:
            query["tenant_id"] = tenant_id
        if severity:
            query["severity"] = severity
        
        sort = [("severity", 1), ("last_seen", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
        notes: Optional[str] = None
    ) -> Optional[ProviderAlert]:
        """Acknowledge alert"""
        now = datetime.utcnow()
        update_data = {
            "status": "acknowledged",
            "acknowledged_by": acknowledged_by,
            "acknowledged_at": now
        }
        if notes:
            update_data["notes"] = notes
        
        return await self.update_by_id(alert_id, update_data, "alert_id")
    
    async def resolve_alert(
        self,
        alert_id: str,
        resolved_by: str,
        resolution: str,
        notes: Optional[str] = None
    ) -> Optional[ProviderAlert]:
        """Resolve alert"""
        now = datetime.utcnow()
        update_data = {
            "status": "resolved",
            "resolved_by": resolved_by,
            "resolved_at": now,
            "resolution": resolution
        }
        if notes:
            update_data["notes"] = notes
        
        return await self.update_by_id(alert_id, update_data, "alert_id")
    
    async def update_alert_last_seen(self, alert_id: str) -> Optional[ProviderAlert]:
        """Update alert last seen timestamp"""
        return await self.update_by_id(
            alert_id,
            {"last_seen": datetime.utcnow()},
            "alert_id"
        )


class ProviderAuditRepository(BaseRepository[ProviderAudit]):
    """Provider audit repository"""
    
    def __init__(self):
        super().__init__("provider_audits", ProviderAudit)
    
    async def log_audit(
        self,
        audit_id: str,
        tenant_id: str,
        action: str,
        actor_id: str,
        target_type: str,
        target_id: str,
        details: Optional[Dict[str, Any]] = None
    ) -> ProviderAudit:
        """Log audit entry"""
        now = datetime.utcnow()
        audit_data = {
            "audit_id": audit_id,
            "tenant_id": tenant_id,
            "action": action,
            "actor_id": actor_id,
            "target_type": target_type,
            "target_id": target_id,
            "timestamp": now,
            "details": details or {},
            "created_at": now,
            "updated_at": now
        }
        
        result = await self.collection.insert_one(audit_data)
        audit_data["_id"] = result.inserted_id
        return ProviderAudit(**audit_data)
    
    async def get_audit_trail(
        self,
        tenant_id: str,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProviderAudit]:
        """Get audit trail"""
        query = {"tenant_id": tenant_id}
        if target_type:
            query["target_type"] = target_type
        if target_id:
            query["target_id"] = target_id
        
        sort = [("timestamp", -1)]
        return await self.get_many(query, skip=skip, limit=limit, sort=sort)
    
    async def cleanup_old_audits(self, days: int = 365) -> int:
        """Clean up old audit entries"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = {"timestamp": {"$lt": cutoff_date}}
        
        result = await self.collection.delete_many(query)
        return result.deleted_count


class ProviderMetricsDailyRepository(BaseRepository[ProviderMetricsDaily]):
    """Provider daily metrics repository"""
    
    def __init__(self):
        super().__init__("provider_metrics_daily", ProviderMetricsDaily)
    
    async def store_daily_metrics(
        self,
        tenant_id: str,
        date: str,
        metrics: Dict[str, Any]
    ) -> ProviderMetricsDaily:
        """Store daily metrics"""
        now = datetime.utcnow()
        metrics_data = {
            "tenant_id": tenant_id,
            "date": date,
            "metrics": metrics,
            "generated_at": now,
            "created_at": now,
            "updated_at": now
        }
        
        result = await self.collection.insert_one(metrics_data)
        metrics_data["_id"] = result.inserted_id
        return ProviderMetricsDaily(**metrics_data)
    
    async def get_metrics_by_date_range(
        self,
        tenant_id: str,
        start_date: str,
        end_date: str
    ) -> List[ProviderMetricsDaily]:
        """Get metrics by date range"""
        query = {
            "tenant_id": tenant_id,
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        sort = [("date", 1)]
        return await self.get_many(query, sort=sort)
    
    async def cleanup_old_metrics(self, days: int = 365) -> int:
        """Clean up old metrics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
        
        query = {"date": {"$lt": cutoff_date_str}}
        result = await self.collection.delete_many(query)
        return result.deleted_count
