"""
Provider Health Router
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from ulid import ULID

from app.models.provider_health import (
    DeviceHeartbeat, ProviderAlert, HeartbeatCreateRequest,
    AlertAcknowledgeRequest, AlertResolveRequest, ProviderOverviewResponse, AlertResponse
)
from app.repositories.provider_health import (
    DeviceHeartbeatRepository, ProviderAlertRepository, ProviderAuditRepository
)
from app.utils.errors import PlayParkException, ErrorCode
from app.deps import get_current_user, get_current_device, get_db

router = APIRouter()


@router.post("/heartbeats")
async def record_heartbeat(
    heartbeat_data: HeartbeatCreateRequest,
    device = Depends(get_current_device),
    db = Depends(get_db)
):
    """Record device heartbeat"""
    try:
        heartbeat_repo = DeviceHeartbeatRepository()
        
        # Record heartbeat
        heartbeat = await heartbeat_repo.record_heartbeat(
            device_id=device["device_id"],
            tenant_id=device["tenant_id"],
            store_id=device["store_id"],
            status=heartbeat_data.status,
            battery_level=heartbeat_data.battery_level,
            signal_strength=heartbeat_data.signal_strength,
            meta=heartbeat_data.meta
        )
        
        return {
            "heartbeat_id": str(heartbeat.id),
            "device_id": heartbeat.device_id,
            "timestamp": heartbeat.timestamp,
            "status": heartbeat.status,
            "message": "Heartbeat recorded successfully"
        }
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to record heartbeat",
            details={"error": str(e)}
        )


@router.get("/overview", response_model=ProviderOverviewResponse)
async def get_provider_overview(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get provider overview"""
    try:
        heartbeat_repo = DeviceHeartbeatRepository()
        alert_repo = ProviderAlertRepository()
        
        # Get offline devices (no heartbeat in last 2 minutes)
        offline_devices = await heartbeat_repo.get_offline_devices(timeout_minutes=2)
        
        # Get active alerts
        active_alerts = await alert_repo.get_active_alerts(
            tenant_id=current_user.tenant_id
        )
        
        # Count alerts by severity
        critical_alerts = len([a for a in active_alerts if a.severity == "critical"])
        
        # Calculate device counts (simplified)
        total_devices = 10  # Would be calculated from actual device count
        online_devices = total_devices - len(offline_devices)
        
        return ProviderOverviewResponse(
            tenant_id=current_user.tenant_id,
            total_devices=total_devices,
            online_devices=online_devices,
            offline_devices=len(offline_devices),
            active_alerts=len(active_alerts),
            critical_alerts=critical_alerts,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to get provider overview",
            details={"error": str(e)}
        )


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get provider alerts"""
    try:
        alert_repo = ProviderAlertRepository()
        
        # Get active alerts with optional filters
        alerts = await alert_repo.get_active_alerts(
            tenant_id=current_user.tenant_id,
            severity=severity,
            skip=skip,
            limit=limit
        )
        
        return [
            AlertResponse(
                alert_id=a.alert_id,
                type=a.type,
                severity=a.severity,
                status=a.status,
                message=a.message,
                first_seen=a.first_seen,
                last_seen=a.last_seen,
                acknowledged_by=a.acknowledged_by,
                acknowledged_at=a.acknowledged_at,
                resolved_by=a.resolved_by,
                resolved_at=a.resolved_at,
                created_at=a.created_at,
                updated_at=a.updated_at
            )
            for a in alerts
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve alerts",
            details={"error": str(e)}
        )


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    acknowledge_data: AlertAcknowledgeRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Acknowledge alert"""
    try:
        alert_repo = ProviderAlertRepository()
        
        # Get existing alert
        existing_alert = await alert_repo.get_by_field("alert_id", alert_id)
        if not existing_alert:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Alert not found",
                status_code=404
            )
        
        # Check tenant access
        if existing_alert.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Acknowledge alert
        acknowledged = await alert_repo.acknowledge_alert(
            alert_id, current_user.employee_id, acknowledge_data.notes
        )
        
        if not acknowledged:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to acknowledge alert"
            )
        
        return {
            "alert_id": alert_id,
            "status": "acknowledged",
            "message": "Alert acknowledged successfully"
        }
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to acknowledge alert",
            details={"error": str(e)}
        )


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolve_data: AlertResolveRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Resolve alert"""
    try:
        alert_repo = ProviderAlertRepository()
        
        # Get existing alert
        existing_alert = await alert_repo.get_by_field("alert_id", alert_id)
        if not existing_alert:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Alert not found",
                status_code=404
            )
        
        # Check tenant access
        if existing_alert.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Resolve alert
        resolved = await alert_repo.resolve_alert(
            alert_id, current_user.employee_id, resolve_data.resolution, resolve_data.notes
        )
        
        if not resolved:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to resolve alert"
            )
        
        return {
            "alert_id": alert_id,
            "status": "resolved",
            "message": "Alert resolved successfully"
        }
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to resolve alert",
            details={"error": str(e)}
        )


@router.get("/devices/offline")
async def get_offline_devices(
    timeout_minutes: int = Query(120, ge=1, le=1440),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get offline devices"""
    try:
        heartbeat_repo = DeviceHeartbeatRepository()
        
        offline_devices = await heartbeat_repo.get_offline_devices(timeout_minutes)
        
        return [
            {
                "device_id": device.device_id,
                "store_id": device.store_id,
                "last_heartbeat": device.timestamp,
                "status": device.status,
                "battery_level": device.battery_level,
                "signal_strength": device.signal_strength
            }
            for device in offline_devices
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to get offline devices",
            details={"error": str(e)}
        )


@router.get("/audit-trail")
async def get_audit_trail(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    target_type: Optional[str] = Query(None),
    target_id: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get audit trail"""
    try:
        audit_repo = ProviderAuditRepository()
        
        audits = await audit_repo.get_audit_trail(
            tenant_id=current_user.tenant_id,
            target_type=target_type,
            target_id=target_id,
            skip=skip,
            limit=limit
        )
        
        return [
            {
                "audit_id": a.audit_id,
                "action": a.action,
                "actor_id": a.actor_id,
                "target_type": a.target_type,
                "target_id": a.target_id,
                "timestamp": a.timestamp,
                "details": a.details
            }
            for a in audits
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve audit trail",
            details={"error": str(e)}
        )
