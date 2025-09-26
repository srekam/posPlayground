"""
Tickets Router
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.tickets import (
    TicketRedeemRequest,
    TicketRedeemResponse,
    TicketResponse
)
from app.deps import (
    CurrentUser,
    CurrentDevice,
    
    RequireTicketScope
)
from app.services.tickets import TicketService
from app.utils.errors import PlayParkException

router = APIRouter()


@router.post("/redeem", response_model=TicketRedeemResponse)
async def redeem_ticket(
    request: TicketRedeemRequest,
    current_device = CurrentDevice,
    ticket_service: TicketService = Depends()
) -> TicketRedeemResponse:
    """Redeem a ticket"""
    
    try:
        result = await ticket_service.redeem_ticket(request, current_device)
        return TicketRedeemResponse(**result)
    
    except PlayParkException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Ticket redemption failed"
            }
        )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    current_user,
    ticket_service: TicketService = Depends()
) -> TicketResponse:
    """Get ticket by ID"""
    
    try:
        result = await ticket_service.get_ticket_by_id(ticket_id, current_user)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "E_TICKET_NOT_FOUND",
                    "message": "Ticket not found"
                }
            )
        
        return TicketResponse(**result)
    
    except HTTPException:
        raise
    except PlayParkException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "E_INTERNAL_ERROR",
                "message": "Failed to retrieve ticket"
            }
        )
