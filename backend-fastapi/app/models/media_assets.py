"""
Media Assets Model for storing image and file metadata
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from beanie import Document, Indexed
from pydantic import Field, BaseModel
from ulid import ULID


class OwnerType(str, Enum):
    """Types of entities that can own media assets"""
    PRODUCT = "product"
    CATEGORY = "category"
    RECEIPT_TEMPLATE = "receipt_template"
    BRAND = "brand"
    USER = "user"
    OTHER = "other"


class ACLType(str, Enum):
    """Access control levels for media assets"""
    PUBLIC = "public"
    SIGNED = "signed"


class ImageVariant(BaseModel):
    """Image variant metadata"""
    storage_key: str = Field(..., description="Storage key for the variant")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    bytes: int = Field(..., description="File size in bytes")
    format: str = Field(..., description="Image format (webp, jpeg, png)")


class MediaAsset(Document):
    """Media asset document for storing image and file metadata"""
    
    # Primary identifiers
    asset_id: str = Field(default_factory=lambda: str(ULID()), description="Unique asset identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    store_id: Optional[str] = Field(None, description="Store identifier")
    
    # Ownership
    owner_type: OwnerType = Field(..., description="Type of entity that owns this asset")
    owner_id: str = Field(..., description="ID of the owning entity")
    
    # File metadata
    filename_original: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="MIME type of the file")
    bytes: int = Field(..., description="File size in bytes")
    
    # Image-specific metadata
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")
    
    # Storage and deduplication
    hash_sha256: str = Field(..., description="SHA256 hash for deduplication")
    storage_key: str = Field(..., description="Storage key for the original file")
    
    # Image variants
    variants: Dict[str, ImageVariant] = Field(default_factory=dict, description="Image variants (thumb, sm, md, lg)")
    
    # Access control
    acl: ACLType = Field(default=ACLType.PUBLIC, description="Access control level")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(None, description="Soft delete timestamp")
    
    # Optional metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    alt_text: Optional[str] = Field(None, description="Alternative text for accessibility")
    dominant_color: Optional[str] = Field(None, description="Dominant color hex code")
    
    # Processing status
    processing_status: str = Field(default="pending", description="Processing status: pending, processing, completed, failed")
    processing_error: Optional[str] = Field(None, description="Processing error message if any")
    
    class Settings:
        name = "media_assets"
        indexes = [
            [("tenant_id", 1), ("owner_type", 1), ("owner_id", 1)],
            [("tenant_id", 1), ("created_at", -1)],
            [("hash_sha256", 1)],
            [("asset_id", 1)],
            [("deleted_at", 1)],
            [("processing_status", 1)],
        ]
    
    def is_deleted(self) -> bool:
        """Check if asset is soft deleted"""
        return self.deleted_at is not None
    
    def get_variant_url(self, variant: str, base_url: str, signed: bool = False, ttl: int = 3600) -> Optional[str]:
        """Get URL for a specific variant"""
        if variant not in self.variants:
            return None
        
        storage_key = self.variants[variant].storage_key
        if self.acl == ACLType.PUBLIC and not signed:
            return f"{base_url}/{storage_key}"
        # For signed URLs, this would be handled by the storage service
        return f"{base_url}/{storage_key}"


class ProductImageMapping(Document):
    """Mapping between products and their images with ordering"""
    
    product_id: str = Field(..., description="Product identifier")
    asset_id: str = Field(..., description="Media asset identifier")
    sort_order: int = Field(default=0, description="Sort order for display")
    is_primary: bool = Field(default=False, description="Whether this is the primary image")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Settings:
        name = "product_images"
        indexes = [
            [("product_id", 1), ("sort_order", 1)],
            [("product_id", 1), ("is_primary", 1)],
            [("asset_id", 1)],
        ]


class MediaUploadRequest(BaseModel):
    """Request model for media upload presigning"""
    filename: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="MIME type")
    owner_type: OwnerType = Field(..., description="Type of owning entity")
    owner_id: str = Field(..., description="ID of owning entity")
    acl: ACLType = Field(default=ACLType.PUBLIC, description="Access control level")


class MediaUploadResponse(BaseModel):
    """Response model for media upload presigning"""
    upload_url: str = Field(..., description="Presigned URL for upload")
    storage_key: str = Field(..., description="Storage key for the file")
    headers: Dict[str, str] = Field(default_factory=dict, description="Required headers for upload")
    max_bytes: int = Field(..., description="Maximum file size allowed")
    asset_id: str = Field(..., description="Generated asset ID")


class MediaCompleteRequest(BaseModel):
    """Request model for completing media upload"""
    asset_id: str = Field(..., description="Asset ID from presign response")
    storage_key: str = Field(..., description="Storage key from presign response")


class MediaVariantResponse(BaseModel):
    """Response model for media variant URLs"""
    variant: str = Field(..., description="Variant name (thumb, sm, md, lg, orig)")
    url: str = Field(..., description="URL for the variant")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    bytes: int = Field(..., description="File size in bytes")
    format: str = Field(..., description="Image format")


class MediaAssetResponse(BaseModel):
    """Response model for media asset details"""
    asset_id: str = Field(..., description="Asset identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    store_id: Optional[str] = Field(None, description="Store identifier")
    owner_type: OwnerType = Field(..., description="Owner type")
    owner_id: str = Field(..., description="Owner ID")
    filename_original: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="MIME type")
    bytes: int = Field(..., description="File size")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")
    hash_sha256: str = Field(..., description="SHA256 hash")
    acl: ACLType = Field(..., description="Access control level")
    variants: List[MediaVariantResponse] = Field(default_factory=list, description="Available variants")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    tags: List[str] = Field(default_factory=list, description="Tags")
    alt_text: Optional[str] = Field(None, description="Alternative text")
    dominant_color: Optional[str] = Field(None, description="Dominant color")
    processing_status: str = Field(..., description="Processing status")


class ProductImageOrderRequest(BaseModel):
    """Request model for reordering product images"""
    asset_ids: List[str] = Field(..., description="Asset IDs in desired order")


class ProductImagePrimaryRequest(BaseModel):
    """Request model for setting primary product image"""
    asset_id: str = Field(..., description="Asset ID to set as primary")
