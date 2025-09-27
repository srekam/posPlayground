"""
Usage Counter Router
"""
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request

from app.models.usage_counters import UsageBillingRequest, UsageBillingResponse
from app.repositories.usage_counters import UsageCounterRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.deps import get_current_user, get_db

router = APIRouter()


@router.get("/billing/usage", response_model=UsageBillingResponse)
async def get_usage_billing(
    tenant_id: str = Query(...),
    from_date: str = Query(...),
    to_date: str = Query(...),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get usage billing for tenant"""
    try:
        usage_counter_repo = UsageCounterRepository()
        
        # Check if user has permission to access this tenant's billing
        if current_user.tenant_id != tenant_id and "admin" not in getattr(current_user, "roles", []):
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Get usage summary
        summary = await usage_counter_repo.get_usage_summary(tenant_id, from_date, to_date)
        
        return UsageBillingResponse(**summary)
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to get usage billing",
            details={"error": str(e)}
        )


@router.get("/stats/tenant")
async def get_tenant_usage_stats(
    period: str = Query(...),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get tenant usage statistics"""
    try:
        usage_counter_repo = UsageCounterRepository()
        
        # Get tenant usage for period
        usage_counters = await usage_counter_repo.get_tenant_usage(
            current_user.tenant_id, period
        )
        
        # Calculate totals
        total_requests = sum(counter.count for counter in usage_counters)
        route_usage = {}
        
        for counter in usage_counters:
            route_key = f"{counter.method} {counter.route}"
            route_usage[route_key] = counter.count
        
        return {
            "tenant_id": current_user.tenant_id,
            "period": period,
            "total_requests": total_requests,
            "route_usage": route_usage,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to get tenant usage stats",
            details={"error": str(e)}
        )


@router.get("/stats/routes")
async def get_route_usage_stats(
    period: str = Query(...),
    route: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get route usage statistics"""
    try:
        usage_counter_repo = UsageCounterRepository()
        
        if route:
            # Get specific route usage
            query = {
                "tenant_id": current_user.tenant_id,
                "period": period,
                "route": route
            }
            counters = await usage_counter_repo.get_many(query)
        else:
            # Get all routes for period
            counters = await usage_counter_repo.get_tenant_usage(
                current_user.tenant_id, period
            )
        
        return [
            {
                "route": c.route,
                "method": c.method,
                "period": c.period,
                "count": c.count,
                "last_reset": c.last_reset
            }
            for c in counters
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to get route usage stats",
            details={"error": str(e)}
        )


@router.post("/increment")
async def increment_usage(
    request: Request,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Increment usage counter (typically called by middleware)"""
    try:
        usage_counter_repo = UsageCounterRepository()
        
        # Extract route and method from request
        route = request.url.path
        method = request.method
        
        # Get current period (YYYY-MM format)
        now = datetime.utcnow()
        period = now.strftime("%Y-%m")
        
        # Increment usage
        await usage_counter_repo.increment_usage(
            tenant_id=current_user.tenant_id,
            route=route,
            method=method,
            period=period
        )
        
        return {"message": "Usage incremented successfully"}
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to increment usage",
            details={"error": str(e)}
        )


@router.post("/cleanup")
async def cleanup_old_counters(
    days: int = Query(90, ge=1, le=365),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Clean up old usage counters (admin only)"""
    try:
        # Check if user is admin
        if "admin" not in getattr(current_user, "roles", []):
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Admin access required",
                status_code=403
            )
        
        usage_counter_repo = UsageCounterRepository()
        
        # Clean up old counters
        deleted_count = await usage_counter_repo.cleanup_old_counters(days)
        
        return {
            "message": f"Cleaned up {deleted_count} old usage counters",
            "deleted_count": deleted_count
        }
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to cleanup old counters",
            details={"error": str(e)}
        )


@router.post("/reset/{period}")
async def reset_period_counters(
    period: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Reset counters for a specific period (admin only)"""
    try:
        # Check if user is admin
        if "admin" not in getattr(current_user, "roles", []):
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Admin access required",
                status_code=403
            )
        
        usage_counter_repo = UsageCounterRepository()
        
        # Reset counters for period
        reset_count = await usage_counter_repo.reset_period_counters(period)
        
        return {
            "message": f"Reset {reset_count} counters for period {period}",
            "reset_count": reset_count,
            "period": period
        }
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to reset period counters",
            details={"error": str(e)}
        )
