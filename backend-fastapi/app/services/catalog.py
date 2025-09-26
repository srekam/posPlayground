"""Catalog Service - Complete Implementation"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from app.repositories.catalog import CatalogRepository
from app.models.catalog import Product, Package, PricingRule, AccessZone
from app.utils.logging import LoggerMixin
from app.utils.errors import PlayParkException, ErrorCode


class CatalogService(LoggerMixin):
    def __init__(self, catalog_repo: CatalogRepository):
        self.catalog_repo = catalog_repo
    
    async def get_packages(self, store_id: str, user) -> List[Dict[str, Any]]:
        """Get packages for a store"""
        self.logger.info("Getting packages", store_id=store_id, user_id=user.employee_id)
        
        try:
            packages = await self.catalog_repo.get_packages_by_store(store_id)
            
            # Convert to response format
            return [
                {
                    "id": package.id,
                    "name": package.name,
                    "description": package.description,
                    "price": package.price,
                    "duration": package.duration,
                    "access_zones": package.access_zones,
                    "is_active": package.is_active,
                    "created_at": package.created_at
                }
                for package in packages
            ]
        except Exception as e:
            self.logger.error("Error getting packages", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to retrieve packages"
            )
    
    async def get_pricing_rules(self, store_id: str, user) -> List[Dict[str, Any]]:
        """Get pricing rules for a store"""
        self.logger.info("Getting pricing rules", store_id=store_id, user_id=user.employee_id)
        
        try:
            pricing_rules = await self.catalog_repo.get_pricing_rules_by_store(store_id)
            
            # Convert to response format
            return [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "description": rule.description,
                    "multiplier": rule.multiplier,
                    "days": rule.days,
                    "dates": rule.dates,
                    "is_active": rule.is_active,
                    "created_at": rule.created_at
                }
                for rule in pricing_rules
            ]
        except Exception as e:
            self.logger.error("Error getting pricing rules", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to retrieve pricing rules"
            )
    
    async def calculate_pricing(self, package_id: str, quantity: int, user, apply_rules: bool = True) -> Dict[str, Any]:
        """Calculate pricing for a package with optional rules"""
        self.logger.info("Calculating pricing", package_id=package_id, quantity=quantity, user_id=user.employee_id)
        
        try:
            # Get package
            package = await self.catalog_repo.get_package_by_id(package_id)
            if not package:
                raise PlayParkException(
                    error_code=ErrorCode.NOT_FOUND,
                    message="Package not found"
                )
            
            base_price = Decimal(str(package.price)) * quantity
            final_price = base_price
            
            if apply_rules:
                # Get applicable pricing rules
                rules = await self.catalog_repo.get_pricing_rules_by_store(user.store_id)
                
                # Apply rules (simplified logic - in real app, you'd have more complex rule matching)
                for rule in rules:
                    if rule.is_active:
                        # Simple weekend/holiday check
                        current_date = datetime.now()
                        if current_date.weekday() in [5, 6]:  # Saturday, Sunday
                            final_price = base_price * Decimal(str(rule.multiplier))
                            break
            
            return {
                "package_id": package_id,
                "package_name": package.name,
                "quantity": quantity,
                "base_price": float(base_price),
                "final_price": float(final_price),
                "discount_amount": float(base_price - final_price),
                "discount_percentage": float((base_price - final_price) / base_price * 100) if base_price > 0 else 0
            }
            
        except PlayParkException:
            raise
        except Exception as e:
            self.logger.error("Error calculating pricing", error=str(e))
            raise PlayParkException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Failed to calculate pricing"
            )
