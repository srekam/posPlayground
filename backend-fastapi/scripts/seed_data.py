"""
Seed script to populate database with initial data
"""
import asyncio
import os
import sys
from datetime import datetime
from ulid import ULID

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.mongo import get_database
from app.models.taxes import Tax
from app.models.payment_types import PaymentType
from app.models.discounts import Discount, DiscountType, DiscountScope
from app.models.settings import Setting
from app.models.approvals import ReasonCode
from app.models.feature_flags import FeatureFlag


async def seed_initial_data():
    """Seed the database with initial data"""
    print("Starting database seeding...")
    
    try:
        # Get database
        db = await get_database()
        
        # Seed taxes
        await seed_taxes(db)
        
        # Seed payment types
        await seed_payment_types(db)
        
        # Seed discounts
        await seed_discounts(db)
        
        # Seed settings
        await seed_settings(db)
        
        # Seed reason codes
        await seed_reason_codes(db)
        
        # Seed feature flags
        await seed_feature_flags(db)
        
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        raise


async def seed_taxes(db):
    """Seed default taxes"""
    print("Seeding taxes...")
    
    taxes_collection = db.taxes
    
    # Check if taxes already exist
    existing_tax = await taxes_collection.find_one({"tenant_id": "default"})
    if existing_tax:
        print("Taxes already exist, skipping...")
        return
    
    # Default VAT tax
    default_tax = Tax(
        tenant_id="default",
        name="VAT 7%",
        rate=7.0,
        type="percentage",
        active=True,
        description="Standard VAT rate for Thailand"
    )
    
    await taxes_collection.insert_one(default_tax.dict(by_alias=True, exclude={"id"}))
    print("✓ Default tax created")


async def seed_payment_types(db):
    """Seed default payment types"""
    print("Seeding payment types...")
    
    payment_types_collection = db.payment_types
    
    # Check if payment types already exist
    existing_payment_type = await payment_types_collection.find_one({"tenant_id": "default"})
    if existing_payment_type:
        print("Payment types already exist, skipping...")
        return
    
    payment_types = [
        PaymentType(
            tenant_id="default",
            name="Cash",
            code="CASH",
            method="cash",
            active=True,
            description="Cash payment",
            requires_reference=False
        ),
        PaymentType(
            tenant_id="default",
            name="QR Code",
            code="QR",
            method="qr",
            active=True,
            description="QR code payment",
            requires_reference=True
        ),
        PaymentType(
            tenant_id="default",
            name="Credit Card",
            code="CARD",
            method="card",
            active=True,
            description="Credit/Debit card payment",
            requires_reference=True
        )
    ]
    
    for payment_type in payment_types:
        await payment_types_collection.insert_one(payment_type.dict(by_alias=True, exclude={"id"}))
    
    print("✓ Default payment types created")


async def seed_discounts(db):
    """Seed default discounts"""
    print("Seeding discounts...")
    
    discounts_collection = db.discounts
    
    # Check if discounts already exist
    existing_discount = await discounts_collection.find_one({"tenant_id": "default"})
    if existing_discount:
        print("Discounts already exist, skipping...")
        return
    
    # Sample discount
    sample_discount = Discount(
        tenant_id="default",
        name="Early Bird 10%",
        code="EARLY10",
        type=DiscountType.PERCENTAGE,
        value=10.0,
        scope=DiscountScope.GLOBAL,
        scope_ids=[],
        min_amount=10000,  # 100 THB in satang
        max_amount=100000,  # 1000 THB in satang
        active=True,
        description="10% discount for early bird customers",
        conditions={"time_start": "06:00", "time_end": "10:00"}
    )
    
    await discounts_collection.insert_one(sample_discount.dict(by_alias=True, exclude={"id"}))
    print("✓ Default discount created")


async def seed_settings(db):
    """Seed default settings"""
    print("Seeding settings...")
    
    settings_collection = db.settings
    
    # Check if settings already exist
    existing_setting = await settings_collection.find_one({"tenant_id": "default"})
    if existing_setting:
        print("Settings already exist, skipping...")
        return
    
    default_settings = [
        Setting(
            tenant_id="default",
            store_id=None,
            key="currency",
            value="THB",
            type="string",
            description="Default currency",
            category="general"
        ),
        Setting(
            tenant_id="default",
            store_id=None,
            key="timezone",
            value="Asia/Bangkok",
            type="string",
            description="Default timezone",
            category="general"
        ),
        Setting(
            tenant_id="default",
            store_id=None,
            key="receipt_footer",
            value="Thank you for your visit!",
            type="string",
            description="Receipt footer text",
            category="receipt"
        ),
        Setting(
            tenant_id="default",
            store_id=None,
            key="max_open_tickets",
            value=10,
            type="integer",
            description="Maximum number of open tickets per device",
            category="pos"
        ),
        Setting(
            tenant_id="default",
            store_id=None,
            key="ticket_expiry_minutes",
            value=30,
            type="integer",
            description="Default ticket expiry time in minutes",
            category="pos"
        )
    ]
    
    for setting in default_settings:
        await settings_collection.insert_one(setting.dict(by_alias=True, exclude={"id"}))
    
    print("✓ Default settings created")


async def seed_reason_codes(db):
    """Seed default reason codes"""
    print("Seeding reason codes...")
    
    reason_codes_collection = db.reason_codes
    
    # Check if reason codes already exist
    existing_reason_code = await reason_codes_collection.find_one({"tenant_id": "default"})
    if existing_reason_code:
        print("Reason codes already exist, skipping...")
        return
    
    reason_codes = [
        ReasonCode(
            tenant_id="default",
            code="DEFECTIVE",
            name="Defective Product",
            category="refund",
            description="Product was defective or damaged",
            requires_approval=True,
            active=True
        ),
        ReasonCode(
            tenant_id="default",
            code="WRONG_ITEM",
            name="Wrong Item",
            category="refund",
            description="Wrong item was sold",
            requires_approval=False,
            active=True
        ),
        ReasonCode(
            tenant_id="default",
            code="CUSTOMER_CHANGE",
            name="Customer Changed Mind",
            category="refund",
            description="Customer changed their mind",
            requires_approval=True,
            active=True
        ),
        ReasonCode(
            tenant_id="default",
            code="LOST_TICKET",
            name="Lost Ticket",
            category="reprint",
            description="Customer lost their ticket",
            requires_approval=False,
            active=True
        ),
        ReasonCode(
            tenant_id="default",
            code="DAMAGED_TICKET",
            name="Damaged Ticket",
            category="reprint",
            description="Ticket was damaged",
            requires_approval=False,
            active=True
        )
    ]
    
    for reason_code in reason_codes:
        await reason_codes_collection.insert_one(reason_code.dict(by_alias=True, exclude={"id"}))
    
    print("✓ Default reason codes created")


async def seed_feature_flags(db):
    """Seed default feature flags"""
    print("Seeding feature flags...")
    
    feature_flags_collection = db.feature_flags
    
    # Check if feature flags already exist
    existing_feature_flag = await feature_flags_collection.find_one({"key": "new_checkout_flow"})
    if existing_feature_flag:
        print("Feature flags already exist, skipping...")
        return
    
    feature_flags = [
        FeatureFlag(
            key="new_checkout_flow",
            enabled=False,
            tenant_id=None,
            store_id=None,
            conditions={},
            description="Enable new checkout flow"
        ),
        FeatureFlag(
            key="loyalty_program",
            enabled=True,
            tenant_id=None,
            store_id=None,
            conditions={},
            description="Enable loyalty program"
        ),
        FeatureFlag(
            key="advanced_reporting",
            enabled=False,
            tenant_id=None,
            store_id=None,
            conditions={},
            description="Enable advanced reporting features"
        ),
        FeatureFlag(
            key="multi_language",
            enabled=False,
            tenant_id=None,
            store_id=None,
            conditions={},
            description="Enable multi-language support"
        )
    ]
    
    for feature_flag in feature_flags:
        await feature_flags_collection.insert_one(feature_flag.dict(by_alias=True, exclude={"id"}))
    
    print("✓ Default feature flags created")


if __name__ == "__main__":
    asyncio.run(seed_initial_data())
