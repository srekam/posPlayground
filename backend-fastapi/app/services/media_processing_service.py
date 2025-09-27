"""
Media Processing Service for background tasks
"""
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta

from ..models.media_assets import MediaAsset, ImageVariant
from ..repositories.media_assets import MediaAssetRepository
from ..services.image_processing_service import image_processing_service
from ..services.storage_service import storage_service
from ..utils.errors import ProcessingError


class MediaProcessingService:
    """Service for processing media assets in the background"""
    
    def __init__(self, media_repo: MediaAssetRepository):
        self.media_repo = media_repo
    
    async def process_asset(self, asset_id: str, tenant_id: str) -> bool:
        """Process a media asset to generate variants"""
        try:
            # Get the asset
            asset = await self.media_repo.get_asset_by_id(asset_id, tenant_id)
            if not asset:
                raise ProcessingError(f"Asset {asset_id} not found")
            
            # Update status to processing
            await self.media_repo.update_processing_status(asset_id, "processing")
            
            # Check if file exists in storage
            if not storage_service.file_exists(asset.storage_key):
                await self.media_repo.update_processing_status(
                    asset_id, 
                    "failed", 
                    "Original file not found in storage"
                )
                return False
            
            # Generate variants
            variants = await image_processing_service.generate_variants(
                asset_id,
                asset.storage_key,
                tenant_id
            )
            
            # Update asset with variants
            asset.variants = variants
            asset.processing_status = "completed"
            asset.updated_at = datetime.utcnow()
            
            await self.media_repo.update_asset(asset)
            
            return True
            
        except Exception as e:
            # Update status to failed
            await self.media_repo.update_processing_status(
                asset_id, 
                "failed", 
                str(e)
            )
            raise ProcessingError(f"Failed to process asset {asset_id}: {str(e)}")
    
    async def process_pending_assets(self, tenant_id: str, limit: int = 10) -> int:
        """Process pending assets"""
        try:
            pending_assets = await self.media_repo.get_assets_by_status(
                tenant_id, 
                "pending", 
                limit
            )
            
            processed_count = 0
            for asset in pending_assets:
                try:
                    success = await self.process_asset(asset.asset_id, tenant_id)
                    if success:
                        processed_count += 1
                except Exception as e:
                    # Log error but continue processing other assets
                    print(f"Failed to process asset {asset.asset_id}: {str(e)}")
                    continue
            
            return processed_count
            
        except Exception as e:
            raise ProcessingError(f"Failed to process pending assets: {str(e)}")
    
    async def cleanup_failed_assets(self, tenant_id: str, older_than_hours: int = 24) -> int:
        """Clean up failed assets older than specified hours"""
        try:
            # This would require additional query methods in the repository
            # For now, we'll implement a basic version
            failed_assets = await self.media_repo.get_assets_by_status(
                tenant_id, 
                "failed", 
                100  # Limit for cleanup
            )
            
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            cleaned_count = 0
            
            for asset in failed_assets:
                if asset.updated_at < cutoff_time:
                    # Delete from storage
                    try:
                        storage_service.delete_file(asset.storage_key)
                        # Delete variants
                        for variant in asset.variants.values():
                            storage_service.delete_file(variant.storage_key)
                    except Exception:
                        pass  # Continue even if storage cleanup fails
                    
                    # Soft delete the asset
                    await self.media_repo.soft_delete_asset(asset.asset_id, tenant_id)
                    cleaned_count += 1
            
            return cleaned_count
            
        except Exception as e:
            raise ProcessingError(f"Failed to cleanup failed assets: {str(e)}")
    
    async def reprocess_asset(self, asset_id: str, tenant_id: str) -> bool:
        """Reprocess an asset (regenerate variants)"""
        try:
            asset = await self.media_repo.get_asset_by_id(asset_id, tenant_id)
            if not asset:
                raise ProcessingError(f"Asset {asset_id} not found")
            
            # Delete existing variants from storage
            for variant in asset.variants.values():
                try:
                    storage_service.delete_file(variant.storage_key)
                except Exception:
                    pass  # Continue even if some deletions fail
            
            # Clear variants and reprocess
            asset.variants = {}
            await self.media_repo.update_asset(asset)
            
            # Process the asset
            return await self.process_asset(asset_id, tenant_id)
            
        except Exception as e:
            raise ProcessingError(f"Failed to reprocess asset {asset_id}: {str(e)}")


# Background task functions for Celery/Redis
async def process_media_asset_task(asset_id: str, tenant_id: str):
    """Background task to process a media asset"""
    from ..db.mongo import get_database
    from ..repositories.media_assets import MediaAssetRepository
    
    db = await get_database()
    media_repo = MediaAssetRepository(db)
    processing_service = MediaProcessingService(media_repo)
    
    try:
        success = await processing_service.process_asset(asset_id, tenant_id)
        return {"success": success, "asset_id": asset_id}
    except Exception as e:
        return {"success": False, "error": str(e), "asset_id": asset_id}


async def cleanup_failed_assets_task(tenant_id: str, older_than_hours: int = 24):
    """Background task to cleanup failed assets"""
    from ..db.mongo import get_database
    from ..repositories.media_assets import MediaAssetRepository
    
    db = await get_database()
    media_repo = MediaAssetRepository(db)
    processing_service = MediaProcessingService(media_repo)
    
    try:
        cleaned_count = await processing_service.cleanup_failed_assets(tenant_id, older_than_hours)
        return {"success": True, "cleaned_count": cleaned_count}
    except Exception as e:
        return {"success": False, "error": str(e)}
