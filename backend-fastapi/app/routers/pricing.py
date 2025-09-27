"""
Pricing Router
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from ulid import ULID

from app.models.pricing import (
    PricingRule, PriceList, PriceListItem,
    PricingPreviewRequest, PricingPreviewResponse, PricingPreviewItem
)
from app.repositories.pricing import PricingRuleRepository, PriceListRepository, PriceListItemRepository
from app.repositories.taxes import TaxRepository
from app.repositories.discounts import DiscountRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.deps import get_current_user, get_db

router = APIRouter()


@router.post("/preview", response_model=PricingPreviewResponse)
async def preview_pricing(
    request: PricingPreviewRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Preview pricing with all rules, discounts, and taxes applied"""
    try:
        # Initialize repositories
        pricing_rule_repo = PricingRuleRepository()
        price_list_repo = PriceListRepository()
        price_item_repo = PriceListItemRepository()
        tax_repo = TaxRepository()
        discount_repo = DiscountRepository()
        
        # Get active pricing rules
        pricing_rules = await pricing_rule_repo.get_active_by_tenant(current_user.tenant_id)
        
        # Get active price lists
        price_lists = await price_list_repo.get_active_by_tenant(current_user.tenant_id)
        
        # Get active taxes
        taxes = await tax_repo.get_active_by_tenant(current_user.tenant_id)
        
        # Process each item
        priced_items = []
        subtotal = 0
        
        for item in request.items:
            product_id = item["product_id"]
            package_id = item.get("package_id")
            quantity = item["quantity"]
            base_price = item["unit_price"]
            
            # Apply price list pricing if available
            final_price = base_price
            applied_price_list = None
            
            for price_list in price_lists:
                price_item = await price_item_repo.get_product_price(
                    price_list.id, product_id, package_id, quantity
                )
                if price_item:
                    final_price = price_item.price
                    applied_price_list = price_list.name
                    break
            
            # Apply pricing rules
            applied_rules = []
            for rule in pricing_rules:
                # Check if rule applies to this item
                if rule.scope == "global" or product_id in rule.scope_ids:
                    # Apply rule (simplified logic)
                    if rule.type == "discount":
                        if rule.actions.get("percentage"):
                            discount_amount = int(final_price * quantity * rule.actions["percentage"] / 100)
                            final_price = max(0, final_price - discount_amount // quantity)
                        elif rule.actions.get("fixed_amount"):
                            discount_amount = rule.actions["fixed_amount"]
                            final_price = max(0, final_price - discount_amount)
                    
                    applied_rules.append({
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "type": rule.type,
                        "actions": rule.actions
                    })
            
            # Calculate line total
            line_total = final_price * quantity
            
            # Apply discounts
            applied_discounts = []
            if request.customer_id:
                # Check for customer-specific discounts
                customer_discounts = await discount_repo.get_by_scope(
                    current_user.tenant_id, "customer", [request.customer_id]
                )
                for discount in customer_discounts:
                    if discount.min_amount and line_total >= discount.min_amount:
                        if discount.type == "percentage":
                            discount_amount = int(line_total * discount.value / 100)
                        else:  # fixed
                            discount_amount = int(discount.value * 100)  # Convert to satang
                        
                        line_total = max(0, line_total - discount_amount)
                        applied_discounts.append({
                            "discount_id": discount.id,
                            "discount_name": discount.name,
                            "type": discount.type,
                            "amount": discount_amount
                        })
            
            # Apply taxes
            applied_taxes = []
            for tax in taxes:
                if tax.type == "percentage":
                    tax_amount = int(line_total * tax.rate / 100)
                else:  # fixed
                    tax_amount = int(tax.rate * 100)  # Convert to satang
                
                applied_taxes.append({
                    "tax_id": str(tax.id),
                    "tax_name": tax.name,
                    "rate": tax.rate,
                    "type": tax.type,
                    "amount": tax_amount
                })
            
            priced_items.append(PricingPreviewItem(
                product_id=product_id,
                package_id=package_id,
                quantity=quantity,
                unit_price=final_price,
                line_total=line_total,
                discounts=applied_discounts,
                taxes=applied_taxes
            ))
            
            subtotal += line_total
        
        # Calculate totals
        discount_total = sum(
            sum(d["amount"] for d in item.discounts)
            for item in priced_items
        )
        
        tax_total = sum(
            sum(t["amount"] for t in item.taxes)
            for item in priced_items
        )
        
        grand_total = subtotal - discount_total + tax_total
        
        return PricingPreviewResponse(
            items=priced_items,
            subtotal=subtotal,
            discount_total=discount_total,
            tax_total=tax_total,
            grand_total=grand_total,
            applied_rules=applied_rules,
            price_list=applied_price_list
        )
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to preview pricing",
            details={"error": str(e)}
        )


@router.get("/rules", response_model=List[Dict[str, Any]])
async def get_pricing_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get pricing rules"""
    try:
        pricing_rule_repo = PricingRuleRepository()
        
        if active_only:
            rules = await pricing_rule_repo.get_active_by_tenant(current_user.tenant_id)
        else:
            rules = await pricing_rule_repo.get_many({"tenant_id": current_user.tenant_id}, skip, limit)
        
        return [
            {
                "id": str(rule.id),
                "name": rule.name,
                "type": rule.type,
                "scope": rule.scope,
                "scope_ids": rule.scope_ids,
                "priority": rule.priority,
                "conditions": rule.conditions,
                "actions": rule.actions,
                "active": rule.active,
                "valid_from": rule.valid_from,
                "valid_until": rule.valid_until,
                "created_at": rule.created_at,
                "updated_at": rule.updated_at
            }
            for rule in rules
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve pricing rules",
            details={"error": str(e)}
        )


@router.post("/rules", status_code=201)
async def create_pricing_rule(
    rule_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new pricing rule"""
    try:
        pricing_rule_repo = PricingRuleRepository()
        
        # Create pricing rule document
        rule = PricingRule(
            tenant_id=current_user.tenant_id,
            name=rule_data["name"],
            type=rule_data["type"],
            scope=rule_data["scope"],
            scope_ids=rule_data.get("scope_ids", []),
            priority=rule_data.get("priority", 0),
            conditions=rule_data.get("conditions", {}),
            actions=rule_data["actions"],
            active=rule_data.get("active", True),
            valid_from=rule_data.get("valid_from"),
            valid_until=rule_data.get("valid_until")
        )
        
        created_rule = await pricing_rule_repo.create(rule)
        
        return {
            "id": str(created_rule.id),
            "message": "Pricing rule created successfully"
        }
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to create pricing rule",
            details={"error": str(e)}
        )


@router.get("/price-lists", response_model=List[Dict[str, Any]])
async def get_price_lists(
    active_only: bool = Query(True),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get price lists"""
    try:
        price_list_repo = PriceListRepository()
        
        if active_only:
            price_lists = await price_list_repo.get_active_by_tenant(current_user.tenant_id)
        else:
            price_lists = await price_list_repo.get_many({"tenant_id": current_user.tenant_id})
        
        return [
            {
                "id": str(price_list.id),
                "name": price_list.name,
                "code": price_list.code,
                "description": price_list.description,
                "active": price_list.active,
                "priority": price_list.priority,
                "valid_from": price_list.valid_from,
                "valid_until": price_list.valid_until,
                "created_at": price_list.created_at,
                "updated_at": price_list.updated_at
            }
            for price_list in price_lists
        ]
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to retrieve price lists",
            details={"error": str(e)}
        )


@router.post("/price-lists", status_code=201)
async def create_price_list(
    price_list_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new price list"""
    try:
        price_list_repo = PriceListRepository()
        
        # Create price list document
        price_list = PriceList(
            tenant_id=current_user.tenant_id,
            name=price_list_data["name"],
            code=price_list_data["code"],
            description=price_list_data.get("description"),
            active=price_list_data.get("active", True),
            priority=price_list_data.get("priority", 0),
            valid_from=price_list_data.get("valid_from"),
            valid_until=price_list_data.get("valid_until")
        )
        
        created_price_list = await price_list_repo.create(price_list)
        
        return {
            "id": str(created_price_list.id),
            "message": "Price list created successfully"
        }
        
    except Exception as e:
        raise PlayParkException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Failed to create price list",
            details={"error": str(e)}
        )
