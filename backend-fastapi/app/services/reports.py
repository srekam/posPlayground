"""Report Service - Complete Implementation"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal

from app.repositories.reports import ReportRepository
from app.repositories.sales import SalesRepository
from app.repositories.shifts import ShiftRepository
from app.repositories.tickets import TicketRepository
from app.utils.logging import LoggerMixin
from app.utils.errors import PlayParkException, ErrorCode


class ReportService(LoggerMixin):
    def __init__(
        self, 
        report_repo: ReportRepository,
        sales_repo: SalesRepository,
        shift_repo: ShiftRepository,
        ticket_repo: TicketRepository
    ):
        self.report_repo = report_repo
        self.sales_repo = sales_repo
        self.shift_repo = shift_repo
        self.ticket_repo = ticket_repo
    
    async def get_sales_report(self, user, from_date: Optional[datetime] = None, to_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate sales report"""
        self.logger.info("Generating sales report", user_id=user.employee_id)
        
        try:
            # Set default date range if not provided
            if not from_date:
                from_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            if not to_date:
                to_date = datetime.utcnow()
            
            # Get sales data
            sales = await self.sales_repo.get_sales_by_store_and_date_range(
                user.store_id, from_date, to_date
            )
            
            # Calculate totals
            total_sales = sum(sale.grand_total for sale in sales)
            total_transactions = len(sales)
            
            # Payment method breakdown
            payment_methods = {}
            for sale in sales:
                method = sale.payment_method
                if method not in payment_methods:
                    payment_methods[method] = {"count": 0, "total": Decimal('0')}
                payment_methods[method]["count"] += 1
                payment_methods[method]["total"] += Decimal(str(sale.grand_total))
            
            # Convert to list format for frontend
            payment_method_data = [
                {
                    "name": method,
                    "value": float(data["total"]),
                    "count": data["count"]
                }
                for method, data in payment_methods.items()
            ]
            
            return {
                "total_sales": float(total_sales),
                "total_transactions": total_transactions,
                "average_transaction": float(total_sales / total_transactions) if total_transactions > 0 else 0,
                "payment_methods": payment_method_data,
                "date_range": {
                    "from": from_date.isoformat(),
                    "to": to_date.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error("Error generating sales report", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to generate sales report"
            )
    
    async def get_shifts_report(self, user, from_date: Optional[datetime] = None, to_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate shifts report"""
        self.logger.info("Generating shifts report", user_id=user.employee_id)
        
        try:
            # Set default date range if not provided
            if not from_date:
                from_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            if not to_date:
                to_date = datetime.utcnow()
            
            # Get shifts data
            shifts = await self.shift_repo.get_shifts_by_store_and_date_range(
                user.store_id, from_date, to_date
            )
            
            # Calculate totals
            total_shifts = len(shifts)
            total_sales = sum(shift.total_sales or 0 for shift in shifts)
            total_duration = sum(shift.duration_minutes or 0 for shift in shifts)
            
            # Employee breakdown
            employee_stats = {}
            for shift in shifts:
                emp_id = shift.employee_id
                if emp_id not in employee_stats:
                    employee_stats[emp_id] = {"shifts": 0, "sales": Decimal('0'), "duration": 0}
                employee_stats[emp_id]["shifts"] += 1
                employee_stats[emp_id]["sales"] += Decimal(str(shift.total_sales or 0))
                employee_stats[emp_id]["duration"] += shift.duration_minutes or 0
            
            return {
                "total_shifts": total_shifts,
                "total_sales": float(total_sales),
                "total_duration_hours": total_duration / 60,
                "average_shift_duration": total_duration / total_shifts if total_shifts > 0 else 0,
                "employee_stats": [
                    {
                        "employee_id": emp_id,
                        "shifts_count": stats["shifts"],
                        "total_sales": float(stats["sales"]),
                        "total_duration": stats["duration"]
                    }
                    for emp_id, stats in employee_stats.items()
                ],
                "date_range": {
                    "from": from_date.isoformat(),
                    "to": to_date.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error("Error generating shifts report", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to generate shifts report"
            )
    
    async def get_tickets_report(self, user, from_date: Optional[datetime] = None, to_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate tickets report"""
        self.logger.info("Generating tickets report", user_id=user.employee_id)
        
        try:
            # Set default date range if not provided
            if not from_date:
                from_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            if not to_date:
                to_date = datetime.utcnow()
            
            # Get tickets data
            issued_tickets = await self.ticket_repo.get_tickets_by_store_and_date_range(
                user.store_id, from_date, to_date
            )
            
            # Calculate totals
            total_issued = len(issued_tickets)
            total_redeemed = sum(1 for ticket in issued_tickets if ticket.status == "redeemed")
            redemption_rate = (total_redeemed / total_issued * 100) if total_issued > 0 else 0
            
            # Package breakdown
            package_stats = {}
            for ticket in issued_tickets:
                package_id = ticket.package_id
                if package_id not in package_stats:
                    package_stats[package_id] = {"issued": 0, "redeemed": 0}
                package_stats[package_id]["issued"] += 1
                if ticket.status == "redeemed":
                    package_stats[package_id]["redeemed"] += 1
            
            return {
                "total_issued": total_issued,
                "total_redeemed": total_redeemed,
                "redemption_rate": round(redemption_rate, 2),
                "package_stats": [
                    {
                        "package_id": package_id,
                        "issued": stats["issued"],
                        "redeemed": stats["redeemed"],
                        "redemption_rate": round((stats["redeemed"] / stats["issued"] * 100) if stats["issued"] > 0 else 0, 2)
                    }
                    for package_id, stats in package_stats.items()
                ],
                "date_range": {
                    "from": from_date.isoformat(),
                    "to": to_date.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error("Error generating tickets report", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to generate tickets report"
            )
    
    async def get_fraud_report(self, user, from_date: Optional[datetime] = None, to_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate fraud detection report"""
        self.logger.info("Generating fraud report", user_id=user.employee_id)
        
        try:
            # Set default date range if not provided
            if not from_date:
                from_date = datetime.utcnow() - timedelta(days=7)
            if not to_date:
                to_date = datetime.utcnow()
            
            # Get audit logs for suspicious activities
            suspicious_activities = await self.report_repo.get_suspicious_activities(
                user.store_id, from_date, to_date
            )
            
            # Analyze patterns
            fraud_indicators = []
            blocked_attempts = 0
            
            for activity in suspicious_activities:
                if activity.event_type == "fraud_detected":
                    blocked_attempts += 1
                    fraud_indicators.append({
                        "id": activity.id,
                        "type": "Fraud Detected",
                        "severity": "High",
                        "description": activity.description,
                        "timestamp": activity.timestamp,
                        "device_id": activity.device_id
                    })
                elif activity.event_type == "suspicious_activity":
                    fraud_indicators.append({
                        "id": activity.id,
                        "type": "Suspicious Activity",
                        "severity": "Medium",
                        "description": activity.description,
                        "timestamp": activity.timestamp,
                        "device_id": activity.device_id
                    })
            
            return {
                "suspicious_activities": len(fraud_indicators),
                "blocked_attempts": blocked_attempts,
                "activities": fraud_indicators[:10],  # Limit to recent 10
                "date_range": {
                    "from": from_date.isoformat(),
                    "to": to_date.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error("Error generating fraud report", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to generate fraud report"
            )
