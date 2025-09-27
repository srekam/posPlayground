"""
Repository for Media Assets operations
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

from beanie import PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.media_assets import (
    MediaAsset, 
    ProductImageMapping, 
    OwnerType, 
    ACLType,
    ImageVariant
)
from ..utils.errors import NotFoundError, ValidationError


class MediaAssetRepository:
    """Repository for media asset operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.media_assets
        self.product_images_collection = db.product_images
    
    async def create_asset(self, asset: MediaAsset) -> MediaAsset:
        """Create a new media asset"""
        try:
            await asset.insert()
            return asset
        except Exception as e:
            raise ValidationError(f"Failed to create media asset: {str(e)}")
    
    async def get_asset_by_id(self, asset_id: str, tenant_id: str) -> Optional[MediaAsset]:
        """Get media asset by ID"""
        try:
            asset = await MediaAsset.find_one(
                MediaAsset.asset_id == asset_id,
                MediaAsset.tenant_id == tenant_id,
                MediaAsset.deleted_at == None
            )
            return asset
        except Exception as e:
            raise ValidationError(f"Failed to get media asset: {str(e)}")
    
    async def get_assets_by_owner(
        self, 
        tenant_id: str, 
        owner_type: OwnerType, 
        owner_id: str,
        include_deleted: bool = False
    ) -> List[MediaAsset]:
        """Get all assets for a specific owner"""
        try:
            query = {
                "tenant_id": tenant_id,
                "owner_type": owner_type.value,
                "owner_id": owner_id
            }
            
            if not include_deleted:
                query["deleted_at"] = None
            
            assets = await MediaAsset.find(query).sort([("created_at", -1)]).to_list()
            return assets
        except Exception as e:
            raise ValidationError(f"Failed to get assets by owner: {str(e)}")
    
    async def update_asset(self, asset: MediaAsset) -> MediaAsset:
        """Update an existing media asset"""
        try:
            asset.updated_at = datetime.utcnow()
            await asset.save()
            return asset
        except Exception as e:
            raise ValidationError(f"Failed to update media asset: {str(e)}")
    
    async def soft_delete_asset(self, asset_id: str, tenant_id: str) -> bool:
        """Soft delete a media asset"""
        try:
            asset = await self.get_asset_by_id(asset_id, tenant_id)
            if not asset:
                raise NotFoundError(f"Media asset {asset_id} not found")
            
            asset.deleted_at = datetime.utcnow()
            await asset.save()
            return True
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise e
            raise ValidationError(f"Failed to delete media asset: {str(e)}")
    
    async def hard_delete_asset(self, asset_id: str, tenant_id: str) -> bool:
        """Hard delete a media asset"""
        try:
            result = await MediaAsset.find_one(
                MediaAsset.asset_id == asset_id,
                MediaAsset.tenant_id == tenant_id
            ).delete()
            return result.deleted_count > 0
        except Exception as e:
            raise ValidationError(f"Failed to hard delete media asset: {str(e)}")
    
    async def find_duplicate_asset(self, hash_sha256: str, tenant_id: str) -> Optional[MediaAsset]:
        """Find duplicate asset by hash"""
        try:
            asset = await MediaAsset.find_one(
                MediaAsset.hash_sha256 == hash_sha256,
                MediaAsset.tenant_id == tenant_id,
                MediaAsset.deleted_at == None
            )
            return asset
        except Exception as e:
            raise ValidationError(f"Failed to find duplicate asset: {str(e)}")
    
    async def update_processing_status(
        self, 
        asset_id: str, 
        status: str, 
        error: Optional[str] = None
    ) -> bool:
        """Update asset processing status"""
        try:
            asset = await MediaAsset.find_one(MediaAsset.asset_id == asset_id)
            if not asset:
                return False
            
            asset.processing_status = status
            asset.processing_error = error
            asset.updated_at = datetime.utcnow()
            await asset.save()
            return True
        except Exception as e:
            raise ValidationError(f"Failed to update processing status: {str(e)}")
    
    async def add_variant(
        self, 
        asset_id: str, 
        variant_name: str, 
        variant_data: ImageVariant
    ) -> bool:
        """Add image variant to asset"""
        try:
            asset = await MediaAsset.find_one(MediaAsset.asset_id == asset_id)
            if not asset:
                return False
            
            asset.variants[variant_name] = variant_data
            asset.updated_at = datetime.utcnow()
            await asset.save()
            return True
        except Exception as e:
            raise ValidationError(f"Failed to add variant: {str(e)}")
    
    async def get_assets_by_status(
        self, 
        tenant_id: str, 
        status: str, 
        limit: int = 100
    ) -> List[MediaAsset]:
        """Get assets by processing status"""
        try:
            assets = await MediaAsset.find(
                MediaAsset.tenant_id == tenant_id,
                MediaAsset.processing_status == status,
                MediaAsset.deleted_at == None
            ).limit(limit).to_list()
            return assets
        except Exception as e:
            raise ValidationError(f"Failed to get assets by status: {str(e)}")


class ProductImageRepository:
    """Repository for product image mapping operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.product_images
    
    async def create_mapping(self, mapping: ProductImageMapping) -> ProductImageMapping:
        """Create a new product image mapping"""
        try:
            await mapping.insert()
            return mapping
        except Exception as e:
            raise ValidationError(f"Failed to create product image mapping: {str(e)}")
    
    async def get_product_images(
        self, 
        product_id: str, 
        include_assets: bool = False
    ) -> List[ProductImageMapping]:
        """Get all images for a product"""
        try:
            mappings = await ProductImageMapping.find(
                ProductImageMapping.product_id == product_id
            ).sort([("sort_order", 1)]).to_list()
            
            if include_assets:
                # Fetch the actual media assets
                for mapping in mappings:
                    asset = await MediaAsset.find_one(
                        MediaAsset.asset_id == mapping.asset_id,
                        MediaAsset.deleted_at == None
                    )
                    if asset:
                        mapping.asset = asset
            
            return mappings
        except Exception as e:
            raise ValidationError(f"Failed to get product images: {str(e)}")
    
    async def get_primary_image(self, product_id: str) -> Optional[ProductImageMapping]:
        """Get primary image for a product"""
        try:
            mapping = await ProductImageMapping.find_one(
                ProductImageMapping.product_id == product_id,
                ProductImageMapping.is_primary == True
            )
            return mapping
        except Exception as e:
            raise ValidationError(f"Failed to get primary image: {str(e)}")
    
    async def set_primary_image(
        self, 
        product_id: str, 
        asset_id: str
    ) -> bool:
        """Set primary image for a product"""
        try:
            # Remove primary flag from all other images
            await ProductImageMapping.find(
                ProductImageMapping.product_id == product_id
            ).update({"$set": {"is_primary": False}})
            
            # Set new primary image
            result = await ProductImageMapping.find(
                ProductImageMapping.product_id == product_id,
                ProductImageMapping.asset_id == asset_id
            ).update({"$set": {"is_primary": True, "updated_at": datetime.utcnow()}})
            
            return result.modified_count > 0
        except Exception as e:
            raise ValidationError(f"Failed to set primary image: {str(e)}")
    
    async def reorder_images(
        self, 
        product_id: str, 
        asset_ids: List[str]
    ) -> bool:
        """Reorder product images"""
        try:
            # Update sort order for each asset
            for index, asset_id in enumerate(asset_ids):
                await ProductImageMapping.find(
                    ProductImageMapping.product_id == product_id,
                    ProductImageMapping.asset_id == asset_id
                ).update({"$set": {"sort_order": index, "updated_at": datetime.utcnow()}})
            
            return True
        except Exception as e:
            raise ValidationError(f"Failed to reorder images: {str(e)}")
    
    async def remove_image_mapping(self, product_id: str, asset_id: str) -> bool:
        """Remove image mapping for a product"""
        try:
            result = await ProductImageMapping.find(
                ProductImageMapping.product_id == product_id,
                ProductImageMapping.asset_id == asset_id
            ).delete()
            return result.deleted_count > 0
        except Exception as e:
            raise ValidationError(f"Failed to remove image mapping: {str(e)}")
    
    async def get_images_by_asset(self, asset_id: str) -> List[ProductImageMapping]:
        """Get all product mappings for an asset"""
        try:
            mappings = await ProductImageMapping.find(
                ProductImageMapping.asset_id == asset_id
            ).to_list()
            return mappings
        except Exception as e:
            raise ValidationError(f"Failed to get images by asset: {str(e)}")
