"""
Enrollment Router
"""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse

from app.models.auth import (
    DeviceEnrollRequest,
    DeviceEnrollResponse,
    GeneratePairingRequest,
    GeneratePairingResponse
)
from app.services.enrollment import EnrollmentService
from app.services.auth import AuthService
from app.deps import get_current_user, get_enrollment_service
from app.utils.errors import PlayParkException, ErrorCode
from app.utils.logging import LoggerMixin
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/api/v1/auth/device/enroll", response_model=DeviceEnrollResponse)
async def enroll_device(
    request: DeviceEnrollRequest,
    http_request: Request,
    enrollment_service: EnrollmentService = Depends(get_enrollment_service)
) -> DeviceEnrollResponse:
    """Enroll a device using an enrollment token"""
    
    # Rate limiting check
    client_ip = http_request.client.host if http_request.client else "unknown"
    device_fingerprint = request.device_fingerprint
    
    # Check rate limit for enrollment attempts
    from app.db.redis import get_redis
    redis = await get_redis()
    
    # Rate limit: 5 attempts per 15 minutes per IP + fingerprint
    rate_limit_key = f"enroll:{client_ip}:{device_fingerprint}"
    current_attempts = await redis.get(rate_limit_key)
    
    if current_attempts and int(current_attempts) >= 5:
        logger.warning("Enrollment rate limit exceeded",
                      client_ip=client_ip,
                      device_fingerprint=device_fingerprint[:8] + "...",
                      attempts=current_attempts)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": ErrorCode.E_RATE_LIMIT,
                "message": "Too many enrollment attempts. Try again later.",
                "retry_after": 900  # 15 minutes
            }
        )
    
    try:
        # Log enrollment attempt with structured data
        logger.info("Device enrollment attempt",
                   enroll_token=request.enroll_token[:8] + "...",
                   device_type=request.device_type,
                   app_version=request.app_version,
                   device_fingerprint=device_fingerprint[:8] + "...",
                   client_ip=client_ip,
                   user_agent=http_request.headers.get("user-agent", "unknown"),
                   request_id=getattr(http_request.state, "request_id", None))
        
        # Add debug logging for manual key detection
        if request.enroll_token.startswith('PP.'):
            logger.info("Router detected manual key", manual_key=request.enroll_token[:10] + "...")
            logger.info("Full manual key in router", manual_key=request.enroll_token)
        
        result = await enrollment_service.enroll_device(request)
        
        # Increment rate limit counter
        await redis.incr(rate_limit_key)
        await redis.expire(rate_limit_key, 900)  # 15 minutes
        
        logger.info("Device enrollment successful",
                   device_id=result.device_id,
                   tenant_id=result.tenant_id,
                   store_id=result.store_id,
                   enroll_token=request.enroll_token[:8] + "...",
                   client_ip=client_ip,
                   request_id=getattr(http_request.state, "request_id", None))
        
        return result
    
    except PlayParkException as e:
        # Increment rate limit counter on failure
        await redis.incr(rate_limit_key)
        await redis.expire(rate_limit_key, 900)
        
        logger.warning("Device enrollment failed",
                     enroll_token=request.enroll_token[:8] + "...",
                     error_code=e.error_code,
                     error_message=e.message,
                     client_ip=client_ip,
                     request_id=getattr(http_request.state, "request_id", None))
        raise
    except Exception as e:
        # Increment rate limit counter on failure
        await redis.incr(rate_limit_key)
        await redis.expire(rate_limit_key, 900)
        
        logger.error("Device enrollment failed with unexpected error",
                   enroll_token=request.enroll_token[:8] + "...",
                   error=str(e),
                   client_ip=client_ip,
                   request_id=getattr(http_request.state, "request_id", None))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": ErrorCode.INTERNAL_ERROR,
                "message": "Enrollment failed"
            }
        )


@router.post("/api/v1/auth/device/pairing/generate", response_model=GeneratePairingResponse)
async def generate_pairing(
    request: GeneratePairingRequest,
    http_request: Request,
    current_user = Depends(get_current_user),
    enrollment_service: EnrollmentService = Depends(get_enrollment_service)
) -> GeneratePairingResponse:
    """Generate pairing token and formats"""
    
    # Rate limiting for pairing generation
    client_ip = http_request.client.host if http_request.client else "unknown"
    user_id = current_user.employee_id
    
    from app.db.redis import get_redis
    redis = await get_redis()
    
    # Rate limit: 10 generations per hour per user
    rate_limit_key = f"rate_limit:pairing_gen:{user_id}"
    current_attempts = await redis.get(rate_limit_key)
    
    if current_attempts and int(current_attempts) >= 10:
        logger.warning("Pairing generation rate limit exceeded",
                     user_id=user_id,
                     client_ip=client_ip,
                     attempts=current_attempts)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": ErrorCode.E_RATE_LIMIT,
                "message": "Too many pairing generation attempts. Try again later.",
                "retry_after": 3600  # 1 hour
            }
        )
    
    try:
        # Extract tenant_id from current user
        tenant_id = current_user.tenant_id
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": ErrorCode.VALIDATION_ERROR,
                    "message": "User must belong to a tenant"
                }
            )
        
        # Log pairing generation with structured data
        logger.info("Pairing generation request",
                   store_id=request.store_id,
                   device_type=request.device_type,
                   ttl_minutes=request.ttl_minutes,
                   created_by=user_id,
                   tenant_id=tenant_id,
                   client_ip=client_ip,
                   user_agent=http_request.headers.get("user-agent", "unknown"),
                   request_id=getattr(http_request.state, "request_id", None))
        
        result = await enrollment_service.generate_pairing(
            request, 
            user_id, 
            tenant_id
        )
        
        # Increment rate limit counter
        await redis.incr(rate_limit_key)
        await redis.expire(rate_limit_key, 3600)  # 1 hour
        
        logger.info("Pairing generated successfully",
                   enroll_token=result.enroll_token[:8] + "...",
                   expires_at=result.expires_at.isoformat(),
                   created_by=user_id,
                   tenant_id=tenant_id,
                   client_ip=client_ip,
                   request_id=getattr(http_request.state, "request_id", None))
        
        return result
    
    except PlayParkException as e:
        # Increment rate limit counter on failure
        await redis.incr(rate_limit_key)
        await redis.expire(rate_limit_key, 3600)
        
        logger.warning("Pairing generation failed",
                     error_code=e.error_code,
                     error_message=e.message,
                     created_by=user_id,
                     client_ip=client_ip,
                     request_id=getattr(http_request.state, "request_id", None))
        raise
    except Exception as e:
        # Increment rate limit counter on failure
        await redis.incr(rate_limit_key)
        await redis.expire(rate_limit_key, 3600)
        
        logger.error("Pairing generation failed with unexpected error",
                   error=str(e),
                   created_by=user_id,
                   client_ip=client_ip,
                   request_id=getattr(http_request.state, "request_id", None))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": ErrorCode.INTERNAL_ERROR,
                "message": "Pairing generation failed"
            }
        )


@router.post("/api/v1/auth/device/pairing/revoke")
async def revoke_pairing(
    token: str,
    http_request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    enrollment_service: EnrollmentService = Depends(get_enrollment_service)
) -> Dict[str, Any]:
    """Revoke an enrollment token"""
    
    try:
        logger.info("Pairing revocation request",
                   token=token[:8] + "...",
                   revoked_by=current_user.employee_id,
                   client_ip=http_request.client.host if http_request.client else "unknown")
        
        success = await enrollment_service.revoke_token(token, current_user.employee_id)
        
        if success:
            logger.info("Pairing revoked successfully", token=token[:8] + "...")
            return {"success": True, "message": "Token revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": ErrorCode.ENROLL_TOKEN_NOT_FOUND,
                    "message": "Token not found"
                }
            )
    
    except PlayParkException:
        raise
    except Exception as e:
        logger.error("Pairing revocation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": ErrorCode.INTERNAL_ERROR,
                "message": "Revocation failed"
            }
        )


@router.get("/api/v1/auth/device/pairing/status/{token}")
async def get_pairing_status(
    token: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    enrollment_service: EnrollmentService = Depends(get_enrollment_service)
) -> Dict[str, Any]:
    """Get enrollment token status"""
    
    try:
        status_info = await enrollment_service.get_token_status(token)
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": ErrorCode.ENROLL_TOKEN_NOT_FOUND,
                    "message": "Token not found"
                }
            )
        
        return status_info
    
    except PlayParkException:
        raise
    except Exception as e:
        logger.error("Failed to get pairing status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": ErrorCode.INTERNAL_ERROR,
                "message": "Failed to get token status"
            }
        )


@router.get("/api/v1/auth/device/pairing/metrics")
async def get_pairing_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    enrollment_service: EnrollmentService = Depends(get_enrollment_service)
) -> Dict[str, Any]:
    """Get pairing metrics and statistics"""
    
    try:
        tenant_id = current_user.tenant_id
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": ErrorCode.VALIDATION_ERROR,
                    "message": "User must belong to a tenant"
                }
            )
        
        # Get token statistics
        token_stats = await enrollment_service.enrollment_repo.get_token_stats(tenant_id)
        
        # Get rate limit information
        from app.db.redis import get_redis
        redis = await get_redis()
        
        # Count active rate limits
        rate_limit_keys = await redis.keys("rate_limit:*")
        active_rate_limits = len(rate_limit_keys)
        
        logger.info("Pairing metrics requested",
                   tenant_id=tenant_id,
                   requested_by=current_user.employee_id)
        
        return {
            "tenant_id": tenant_id,
            "token_stats": token_stats,
            "rate_limits": {
                "active_limits": active_rate_limits,
                "total_keys": len(rate_limit_keys)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except PlayParkException:
        raise
    except Exception as e:
        logger.error("Failed to get pairing metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": ErrorCode.INTERNAL_ERROR,
                "message": "Failed to get metrics"
            }
        )
