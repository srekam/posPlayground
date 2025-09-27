"""
Tax Router
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from ulid import ULID

from app.models.taxes import Tax, TaxCreateRequest, TaxUpdateRequest, TaxResponse
from app.repositories.taxes import TaxRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.deps import get_current_user, get_db

router = APIRouter()


@router.post("/", response_model=TaxResponse, status_code=201)
async def create_tax(
    tax_data: TaxCreateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new tax"""
    try:
        tax_repo = TaxRepository()
        
        # Create tax document
        tax = Tax(
            tenant_id=current_user.tenant_id,
            name=tax_data.name,
            rate=tax_data.rate,
            type=tax_data.type,
            active=tax_data.active,
            description=tax_data.description
        )
        
        created_tax = await tax_repo.create(tax)
        
        return TaxResponse(
            id=str(created_tax.id),
            name=created_tax.name,
            rate=created_tax.rate,
            type=created_tax.type,
            active=created_tax.active,
            description=created_tax.description,
            created_at=created_tax.created_at,
            updated_at=created_tax.updated_at
        )
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to create tax",
            details={"error": str(e)}
        )


@router.get("/", response_model=List[TaxResponse])
async def get_taxes(
    active_only: bool = Query(True),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get taxes for tenant"""
    try:
        tax_repo = TaxRepository()
        
        if active_only:
            taxes = await tax_repo.get_active_by_tenant(current_user.tenant_id)
        else:
            taxes = await tax_repo.get_many({"tenant_id": current_user.tenant_id})
        
        return [
            TaxResponse(
                id=str(tax.id),
                name=tax.name,
                rate=tax.rate,
                type=tax.type,
                active=tax.active,
                description=tax.description,
                created_at=tax.created_at,
                updated_at=tax.updated_at
            )
            for tax in taxes
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve taxes",
            details={"error": str(e)}
        )


@router.get("/{tax_id}", response_model=TaxResponse)
async def get_tax(
    tax_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get tax by ID"""
    try:
        tax_repo = TaxRepository()
        tax = await tax_repo.get_by_id(tax_id)
        
        if not tax:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Tax not found",
                status_code=404
            )
        
        # Check tenant access
        if tax.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        return TaxResponse(
            id=str(tax.id),
            name=tax.name,
            rate=tax.rate,
            type=tax.type,
            active=tax.active,
            description=tax.description,
            created_at=tax.created_at,
            updated_at=tax.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve tax",
            details={"error": str(e)}
        )


@router.put("/{tax_id}", response_model=TaxResponse)
async def update_tax(
    tax_id: str,
    tax_data: TaxUpdateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update tax"""
    try:
        tax_repo = TaxRepository()
        
        # Get existing tax
        existing_tax = await tax_repo.get_by_id(tax_id)
        if not existing_tax:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Tax not found",
                status_code=404
            )
        
        # Check tenant access
        if existing_tax.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Prepare update data
        update_data = {}
        if tax_data.name is not None:
            update_data["name"] = tax_data.name
        if tax_data.rate is not None:
            update_data["rate"] = tax_data.rate
        if tax_data.type is not None:
            update_data["type"] = tax_data.type
        if tax_data.active is not None:
            update_data["active"] = tax_data.active
        if tax_data.description is not None:
            update_data["description"] = tax_data.description
        
        # Update tax
        updated_tax = await tax_repo.update_by_id(tax_id, update_data)
        
        if not updated_tax:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to update tax"
            )
        
        return TaxResponse(
            id=str(updated_tax.id),
            name=updated_tax.name,
            rate=updated_tax.rate,
            type=updated_tax.type,
            active=updated_tax.active,
            description=updated_tax.description,
            created_at=updated_tax.created_at,
            updated_at=updated_tax.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to update tax",
            details={"error": str(e)}
        )


@router.delete("/{tax_id}")
async def delete_tax(
    tax_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete tax (soft delete by deactivating)"""
    try:
        tax_repo = TaxRepository()
        
        # Get existing tax
        existing_tax = await tax_repo.get_by_id(tax_id)
        if not existing_tax:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Tax not found",
                status_code=404
            )
        
        # Check tenant access
        if existing_tax.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Deactivate tax
        await tax_repo.deactivate(tax_id)
        
        return {"message": "Tax deactivated successfully"}
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to delete tax",
            details={"error": str(e)}
        )
