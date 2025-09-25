"""
Catalog Repository
"""
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from app.repositories.base import BaseRepository
from app.models.catalog import Product, Category, Package, AccessZone, PricingRule
from app.utils.logging import LoggerMixin

logger = structlog.get_logger(__name__)


class CatalogRepository(BaseRepository, LoggerMixin):
    """Catalog repository"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "products")
        self.categories_collection = db["categories"]
        self.packages_collection = db["packages"]
        self.access_zones_collection = db["access_zones"]
        self.pricing_rules_collection = db["pricing_rules"]
    
    # Product methods
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        return await self.get_by_id(product_id)
    
    async def get_products_by_store(self, store_id: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get products by store"""
        cursor = self.collection.find({"store_id": store_id}).skip(skip).limit(limit)
        return [Product(**doc) async for doc in cursor]
    
    async def search_products(self, query: str, store_id: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Search products"""
        search_filter = {
            "store_id": store_id,
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"sku": {"$regex": query, "$options": "i"}}
            ]
        }
        cursor = self.collection.find(search_filter).skip(skip).limit(limit)
        return [Product(**doc) async for doc in cursor]
    
    async def get_products_by_category(self, category_id: str, store_id: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get products by category"""
        cursor = self.collection.find({"category_id": category_id, "store_id": store_id}).skip(skip).limit(limit)
        return [Product(**doc) async for doc in cursor]
    
    async def create_product(self, product: Product) -> Product:
        """Create a new product"""
        return await self.create(product)
    
    async def update_product(self, product_id: str, updates: Dict[str, Any]) -> Optional[Product]:
        """Update product"""
        return await self.update_by_id(product_id, updates)
    
    async def delete_product(self, product_id: str) -> bool:
        """Delete product"""
        return await self.delete_by_id(product_id)
    
    # Category methods
    async def get_category_by_id(self, category_id: str) -> Optional[Category]:
        """Get category by ID"""
        doc = await self.categories_collection.find_one({"_id": category_id})
        return Category(**doc) if doc else None
    
    async def get_categories_by_store(self, store_id: str) -> List[Category]:
        """Get categories by store"""
        cursor = self.categories_collection.find({"store_id": store_id})
        return [Category(**doc) async for doc in cursor]
    
    async def create_category(self, category: Category) -> Category:
        """Create a new category"""
        doc = await self.categories_collection.insert_one(category.dict())
        category.id = doc.inserted_id
        return category
    
    # Package methods
    async def get_package_by_id(self, package_id: str) -> Optional[Package]:
        """Get package by ID"""
        doc = await self.packages_collection.find_one({"_id": package_id})
        return Package(**doc) if doc else None
    
    async def get_packages_by_store(self, store_id: str) -> List[Package]:
        """Get packages by store"""
        cursor = self.packages_collection.find({"store_id": store_id})
        return [Package(**doc) async for doc in cursor]
    
    async def create_package(self, package: Package) -> Package:
        """Create a new package"""
        doc = await self.packages_collection.insert_one(package.dict())
        package.id = doc.inserted_id
        return package
    
    # Access Zone methods
    async def get_access_zone_by_id(self, zone_id: str) -> Optional[AccessZone]:
        """Get access zone by ID"""
        doc = await self.access_zones_collection.find_one({"_id": zone_id})
        return AccessZone(**doc) if doc else None
    
    async def get_access_zones_by_store(self, store_id: str) -> List[AccessZone]:
        """Get access zones by store"""
        cursor = self.access_zones_collection.find({"store_id": store_id})
        return [AccessZone(**doc) async for doc in cursor]
    
    async def create_access_zone(self, zone: AccessZone) -> AccessZone:
        """Create a new access zone"""
        doc = await self.access_zones_collection.insert_one(zone.dict())
        zone.id = doc.inserted_id
        return zone
    
    # Pricing Rule methods
    async def get_pricing_rule_by_id(self, rule_id: str) -> Optional[PricingRule]:
        """Get pricing rule by ID"""
        doc = await self.pricing_rules_collection.find_one({"_id": rule_id})
        return PricingRule(**doc) if doc else None
    
    async def get_pricing_rules_by_store(self, store_id: str) -> List[PricingRule]:
        """Get pricing rules by store"""
        cursor = self.pricing_rules_collection.find({"store_id": store_id})
        return [PricingRule(**doc) async for doc in cursor]
    
    async def create_pricing_rule(self, rule: PricingRule) -> PricingRule:
        """Create a new pricing rule"""
        doc = await self.pricing_rules_collection.insert_one(rule.dict())
        rule.id = doc.inserted_id
        return rule
