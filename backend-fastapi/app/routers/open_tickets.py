"""
Open Tickets Router (Cart/Park functionality)
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from ulid import ULID

from app.models.open_tickets import (
    OpenTicket, OpenTicketCreateRequest, OpenTicketUpdateRequest,
    OpenTicketCheckoutRequest, OpenTicketResponse, OpenTicketCheckoutResponse
)
from app.repositories.open_tickets import OpenTicketRepository
from app.repositories.sales import SalesRepository
from app.repositories.payments import PaymentRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.deps import get_current_user, get_db

router = APIRouter()


@router.post("/", response_model=OpenTicketResponse, status_code=201)
async def create_open_ticket(
    open_ticket_data: OpenTicketCreateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new open ticket (park cart)"""
    try:
        open_ticket_repo = OpenTicketRepository()
        
        # Generate open ticket ID
        open_ticket_id = str(ULID())
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(minutes=open_ticket_data.expires_in_minutes)
        
        # Calculate totals (simplified - in production, use proper pricing service)
        subtotal = sum(item["quantity"] * item["unit_price"] for item in open_ticket_data.items)
        grand_total = subtotal  # No taxes/discounts for now
        
        # Create open ticket document
        open_ticket = OpenTicket(
            open_ticket_id=open_ticket_id,
            tenant_id=current_user.tenant_id,
            store_id=current_user.store_id,
            device_id=current_user.device_id,
            cashier_id=current_user.employee_id,
            items=[
                {
                    "package_id": item["package_id"],
                    "package_name": item["package_name"],
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "line_total": item["quantity"] * item["unit_price"]
                }
                for item in open_ticket_data.items
            ],
            subtotal=subtotal,
            grand_total=grand_total,
            status="active",
            expires_at=expires_at,
            notes=open_ticket_data.notes,
            meta=open_ticket_data.meta
        )
        
        created_open_ticket = await open_ticket_repo.create(open_ticket)
        
        return OpenTicketResponse(
            open_ticket_id=created_open_ticket.open_ticket_id,
            items=created_open_ticket.items,
            subtotal=created_open_ticket.subtotal,
            discount_total=created_open_ticket.discount_total,
            tax_total=created_open_ticket.tax_total,
            grand_total=created_open_ticket.grand_total,
            status=created_open_ticket.status,
            expires_at=created_open_ticket.expires_at,
            notes=created_open_ticket.notes,
            created_at=created_open_ticket.created_at,
            updated_at=created_open_ticket.updated_at
        )
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to create open ticket",
            details={"error": str(e)}
        )


@router.get("/", response_model=List[OpenTicketResponse])
async def get_open_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query("active"),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get open tickets"""
    try:
        open_ticket_repo = OpenTicketRepository()
        
        if status == "active":
            open_tickets = await open_ticket_repo.get_active_by_store(
                current_user.store_id, skip, limit
            )
        elif status == "device":
            open_tickets = await open_ticket_repo.get_active_by_device(
                current_user.device_id, skip, limit
            )
        elif status == "cashier":
            open_tickets = await open_ticket_repo.get_active_by_cashier(
                current_user.employee_id, skip, limit
            )
        else:
            open_tickets = await open_ticket_repo.get_many(
                {"store_id": current_user.store_id}, skip, limit
            )
        
        return [
            OpenTicketResponse(
                open_ticket_id=ot.open_ticket_id,
                items=ot.items,
                subtotal=ot.subtotal,
                discount_total=ot.discount_total,
                tax_total=ot.tax_total,
                grand_total=ot.grand_total,
                status=ot.status,
                expires_at=ot.expires_at,
                notes=ot.notes,
                created_at=ot.created_at,
                updated_at=ot.updated_at
            )
            for ot in open_tickets
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve open tickets",
            details={"error": str(e)}
        )


@router.get("/{open_ticket_id}", response_model=OpenTicketResponse)
async def get_open_ticket(
    open_ticket_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get open ticket by ID"""
    try:
        open_ticket_repo = OpenTicketRepository()
        open_ticket = await open_ticket_repo.get_by_field("open_ticket_id", open_ticket_id)
        
        if not open_ticket:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Open ticket not found",
                status_code=404
            )
        
        # Check tenant access
        if open_ticket.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        return OpenTicketResponse(
            open_ticket_id=open_ticket.open_ticket_id,
            items=open_ticket.items,
            subtotal=open_ticket.subtotal,
            discount_total=open_ticket.discount_total,
            tax_total=open_ticket.tax_total,
            grand_total=open_ticket.grand_total,
            status=open_ticket.status,
            expires_at=open_ticket.expires_at,
            notes=open_ticket.notes,
            created_at=open_ticket.created_at,
            updated_at=open_ticket.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve open ticket",
            details={"error": str(e)}
        )


@router.put("/{open_ticket_id}", response_model=OpenTicketResponse)
async def update_open_ticket(
    open_ticket_id: str,
    open_ticket_data: OpenTicketUpdateRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update open ticket"""
    try:
        open_ticket_repo = OpenTicketRepository()
        
        # Get existing open ticket
        existing_open_ticket = await open_ticket_repo.get_by_field("open_ticket_id", open_ticket_id)
        if not existing_open_ticket:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Open ticket not found",
                status_code=404
            )
        
        # Check tenant access
        if existing_open_ticket.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Prepare update data
        update_data = {}
        if open_ticket_data.items is not None:
            update_data["items"] = [
                {
                    "package_id": item["package_id"],
                    "package_name": item["package_name"],
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "line_total": item["quantity"] * item["unit_price"]
                }
                for item in open_ticket_data.items
            ]
            # Recalculate totals
            subtotal = sum(item["quantity"] * item["unit_price"] for item in open_ticket_data.items)
            update_data["subtotal"] = subtotal
            update_data["grand_total"] = subtotal  # No taxes/discounts for now
        
        if open_ticket_data.notes is not None:
            update_data["notes"] = open_ticket_data.notes
        if open_ticket_data.meta is not None:
            update_data["meta"] = open_ticket_data.meta
        
        # Update open ticket
        updated_open_ticket = await open_ticket_repo.update_by_id(
            open_ticket_id, update_data, "open_ticket_id"
        )
        
        if not updated_open_ticket:
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to update open ticket"
            )
        
        return OpenTicketResponse(
            open_ticket_id=updated_open_ticket.open_ticket_id,
            items=updated_open_ticket.items,
            subtotal=updated_open_ticket.subtotal,
            discount_total=updated_open_ticket.discount_total,
            tax_total=updated_open_ticket.tax_total,
            grand_total=updated_open_ticket.grand_total,
            status=updated_open_ticket.status,
            expires_at=updated_open_ticket.expires_at,
            notes=updated_open_ticket.notes,
            created_at=updated_open_ticket.created_at,
            updated_at=updated_open_ticket.updated_at
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to update open ticket",
            details={"error": str(e)}
        )


@router.post("/{open_ticket_id}/checkout", response_model=OpenTicketCheckoutResponse)
async def checkout_open_ticket(
    open_ticket_id: str,
    checkout_data: OpenTicketCheckoutRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Checkout open ticket to create sale and payment"""
    try:
        open_ticket_repo = OpenTicketRepository()
        sales_repo = SalesRepository()
        payment_repo = PaymentRepository()
        
        # Get existing open ticket
        open_ticket = await open_ticket_repo.get_by_field("open_ticket_id", open_ticket_id)
        if not open_ticket:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Open ticket not found",
                status_code=404
            )
        
        # Check if ticket is still active
        if open_ticket.status != "active":
            raise PlayParkException(
                error_code=ErrorCode.E_RULE_CONFLICT,
                message="Open ticket is not active",
                status_code=400
            )
        
        # Check if ticket has expired
        if open_ticket.expires_at < datetime.utcnow():
            await open_ticket_repo.mark_as_expired(open_ticket_id)
            raise PlayParkException(
                error_code=ErrorCode.E_EXPIRED,
                message="Open ticket has expired",
                status_code=400
            )
        
        # Generate sale and payment IDs
        sale_id = str(ULID())
        payment_id = str(ULID())
        
        # Create sale (simplified)
        from app.models.sales import Sale, SaleItem, SaleStatus, PaymentMethod
        
        sale_items = [
            SaleItem(
                package_id=item["package_id"],
                package_name=item["package_name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"] / 100,  # Convert from satang
                line_total=item["line_total"] / 100   # Convert from satang
            )
            for item in open_ticket.items
        ]
        
        sale = Sale(
            sale_id=sale_id,
            tenant_id=open_ticket.tenant_id,
            store_id=open_ticket.store_id,
            device_id=open_ticket.device_id,
            cashier_id=open_ticket.cashier_id,
            shift_id="",  # Should be provided or retrieved
            reference=f"open_ticket_{open_ticket_id}",
            items=sale_items,
            subtotal=open_ticket.subtotal / 100,  # Convert from satang
            discount_total=open_ticket.discount_total / 100,
            tax_total=open_ticket.tax_total / 100,
            grand_total=open_ticket.grand_total / 100,
            payment_method=PaymentMethod(checkout_data.payment_method),
            amount_tendered=checkout_data.amount_tendered / 100 if checkout_data.amount_tendered else None,
            change=(checkout_data.amount_tendered - open_ticket.grand_total) / 100 if checkout_data.amount_tendered else None,
            notes=checkout_data.notes,
            status=SaleStatus.COMPLETED
        )
        
        created_sale = await sales_repo.create(sale)
        
        # Create payment
        from app.models.payments import Payment, PaymentStatus
        
        payment = Payment(
            payment_id=payment_id,
            tenant_id=open_ticket.tenant_id,
            store_id=open_ticket.store_id,
            sale_id=sale_id,
            method=PaymentMethod(checkout_data.payment_method),
            amount=open_ticket.grand_total,
            currency="THB",
            status=PaymentStatus.SUCCEEDED,
            meta={"from_open_ticket": open_ticket_id}
        )
        
        created_payment = await payment_repo.create(payment)
        
        # Mark open ticket as checked out
        await open_ticket_repo.mark_as_checked_out(open_ticket_id)
        
        return OpenTicketCheckoutResponse(
            open_ticket_id=open_ticket_id,
            sale_id=sale_id,
            payment_id=payment_id,
            status="completed",
            tickets=[]  # Would be populated by ticket generation service
        )
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to checkout open ticket",
            details={"error": str(e)}
        )


@router.delete("/{open_ticket_id}")
async def cancel_open_ticket(
    open_ticket_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Cancel open ticket"""
    try:
        open_ticket_repo = OpenTicketRepository()
        
        # Get existing open ticket
        existing_open_ticket = await open_ticket_repo.get_by_field("open_ticket_id", open_ticket_id)
        if not existing_open_ticket:
            raise PlayParkException(
                error_code=ErrorCode.NOT_FOUND,
                message="Open ticket not found",
                status_code=404
            )
        
        # Check tenant access
        if existing_open_ticket.tenant_id != current_user.tenant_id:
            raise PlayParkException(
                error_code=ErrorCode.E_PERMISSION,
                message="Access denied",
                status_code=403
            )
        
        # Cancel open ticket
        await open_ticket_repo.cancel(open_ticket_id)
        
        return {"message": "Open ticket cancelled successfully"}
        
    except PlayParkException:
        raise
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to cancel open ticket",
            details={"error": str(e)}
        )
