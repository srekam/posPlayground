"""
Image Processing Service for generating variants
"""
import io
from typing import Dict, Optional, Tuple, BinaryIO
from PIL import Image, ImageOps
import asyncio

from ..config import settings
from ..models.media_assets import ImageVariant
from ..services.storage_service import storage_service
from ..utils.errors import ProcessingError


class ImageProcessingService:
    """Service for image processing and variant generation"""
    
    def __init__(self):
        self.variant_sizes = settings.media_variant_sizes_dict
    
    async def generate_variants(
        self, 
        asset_id: str, 
        storage_key: str, 
        tenant_id: str
    ) -> Dict[str, ImageVariant]:
        """Generate image variants for an asset"""
        try:
            # Download original image from storage
            original_data = await self._download_image(storage_key)
            if not original_data:
                raise ProcessingError("Failed to download original image")
            
            variants = {}
            
            # Process each variant size
            for variant_name, size_config in self.variant_sizes.items():
                variant = await self._create_variant(
                    original_data,
                    variant_name,
                    size_config['width'],
                    size_config['height'],
                    asset_id,
                    storage_key,
                    tenant_id
                )
                
                if variant:
                    variants[variant_name] = variant
            
            return variants
            
        except Exception as e:
            raise ProcessingError(f"Failed to generate variants: {str(e)}")
    
    async def _download_image(self, storage_key: str) -> Optional[bytes]:
        """Download image from storage"""
        try:
            response = storage_service.s3_client.get_object(
                Bucket=storage_service.bucket_name,
                Key=storage_key
            )
            return response['Body'].read()
        except Exception:
            return None
    
    async def _create_variant(
        self,
        original_data: bytes,
        variant_name: str,
        target_width: int,
        target_height: int,
        asset_id: str,
        base_storage_key: str,
        tenant_id: str
    ) -> Optional[ImageVariant]:
        """Create a single image variant"""
        try:
            # Load original image
            with Image.open(io.BytesIO(original_data)) as img:
                # Convert to RGB if necessary (for JPEG output)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calculate resize dimensions maintaining aspect ratio
                img_width, img_height = img.size
                
                # Calculate scaling factor
                scale_w = target_width / img_width
                scale_h = target_height / img_height
                scale = min(scale_w, scale_h)
                
                # Only resize if image is larger than target
                if scale < 1.0:
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # For thumbnails, crop to exact size if needed
                if variant_name == 'thumb' and (img.width != target_width or img.height != target_height):
                    img = ImageOps.fit(img, (target_width, target_height), Image.Resampling.LANCZOS)
                
                # Strip EXIF if configured
                if settings.MEDIA_STRIP_EXIF:
                    img = self._strip_exif(img)
                
                # Save as WebP with compression
                output_buffer = io.BytesIO()
                img.save(
                    output_buffer,
                    format='WEBP',
                    quality=settings.MEDIA_COMPRESS_QUALITY,
                    optimize=True
                )
                
                # Upload variant to storage
                variant_data = output_buffer.getvalue()
                variant_storage_key = storage_service.generate_variant_storage_key(
                    base_storage_key,
                    variant_name,
                    'webp'
                )
                
                # Upload the variant
                variant_buffer = io.BytesIO(variant_data)
                success = storage_service.upload_file(
                    variant_buffer,
                    variant_storage_key,
                    'image/webp',
                    metadata={
                        'variant': variant_name,
                        'asset_id': asset_id,
                        'tenant_id': tenant_id
                    }
                )
                
                if success:
                    return ImageVariant(
                        storage_key=variant_storage_key,
                        width=img.width,
                        height=img.height,
                        bytes=len(variant_data),
                        format='webp'
                    )
                
                return None
                
        except Exception as e:
            raise ProcessingError(f"Failed to create variant {variant_name}: {str(e)}")
    
    def _strip_exif(self, img: Image.Image) -> Image.Image:
        """Strip EXIF data from image"""
        try:
            # Create new image without EXIF
            data = list(img.getdata())
            new_img = Image.new(img.mode, img.size)
            new_img.putdata(data)
            return new_img
        except Exception:
            return img
    
    async def create_thumbnail(
        self,
        image_data: bytes,
        size: Tuple[int, int] = (150, 150),
        format: str = 'webp'
    ) -> Optional[bytes]:
        """Create a thumbnail from image data"""
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                # Convert to RGB
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Save to buffer
                output_buffer = io.BytesIO()
                img.save(output_buffer, format=format.upper(), quality=85)
                
                return output_buffer.getvalue()
                
        except Exception:
            return None
    
    async def get_image_info(self, image_data: bytes) -> Dict:
        """Get image information"""
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size': len(image_data)
                }
        except Exception:
            return {}


# Global image processing service instance
image_processing_service = ImageProcessingService()
