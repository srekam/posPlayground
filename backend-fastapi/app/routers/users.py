"""
Users Router
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import CurrentUser
from app.services.users import UserService

router = APIRouter()


@router.get("/me")
async def get_current_user_info(
    current_user = CurrentUser,
    user_service: UserService = Depends()
) -> Dict[str, Any]:
    """Get current user information"""
    
    try:
        return {
            "employee_id": current_user.employee_id,
            "name": current_user.name,
            "email": current_user.email,
            "roles": current_user.roles,
            "permissions": current_user.permissions,
            "tenant_id": current_user.tenant_id,
            "store_id": current_user.store_id,
            "status": current_user.status
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve user information"
            }
        )
