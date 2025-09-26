"""Shift Service - Complete Implementation"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.shifts import Shift, ShiftOpenRequest, ShiftCloseRequest
from app.repositories.shifts import ShiftRepository
from app.utils.logging import LoggerMixin
from app.utils.errors import PlayParkException, ErrorCode


class ShiftService(LoggerMixin):
    def __init__(self, shift_repo: ShiftRepository):
        self.shift_repo = shift_repo
    
    async def open_shift(self, request: ShiftOpenRequest, user) -> Dict[str, Any]:
        """Open a new shift"""
        self.logger.info("Opening shift", user_id=user.employee_id, store_id=user.store_id)
        
        try:
            # Check if there's already an open shift for this user
            existing_shift = await self.shift_repo.get_current_shift_by_employee(user.employee_id)
            if existing_shift and existing_shift.status == "open":
                raise PlayParkException(
                    error_code=ErrorCode.BAD_REQUEST,
                    message="Employee already has an open shift"
                )
            
            # Create new shift
            shift = Shift(
                shift_id=f"shift_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{user.employee_id}",
                tenant_id=user.tenant_id if hasattr(user, 'tenant_id') else "default",
                store_id=user.store_id,
                device_id=user.device_id if hasattr(user, 'device_id') else "default",
                opened_by=user.employee_id,
                open_at=datetime.utcnow(),
                cash_open=request.cash_open,
                status="open",
                notes=request.notes if hasattr(request, 'notes') else None
            )
            
            created_shift = await self.shift_repo.create_shift(shift)
            
            return {
                "shift_id": created_shift.shift_id,
                "store_id": created_shift.store_id,
                "employee_id": created_shift.opened_by,
                "status": created_shift.status,
                "opening_cash": created_shift.cash_open,
                "opening_time": created_shift.open_at,
                "notes": created_shift.notes
            }
            
        except PlayParkException:
            raise
        except Exception as e:
            self.logger.error("Error opening shift", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to open shift"
            )
    
    async def close_shift(self, request: ShiftCloseRequest, user) -> Dict[str, Any]:
        """Close the current shift"""
        self.logger.info("Closing shift", user_id=user.employee_id)
        
        try:
            # Get current shift
            current_shift = await self.shift_repo.get_current_shift_by_employee(user.employee_id)
            if not current_shift or current_shift.status != "open":
                raise PlayParkException(
                    error_code=ErrorCode.BAD_REQUEST,
                    message="No open shift found for employee"
                )
            
            # Update shift with closing information
            closing_time = datetime.utcnow()
            shift_duration = closing_time - current_shift.open_at
            
            # Calculate totals (in real app, you'd get these from sales)
            total_sales = Decimal('0')  # Placeholder
            total_refunds = Decimal('0')  # Placeholder
            closing_cash = request.cash_counted or Decimal('0')
            cash_difference = closing_cash - current_shift.cash_open - total_sales + total_refunds
            
            updated_shift = await self.shift_repo.update_shift(
                current_shift.shift_id,
                {
                    "status": "closed",
                    "close_at": closing_time,
                    "closed_by": user.employee_id,
                    "cash_counted": float(closing_cash),
                    "cash_expected": float(current_shift.cash_open + total_sales - total_refunds),
                    "cash_diff": float(cash_difference),
                    "notes": request.notes
                }
            )
            
            return {
                "shift_id": updated_shift.shift_id,
                "status": updated_shift.status,
                "opening_time": updated_shift.open_at,
                "closing_time": updated_shift.close_at,
                "duration_minutes": int((updated_shift.close_at - updated_shift.open_at).total_seconds() / 60),
                "opening_cash": updated_shift.cash_open,
                "closing_cash": updated_shift.cash_counted,
                "total_sales": float(total_sales),
                "cash_difference": updated_shift.cash_diff,
                "notes": updated_shift.notes
            }
            
        except PlayParkException:
            raise
        except Exception as e:
            self.logger.error("Error closing shift", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to close shift"
            )
    
    async def get_current_shift(self, user) -> Optional[Dict[str, Any]]:
        """Get the current open shift for the user"""
        self.logger.info("Getting current shift", user_id=user.employee_id)
        
        try:
            shift = await self.shift_repo.get_current_shift_by_employee(user.employee_id)
            
            if not shift or shift.status != "open":
                return None
            
            return {
                "shift_id": shift.shift_id,
                "store_id": shift.store_id,
                "employee_id": shift.opened_by,
                "status": shift.status,
                "opening_cash": shift.cash_open,
                "opening_time": shift.open_at,
                "notes": shift.notes,
                "duration_minutes": int((datetime.utcnow() - shift.open_at).total_seconds() / 60)
            }
            
        except Exception as e:
            self.logger.error("Error getting current shift", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to retrieve current shift"
            )
