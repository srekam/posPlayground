"""
Media API Router for file upload and management
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from ..deps import get_current_user, get_database, get_tenant_id
from ..config import settings
from ..models.core import Employee
from ..models.media_assets import (
    MediaAsset, 
    ProductImageMapping,
    MediaUploadRequest, 
    MediaUploadResponse,
    MediaCompleteRequest,
    MediaAssetResponse,
    MediaVariantResponse,
    ProductImageOrderRequest,
    ProductImagePrimaryRequest,
    OwnerType,
    ACLType
)
from ..repositories.media_assets import MediaAssetRepository, ProductImageRepository
from ..services.storage_service import storage_service
from ..services.media_processing_service import process_media_asset_task
from ..utils.errors import NotFoundError, ValidationError, StorageError
from fastapi.logger import logger

router = APIRouter(prefix="/api/v1/media", tags=["Media"])


@router.post("/uploads/test-presign")
async def test_presign_upload(request: MediaUploadRequest):
    """Test endpoint for generating presigned URL without authentication"""
    try:
        # Use default values for testing
        tenant_id = "test-tenant"
        
        # Generate a simple asset ID
        import uuid
        asset_id = str(uuid.uuid4())
        
        # Create a mock presigned URL response
        response_data = {
            "upload_url": f"https://storage.example.com/bucket/tenants/{tenant_id}/products/{request.owner_id}/{asset_id}/orig.jpg",
            "storage_key": f"tenants/{tenant_id}/products/{request.owner_id}/{asset_id}/orig.jpg",
            "headers": {
                "Content-Type": request.mime_type,
                "x-amz-algorithm": "AWS4-HMAC-SHA256",
                "x-amz-credential": "test-credential",
                "x-amz-date": "20231201T120000Z",
                "x-amz-signature": "test-signature"
            },
            "max_bytes": 10485760,
            "asset_id": asset_id
        }
        
        return {
            "success": True,
            "data": response_data,
            "message": "Presigned URL generated successfully"
        }
        
    except Exception as e:
        logger.error("Failed to generate test presigned URL", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate presigned URL: {str(e)}"
        )


@router.post("/test-complete")
async def test_complete_upload(request: MediaCompleteRequest):
    """Test endpoint for completing upload without authentication"""
    try:
        # Mock successful completion
        response_data = {
            "asset_id": request.asset_id,
            "storage_key": request.storage_key,
            "status": "completed",
            "url": f"https://storage.example.com/bucket/{request.storage_key}",
            "created_at": "2023-12-01T12:00:00Z"
        }
        
        return {
            "success": True,
            "data": response_data,
            "message": "Upload completed successfully"
        }
        
    except Exception as e:
        logger.error("Failed to complete test upload", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete upload: {str(e)}"
        )


@router.post("/uploads/presign", response_model=MediaUploadResponse)
async def presign_upload(
    request: MediaUploadRequest,
    current_user: Employee = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_database)
):
    """Generate presigned URL for file upload"""
    try:
        # Validate MIME type
        if request.mime_type not in settings.allowed_mime_types_list:
            raise HTTPException(
                status_code=400,
                detail=f"MIME type {request.mime_type} not allowed"
            )
        
        # Generate asset ID and storage key
        asset_id = MediaAsset().asset_id  # This will generate a new ULID
        storage_key = storage_service.generate_storage_key(
            tenant_id,
            request.owner_type.value,
            request.owner_id,
            asset_id,
            request.filename
        )
        
        # Generate presigned upload URL
        upload_url, fields = storage_service.generate_presigned_upload_url(
            storage_key,
            request.mime_type
        )
        
        return MediaUploadResponse(
            upload_url=upload_url,
            storage_key=storage_key,
            headers=fields,
            max_bytes=settings.S3_MAX_FILE_SIZE,
            asset_id=asset_id
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {str(e)}")


@router.post("/complete")
async def complete_upload(
    request: MediaCompleteRequest,
    background_tasks: BackgroundTasks,
    current_user: Employee = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_database)
):
    """Complete file upload and create media asset record"""
    try:
        media_repo = MediaAssetRepository(db)
        
        # Check if file exists in storage
        if not storage_service.file_exists(request.storage_key):
            raise HTTPException(status_code=404, detail="File not found in storage")
        
        # Get file info from storage
        file_info = storage_service.get_file_info(request.storage_key)
        if not file_info:
            raise HTTPException(status_code=500, detail="Failed to get file information")
        
        # Validate file
        # Note: In a real implementation, you'd download and validate the file
        # For now, we'll trust the storage metadata
        
        # Calculate file hash (you'd need to download the file for this)
        # hash_sha256 = storage_service.calculate_file_hash(file_obj)
        
        # Get image dimensions if it's an image
        width, height = None, None
        dominant_color = None
        
        if file_info['content_type'].startswith('image/'):
            # Download file to get dimensions and dominant color
            # In production, you might want to do this asynchronously
            try:
                # This is a simplified version - in practice you'd download the file
                # and use storage_service.get_image_dimensions() and extract_dominant_color()
                pass
            except Exception:
                pass  # Continue without dimensions if extraction fails
        
        # For now, we'll need to store the presign request data somewhere
        # In a real implementation, you'd store this temporarily or pass it through
        # For this example, we'll use default values
        
        # Create media asset record
        asset = MediaAsset(
            asset_id=request.asset_id,
            tenant_id=tenant_id,
            owner_type=OwnerType.OTHER,  # You'd get this from the presign request
            owner_id="temp",  # You'd get this from the presign request
            filename_original="uploaded_file",  # You'd get this from the presign request
            mime_type=file_info['content_type'],
            bytes=file_info['size'],
            width=width,
            height=height,
            hash_sha256="temp_hash",  # You'd calculate this from the actual file
            storage_key=request.storage_key,
            acl=ACLType.PUBLIC,
            processing_status="pending"
        )
        
        # Save to database
        await media_repo.create_asset(asset)
        
        # Queue background processing for variants
        if asset.mime_type.startswith('image/') and settings.MEDIA_PROCESSING_ENABLED:
            background_tasks.add_task(
                process_media_asset_task,
                request.asset_id,
                tenant_id
            )
        
        return {
            "success": True,
            "asset_id": request.asset_id,
            "processing_status": "pending"
        }
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete upload: {str(e)}")


@router.get("", response_model=List[MediaAssetResponse])
async def list_assets(
    owner_type: Optional[OwnerType] = Query(None, description="Filter by owner type"),
    owner_id: Optional[str] = Query(None, description="Filter by owner ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of assets to return"),
    offset: int = Query(0, ge=0, description="Number of assets to skip"),
    current_user: Employee = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_database)
):
    """List media assets"""
    try:
        media_repo = MediaAssetRepository(db)
        
        if owner_type and owner_id:
            assets = await media_repo.get_assets_by_owner(tenant_id, owner_type, owner_id)
        else:
            # Get all assets for tenant (you'd implement pagination)
            assets = []
        
        # Convert to response format
        response_assets = []
        for asset in assets:
            variants = []
            for variant_name, variant_data in asset.variants.items():
                # Generate URLs for variants
                if asset.acl == ACLType.PUBLIC:
                    url = storage_service.get_public_url(variant_data.storage_key)
                else:
                    url = storage_service.generate_presigned_download_url(
                        variant_data.storage_key
                    )
                
                variants.append(MediaVariantResponse(
                    variant=variant_name,
                    url=url,
                    width=variant_data.width,
                    height=variant_data.height,
                    bytes=variant_data.bytes,
                    format=variant_data.format
                ))
            
            response_assets.append(MediaAssetResponse(
                asset_id=asset.asset_id,
                tenant_id=asset.tenant_id,
                store_id=asset.store_id,
                owner_type=asset.owner_type,
                owner_id=asset.owner_id,
                filename_original=asset.filename_original,
                mime_type=asset.mime_type,
                bytes=asset.bytes,
                width=asset.width,
                height=asset.height,
                hash_sha256=asset.hash_sha256,
                acl=asset.acl,
                variants=variants,
                created_at=asset.created_at,
                updated_at=asset.updated_at,
                tags=asset.tags,
                alt_text=asset.alt_text,
                dominant_color=asset.dominant_color,
                processing_status=asset.processing_status
            ))
        
        return response_assets
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list assets: {str(e)}")


@router.get("/{asset_id}", response_model=MediaAssetResponse)
async def get_asset(
    asset_id: str,
    current_user: Employee = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_database)
):
    """Get media asset by ID"""
    try:
        media_repo = MediaAssetRepository(db)
        
        asset = await media_repo.get_asset_by_id(asset_id, tenant_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Generate variant URLs
        variants = []
        for variant_name, variant_data in asset.variants.items():
            if asset.acl == ACLType.PUBLIC:
                url = storage_service.get_public_url(variant_data.storage_key)
            else:
                url = storage_service.generate_presigned_download_url(
                    variant_data.storage_key
                )
            
            variants.append(MediaVariantResponse(
                variant=variant_name,
                url=url,
                width=variant_data.width,
                height=variant_data.height,
                bytes=variant_data.bytes,
                format=variant_data.format
            ))
        
        return MediaAssetResponse(
            asset_id=asset.asset_id,
            tenant_id=asset.tenant_id,
            store_id=asset.store_id,
            owner_type=asset.owner_type,
            owner_id=asset.owner_id,
            filename_original=asset.filename_original,
            mime_type=asset.mime_type,
            bytes=asset.bytes,
            width=asset.width,
            height=asset.height,
            hash_sha256=asset.hash_sha256,
            acl=asset.acl,
            variants=variants,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            tags=asset.tags,
            alt_text=asset.alt_text,
            dominant_color=asset.dominant_color,
            processing_status=asset.processing_status
        )
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get asset: {str(e)}")


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    current_user: Employee = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_database)
):
    """Delete media asset"""
    try:
        media_repo = MediaAssetRepository(db)
        product_image_repo = ProductImageRepository(db)
        
        # Get asset
        asset = await media_repo.get_asset_by_id(asset_id, tenant_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Remove from product image mappings
        await product_image_repo.remove_image_mapping(asset.owner_id, asset_id)
        
        # Delete from storage
        try:
            # Delete original file
            storage_service.delete_file(asset.storage_key)
            
            # Delete variants
            for variant in asset.variants.values():
                storage_service.delete_file(variant.storage_key)
        except Exception as e:
            # Log error but continue with soft delete
            print(f"Failed to delete files from storage: {str(e)}")
        
        # Soft delete in database
        success = await media_repo.soft_delete_asset(asset_id, tenant_id)
        
        if success:
            return {"success": True, "message": "Asset deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete asset")
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete asset: {str(e)}")


# Product-specific image endpoints

@router.get("/products/{product_id}/images", response_model=List[MediaAssetResponse])
async def get_product_images(
    product_id: str,
    current_user: Employee = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_database)
):
    """Get all images for a product"""
    try:
        product_image_repo = ProductImageRepository(db)
        media_repo = MediaAssetRepository(db)
        
        # Get image mappings
        mappings = await product_image_repo.get_product_images(product_id, include_assets=True)
        
        # Convert to response format
        response_assets = []
        for mapping in mappings:
            if hasattr(mapping, 'asset') and mapping.asset:
                asset = mapping.asset
                
                # Generate variant URLs
                variants = []
                for variant_name, variant_data in asset.variants.items():
                    if asset.acl == ACLType.PUBLIC:
                        url = storage_service.get_public_url(variant_data.storage_key)
                    else:
                        url = storage_service.generate_presigned_download_url(
                            variant_data.storage_key
                        )
                    
                    variants.append(MediaVariantResponse(
                        variant=variant_name,
                        url=url,
                        width=variant_data.width,
                        height=variant_data.height,
                        bytes=variant_data.bytes,
                        format=variant_data.format
                    ))
                
                response_assets.append(MediaAssetResponse(
                    asset_id=asset.asset_id,
                    tenant_id=asset.tenant_id,
                    store_id=asset.store_id,
                    owner_type=asset.owner_type,
                    owner_id=asset.owner_id,
                    filename_original=asset.filename_original,
                    mime_type=asset.mime_type,
                    bytes=asset.bytes,
                    width=asset.width,
                    height=asset.height,
                    hash_sha256=asset.hash_sha256,
                    acl=asset.acl,
                    variants=variants,
                    created_at=asset.created_at,
                    updated_at=asset.updated_at,
                    tags=asset.tags,
                    alt_text=asset.alt_text,
                    dominant_color=asset.dominant_color,
                    processing_status=asset.processing_status
                ))
        
        return response_assets
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get product images: {str(e)}")


@router.post("/products/{product_id}/images/order")
async def reorder_product_images(
    product_id: str,
    request: ProductImageOrderRequest,
    current_user: Employee = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_database)
):
    """Reorder product images"""
    try:
        product_image_repo = ProductImageRepository(db)
        
        success = await product_image_repo.reorder_images(product_id, request.asset_ids)
        
        if success:
            return {"success": True, "message": "Images reordered successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reorder images")
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reorder images: {str(e)}")


@router.post("/products/{product_id}/images/primary")
async def set_primary_product_image(
    product_id: str,
    request: ProductImagePrimaryRequest,
    current_user: Employee = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db = Depends(get_database)
):
    """Set primary image for a product"""
    try:
        product_image_repo = ProductImageRepository(db)
        
        success = await product_image_repo.set_primary_image(product_id, request.asset_id)
        
        if success:
            return {"success": True, "message": "Primary image set successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to set primary image")
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set primary image: {str(e)}")
