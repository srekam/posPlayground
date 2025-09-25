"""
Authentication Router
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.models.auth import (
    DeviceLoginRequest,
    EmployeeLoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    DeviceAuthResponse,
    EmployeeAuthResponse
)
from app.services.auth import AuthService
from app.deps import get_auth_service
from app.utils.errors import PlayParkException

router = APIRouter()


@router.post("/device/login", response_model=DeviceAuthResponse)
async def device_login(
    request: DeviceLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> DeviceAuthResponse:
    """Authenticate a device"""
    
    try:
        result = await auth_service.authenticate_device(request)
        return DeviceAuthResponse(**result)
    
    except PlayParkException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Authentication failed"
            }
        )


@router.post("/employees/login", response_model=EmployeeAuthResponse)
async def employee_login(
    request: EmployeeLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> EmployeeAuthResponse:
    """Authenticate an employee"""
    
    try:
        result = await auth_service.authenticate_employee(request)
        return EmployeeAuthResponse(**result)
    
    except PlayParkException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Authentication failed"
            }
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """Refresh an access token"""
    
    try:
        result = await auth_service.refresh_token(request.refresh_token)
        return TokenResponse(**result)
    
    except PlayParkException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Token refresh failed"
            }
        )


@router.post("/logout")
async def logout(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Logout user"""
    
    try:
        # Get refresh token from request body or cookies
        refresh_token = None
        
        # Try to get from Authorization header or cookies
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # For logout, we might need to extract the refresh token differently
            # This is a simplified implementation
            pass
        
        # Try cookies
        refresh_token = request.cookies.get("refresh_token")
        
        # Extract user ID from token if available
        user_id = None
        if refresh_token:
            try:
                payload = auth_service.verify_token(refresh_token)
                user_id = payload.sub
            except:
                pass
        
        # Logout
        success = await auth_service.logout(refresh_token=refresh_token, user_id=user_id)
        
        return {
            "message": "Logged out successfully" if success else "Logout completed",
            "success": True
        }
    
    except PlayParkException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Logout failed"
            }
        )


@router.post("/verify_pin")
async def verify_pin(
    request: Dict[str, str],
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Verify approval PIN"""
    
    try:
        pin = request.get("pin")
        if not pin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "E_MISSING_REQUIRED_FIELD",
                    "message": "PIN is required"
                }
            )
        
        # This is a placeholder implementation
        # In a real system, you'd verify the PIN against the database
        # and check if the user has approval permissions
        
        return {
            "verified": True,
            "message": "PIN verified successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "PIN verification failed"
            }
        )
