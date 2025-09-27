"""
Payment Router
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from ulid import ULID

from app.models.payments import Payment, PaymentCreateRequest, PaymentUpdateRequest, PaymentResponse
from app.repositories.payments import PaymentRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.deps import get_current_user, get_db

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=201)
async def create_payment(
    payment_data: PaymentCreateRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new payment"""
    try:
        payment_repo = PaymentRepository()
        
        # Generate payment ID
        payment_id = str(ULID())
        
        # Create payment document
        payment = Payment(
            payment_id=payment_id,
            tenant_id=current_user.tenant_id,
            store_id=current_user.store_id,
            sale_id=payment_data.sale_id,
            method=payment_data.method,
            amount=payment_data.amount,
            currency="THB",
            status="pending",
            txn_ref=payment_data.txn_ref,
            gateway=payment_data.gateway,
            meta=payment_data.meta
        )
        
        created_payment = await payment_repo.create(payment)
        
        return PaymentResponse(
            payment_id=created_payment.payment_id,
            sale_id=created_payment.sale_id,
            method=created_payment.method,
            amount=created_payment.amount,
            currency=created_payment.currency,
            status=created_payment.status,
            txn_ref=created_payment.txn_ref,
            gateway=created_payment.gateway,
            meta=created_payment.meta,
            created_at=created_payment.created_at,
            updated_at=created_payment.updated_at
        )
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to create payment",
            details={"error": str(e)}
        )


@router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get payments with optional filters"""
    try:
        payment_repo = PaymentRepository()
        
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        if start_dt and end_dt:
            payments = await payment_repo.get_by_store_and_date_range(
                current_user.store_id, start_dt, end_dt, skip, limit
            )
        elif status:
            now = datetime.utcnow()
            start_dt = now - timedelta(days=30)  # Default to last 30 days
            payments = await payment_repo.get_by_status_and_date(
                status, start_dt, now, skip, limit
            )
        else:
            payments = await payment_repo.get_many(
                {"store_id": current_user.store_id}, skip, limit
            )
        
        return [
            PaymentResponse(
                payment_id=p.payment_id,
                sale_id=p.sale_id,
                method=p.method,
                amount=p.amount,
                currency=p.currency,
                status=p.status,
                txn_ref=p.txn_ref,
                gateway=p.gateway,
                meta=p.meta,
                created_at=p.created_at,
                updated_at=p.updated_at
            )
            for p in payments
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve payments",
            details={"error": str(e)}
        )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get payment by ID"""
    try:
        payment_repo = PaymentRepository()
        payment = await payment_repo.get_by_field("payment_id", payment_id)
        
        if not payment:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Payment not found",
                status_code=404
            )
        
        # Check tenant access
        if payment.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        return PaymentResponse(
            payment_id=payment.payment_id,
            sale_id=payment.sale_id,
            method=payment.method,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            txn_ref=payment.txn_ref,
            gateway=payment.gateway,
            meta=payment.meta,
            created_at=payment.created_at,
            updated_at=payment.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve payment",
            details={"error": str(e)}
        )


@router.patch("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: str,
    payment_data: PaymentUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update payment"""
    try:
        payment_repo = PaymentRepository()
        
        # Get existing payment
        existing_payment = await payment_repo.get_by_field("payment_id", payment_id)
        if not existing_payment:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Payment not found",
                status_code=404
            )
        
        # Check tenant access
        if existing_payment.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Update payment
        updated_payment = await payment_repo.update_status(
            payment_id, payment_data.status, payment_data.txn_ref, payment_data.meta
        )
        
        if not updated_payment:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to update payment"
            )
        
        return PaymentResponse(
            payment_id=updated_payment.payment_id,
            sale_id=updated_payment.sale_id,
            method=updated_payment.method,
            amount=updated_payment.amount,
            currency=updated_payment.currency,
            status=updated_payment.status,
            txn_ref=updated_payment.txn_ref,
            gateway=updated_payment.gateway,
            meta=updated_payment.meta,
            created_at=updated_payment.created_at,
            updated_at=updated_payment.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to update payment",
            details={"error": str(e)}
        )


@router.get("/summary/stats")
async def get_payment_summary(
    start_date: str = Query(...),
    end_date: str = Query(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get payment summary statistics"""
    try:
        payment_repo = PaymentRepository()
        
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        summary = await payment_repo.get_payment_summary(
            current_user.store_id, start_dt, end_dt
        )
        
        return summary
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to get payment summary",
            details={"error": str(e)}
        )
