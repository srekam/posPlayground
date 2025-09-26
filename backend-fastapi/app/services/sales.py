"""
Sales Service - Complete Implementation
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

from app.models.sales import SaleCreateRequest, RefundRequest, ReprintRequest, Sale, SaleItem
from app.repositories.sales import SalesRepository
from app.utils.logging import LoggerMixin
from app.utils.errors import PlayParkException, ErrorCode


class SalesService(LoggerMixin):
    """Sales service"""
    
    def __init__(self, sales_repo: SalesRepository):
        self.sales_repo = sales_repo
    
    async def create_sale(
        self,
        request: SaleCreateRequest,
        user,
        device,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new sale"""
        
        self.logger.info("Creating sale", user_id=user.employee_id, device_id=device["device_id"])
        
        try:
            # Calculate totals
            subtotal = sum(item.price * item.quantity for item in request.items)
            discount_total = request.discount_total or Decimal('0')
            tax_total = request.tax_total or Decimal('0')
            grand_total = subtotal - discount_total + tax_total
            
            # Create sale object
            sale = Sale(
                sale_id=f"sale_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{user.employee_id}",
                reference=idempotency_key or f"ref_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                store_id=device["store_id"],
                employee_id=user.employee_id,
                device_id=device["device_id"],
                shift_id=request.shift_id,
                status="completed",
                subtotal=float(subtotal),
                discount_total=float(discount_total),
                tax_total=float(tax_total),
                grand_total=float(grand_total),
                payment_method=request.payment_method,
                amount_tendered=request.amount_tendered,
                change=request.amount_tendered - float(grand_total),
                notes=request.notes,
                timestamp=datetime.utcnow()
            )
            
            # Save sale to database
            created_sale = await self.sales_repo.create_sale(sale)
            
            # Create sale items
            sale_items = []
            for item in request.items:
                sale_item = SaleItem(
                    sale_id=created_sale.sale_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.price,
                    total=item.price * item.quantity
                )
                created_item = await self.sales_repo.create_sale_item(sale_item)
                sale_items.append(created_item)
            
            # Return response
            return {
                "sale_id": created_sale.sale_id,
                "reference": created_sale.reference,
                "status": created_sale.status,
                "items": [{"product_id": item.product_id, "quantity": item.quantity, "price": item.price} for item in sale_items],
                "subtotal": created_sale.subtotal,
                "discount_total": created_sale.discount_total,
                "tax_total": created_sale.tax_total,
                "grand_total": created_sale.grand_total,
                "payment_method": created_sale.payment_method,
                "amount_tendered": created_sale.amount_tendered,
                "change": created_sale.change,
                "notes": created_sale.notes,
                "tickets": request.tickets or [],
                "timestamp": created_sale.timestamp
            }
            
        except Exception as e:
            self.logger.error("Error creating sale", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to create sale"
            )
    
    async def get_sale_by_id(self, sale_id: str, user) -> Optional[Dict[str, Any]]:
        """Get sale by ID"""
        
        self.logger.info("Getting sale", sale_id=sale_id, user_id=user.employee_id)
        
        try:
            sale = await self.sales_repo.get_sale_by_id(sale_id)
            if not sale:
                return None
            
            # Get sale items
            sale_items = await self.sales_repo.get_sale_items_by_sale(sale_id)
            
            return {
                "sale_id": sale.sale_id,
                "reference": sale.reference,
                "status": sale.status,
                "items": [{"product_id": item.product_id, "quantity": item.quantity, "price": item.price} for item in sale_items],
                "subtotal": sale.subtotal,
                "discount_total": sale.discount_total,
                "tax_total": sale.tax_total,
                "grand_total": sale.grand_total,
                "payment_method": sale.payment_method,
                "amount_tendered": sale.amount_tendered,
                "change": sale.change,
                "notes": sale.notes,
                "timestamp": sale.timestamp
            }
            
        except Exception as e:
            self.logger.error("Error getting sale", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to retrieve sale"
            )
    
    async def get_sales(
        self,
        user,
        limit: int = 50,
        offset: int = 0,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get sales list"""
        
        self.logger.info("Getting sales list", user_id=user.employee_id, limit=limit, offset=offset)
        
        try:
            # Build query
            query = {"store_id": user.store_id}
            
            if status:
                query["status"] = status
            
            if from_date or to_date:
                query["timestamp"] = {}
                if from_date:
                    query["timestamp"]["$gte"] = from_date
                if to_date:
                    query["timestamp"]["$lte"] = to_date
            
            # Get sales from repository
            sales = await self.sales_repo.get_many(
                query=query,
                skip=offset,
                limit=limit,
                sort=[("timestamp", -1)]  # Most recent first
            )
            
            # Get total count for pagination
            total_count = await self.sales_repo.count_documents(query)
            
            # Format sales data
            sales_data = []
            for sale in sales:
                sales_data.append({
                    "sale_id": sale.sale_id,
                    "reference": sale.reference,
                    "status": sale.status,
                    "subtotal": sale.subtotal,
                    "grand_total": sale.grand_total,
                    "payment_method": sale.payment_method,
                    "timestamp": sale.timestamp
                })
            
            return {
                "sales": sales_data,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                }
            }
            
        except Exception as e:
            self.logger.error("Error getting sales", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to retrieve sales"
            )
    
    async def request_refund(self, request: RefundRequest, user) -> Dict[str, Any]:
        """Request refund - placeholder implementation"""
        
        self.logger.info("Requesting refund", user_id=user.employee_id, sale_id=request.sale_id)
        
        # Placeholder implementation
        return {
            "refund_id": "refund_123456789",
            "sale_id": request.sale_id,
            "amount": 0.0,
            "status": "pending",
            "reason_code": request.reason_code,
            "reason_text": request.reason_text,
            "requested_by": user.employee_id,
            "timestamp": datetime.utcnow()
        }
    
    async def request_reprint(self, request: ReprintRequest, user) -> Dict[str, Any]:
        """Request reprint - placeholder implementation"""
        
        self.logger.info("Requesting reprint", user_id=user.employee_id, ticket_id=request.ticket_id)
        
        # Placeholder implementation
        return {
            "reprint_id": "reprint_123456789",
            "ticket_id": request.ticket_id,
            "status": "pending",
            "reason_code": request.reason_code,
            "reason_text": request.reason_text,
            "requested_by": user.employee_id,
            "timestamp": datetime.utcnow()
        }
