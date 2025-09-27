"""
Approval Router
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ulid import ULID

from app.models.approvals import (
    ReasonCode, Approval, ReasonCodeCreateRequest, ReasonCodeUpdateRequest,
    ApprovalVerifyRequest, ReasonCodeResponse, ApprovalResponse
)
from app.repositories.approvals import ReasonCodeRepository, ApprovalRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.deps import get_current_user, get_db

router = APIRouter()


@router.post("/verify-pin")
async def verify_pin(
    verify_data: ApprovalVerifyRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Verify approval PIN"""
    try:
        approval_repo = ApprovalRepository()
        
        # Verify PIN
        approval = await approval_repo.verify_pin(
            verify_data.pin, verify_data.reference_id, "general"
        )
        
        if not approval:
            raise PlayParkException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message="Invalid PIN",
                status_code=401
            )
        
        return {
            "verified": True,
            "approval_id": approval.approval_id,
            "message": "PIN verified successfully"
        }
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to verify PIN",
            details={"error": str(e)}
        )


@router.get("/reason-codes", response_model=List[ReasonCodeResponse])
async def get_reason_codes(
    category: Optional[str] = Query(None),
    active_only: bool = Query(True),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get reason codes"""
    try:
        reason_code_repo = ReasonCodeRepository()
        
        if category:
            reason_codes = await reason_code_repo.get_by_category(
                current_user.tenant_id, category
            )
        else:
            if active_only:
                reason_codes = await reason_code_repo.get_many({
                    "tenant_id": current_user.tenant_id,
                    "active": True
                })
            else:
                reason_codes = await reason_code_repo.get_many({
                    "tenant_id": current_user.tenant_id
                })
        
        return [
            ReasonCodeResponse(
                id=str(rc.id),
                code=rc.code,
                name=rc.name,
                category=rc.category,
                description=rc.description,
                requires_approval=rc.requires_approval,
                active=rc.active,
                created_at=rc.created_at,
                updated_at=rc.updated_at
            )
            for rc in reason_codes
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve reason codes",
            details={"error": str(e)}
        )


@router.post("/reason-codes", response_model=ReasonCodeResponse, status_code=201)
async def create_reason_code(
    reason_code_data: ReasonCodeCreateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new reason code"""
    try:
        reason_code_repo = ReasonCodeRepository()
        
        # Check if reason code already exists
        existing = await reason_code_repo.get_by_code(
            current_user.tenant_id, reason_code_data.code
        )
        if existing:
            raise PlayParkException(
                error_code=ErrorCode.E_DUPLICATE,
                message="Reason code already exists",
                status_code=400
            )
        
        # Create reason code document
        reason_code = ReasonCode(
            tenant_id=current_user.tenant_id,
            code=reason_code_data.code,
            name=reason_code_data.name,
            category=reason_code_data.category,
            description=reason_code_data.description,
            requires_approval=reason_code_data.requires_approval,
            active=reason_code_data.active
        )
        
        created_reason_code = await reason_code_repo.create(reason_code)
        
        return ReasonCodeResponse(
            id=str(created_reason_code.id),
            code=created_reason_code.code,
            name=created_reason_code.name,
            category=created_reason_code.category,
            description=created_reason_code.description,
            requires_approval=created_reason_code.requires_approval,
            active=created_reason_code.active,
            created_at=created_reason_code.created_at,
            updated_at=created_reason_code.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to create reason code",
            details={"error": str(e)}
        )


@router.put("/reason-codes/{reason_code_id}", response_model=ReasonCodeResponse)
async def update_reason_code(
    reason_code_id: str,
    reason_code_data: ReasonCodeUpdateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update reason code"""
    try:
        reason_code_repo = ReasonCodeRepository()
        
        # Get existing reason code
        existing = await reason_code_repo.get_by_id(reason_code_id)
        if not existing:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Reason code not found",
                status_code=404
            )
        
        # Check tenant access
        if existing.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Prepare update data
        update_data = {}
        if reason_code_data.name is not None:
            update_data["name"] = reason_code_data.name
        if reason_code_data.category is not None:
            update_data["category"] = reason_code_data.category
        if reason_code_data.description is not None:
            update_data["description"] = reason_code_data.description
        if reason_code_data.requires_approval is not None:
            update_data["requires_approval"] = reason_code_data.requires_approval
        if reason_code_data.active is not None:
            update_data["active"] = reason_code_data.active
        
        # Update reason code
        updated = await reason_code_repo.update_by_id(reason_code_id, update_data)
        
        if not updated:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to update reason code"
            )
        
        return ReasonCodeResponse(
            id=str(updated.id),
            code=updated.code,
            name=updated.name,
            category=updated.category,
            description=updated.description,
            requires_approval=updated.requires_approval,
            active=updated.active,
            created_at=updated.created_at,
            updated_at=updated.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to update reason code",
            details={"error": str(e)}
        )


@router.delete("/reason-codes/{reason_code_id}")
async def delete_reason_code(
    reason_code_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete reason code (soft delete by deactivating)"""
    try:
        reason_code_repo = ReasonCodeRepository()
        
        # Get existing reason code
        existing = await reason_code_repo.get_by_id(reason_code_id)
        if not existing:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Reason code not found",
                status_code=404
            )
        
        # Check tenant access
        if existing.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Deactivate reason code
        await reason_code_repo.deactivate(reason_code_id)
        
        return {"message": "Reason code deactivated successfully"}
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to delete reason code",
            details={"error": str(e)}
        )


@router.get("/pending", response_model=List[ApprovalResponse])
async def get_pending_approvals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get pending approvals for store"""
    try:
        approval_repo = ApprovalRepository()
        
        approvals = await approval_repo.get_pending_by_store(
            current_user.store_id, skip, limit
        )
        
        return [
            ApprovalResponse(
                approval_id=a.approval_id,
                type=a.type,
                reference_id=a.reference_id,
                status=a.status,
                requested_by=a.requested_by,
                approved_by=a.approved_by,
                requested_at=a.requested_at,
                approved_at=a.approved_at,
                reason_code=a.reason_code,
                notes=a.notes
            )
            for a in approvals
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve pending approvals",
            details={"error": str(e)}
        )


@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
async def approve_request(
    approval_id: str,
    notes: Optional[str] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Approve a request"""
    try:
        approval_repo = ApprovalRepository()
        
        # Get existing approval
        existing = await approval_repo.get_by_id(approval_id)
        if not existing:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Approval not found",
                status_code=404
            )
        
        # Check tenant access
        if existing.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Approve request
        approved = await approval_repo.approve(
            approval_id, current_user.employee_id, notes
        )
        
        if not approved:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to approve request"
            )
        
        return ApprovalResponse(
            approval_id=approved.approval_id,
            type=approved.type,
            reference_id=approved.reference_id,
            status=approved.status,
            requested_by=approved.requested_by,
            approved_by=approved.approved_by,
            requested_at=approved.requested_at,
            approved_at=approved.approved_at,
            reason_code=approved.reason_code,
            notes=approved.notes
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to approve request",
            details={"error": str(e)}
        )


@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
async def reject_request(
    approval_id: str,
    notes: Optional[str] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Reject a request"""
    try:
        approval_repo = ApprovalRepository()
        
        # Get existing approval
        existing = await approval_repo.get_by_id(approval_id)
        if not existing:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Approval not found",
                status_code=404
            )
        
        # Check tenant access
        if existing.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Reject request
        rejected = await approval_repo.reject(
            approval_id, current_user.employee_id, notes
        )
        
        if not rejected:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to reject request"
            )
        
        return ApprovalResponse(
            approval_id=rejected.approval_id,
            type=rejected.type,
            reference_id=rejected.reference_id,
            status=rejected.status,
            requested_by=rejected.requested_by,
            approved_by=rejected.approved_by,
            requested_at=rejected.requested_at,
            approved_at=rejected.approved_at,
            reason_code=rejected.reason_code,
            notes=rejected.notes
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to reject request",
            details={"error": str(e)}
        )
