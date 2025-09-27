"""
Storage Service for S3/MinIO operations
"""
import hashlib
import mimetypes
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, BinaryIO
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from PIL import Image
import magic

from ..config import settings
from ..utils.errors import ValidationError, StorageError


class StorageService:
    """Service for S3/MinIO storage operations"""
    
    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.S3_BUCKET
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize S3 client"""
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                use_ssl=settings.S3_USE_SSL,
                verify=False if not settings.S3_USE_SSL else True
            )
            
            # Ensure bucket exists
            self._ensure_bucket_exists()
            
        except NoCredentialsError:
            raise StorageError("S3 credentials not found")
        except Exception as e:
            raise StorageError(f"Failed to initialize S3 client: {str(e)}")
    
    def _ensure_bucket_exists(self):
        """Ensure the storage bucket exists"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    if settings.S3_REGION == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': settings.S3_REGION}
                        )
                except ClientError as create_error:
                    raise StorageError(f"Failed to create bucket: {str(create_error)}")
            else:
                raise StorageError(f"Bucket access error: {str(e)}")
    
    def generate_storage_key(
        self, 
        tenant_id: str, 
        owner_type: str, 
        owner_id: str, 
        asset_id: str, 
        filename: str
    ) -> str:
        """Generate storage key for a file"""
        # Extract file extension
        file_ext = mimetypes.guess_extension(mimetypes.guess_type(filename)[0]) or '.bin'
        
        # Generate storage path: tenants/<tid>/<owner_type>/<owner_id>/<asset_id>/orig.ext
        storage_key = f"tenants/{tenant_id}/{owner_type}s/{owner_id}/{asset_id}/orig{file_ext}"
        return storage_key
    
    def generate_variant_storage_key(
        self, 
        base_storage_key: str, 
        variant: str, 
        format: str = "webp"
    ) -> str:
        """Generate storage key for a variant"""
        # Replace 'orig.ext' with 'variant.format'
        parts = base_storage_key.rsplit('/', 1)
        if len(parts) == 2:
            return f"{parts[0]}/{variant}.{format}"
        return f"{base_storage_key.rsplit('.', 1)[0]}/{variant}.{format}"
    
    def generate_presigned_upload_url(
        self, 
        storage_key: str, 
        mime_type: str, 
        max_size: int = None
    ) -> Tuple[str, Dict[str, str]]:
        """Generate presigned URL for file upload"""
        try:
            max_size = max_size or settings.S3_MAX_FILE_SIZE
            
            # Generate presigned POST data
            conditions = [
                {"bucket": self.bucket_name},
                ["content-length-range", 1, max_size],
                {"Content-Type": mime_type},
                {"key": storage_key}
            ]
            
            fields = {
                "Content-Type": mime_type
            }
            
            presigned_post = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=storage_key,
                Fields=fields,
                Conditions=conditions,
                ExpiresIn=3600  # 1 hour
            )
            
            return presigned_post['url'], presigned_post['fields']
            
        except ClientError as e:
            raise StorageError(f"Failed to generate presigned URL: {str(e)}")
    
    def generate_presigned_download_url(
        self, 
        storage_key: str, 
        expires_in: int = None
    ) -> str:
        """Generate presigned URL for file download"""
        try:
            expires_in = expires_in or settings.S3_SIGNED_URL_TTL
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': storage_key},
                ExpiresIn=expires_in
            )
            
            return url
            
        except ClientError as e:
            raise StorageError(f"Failed to generate download URL: {str(e)}")
    
    def get_public_url(self, storage_key: str) -> str:
        """Get public URL for a file"""
        base_url = settings.media_base_url
        if settings.MEDIA_CDN_BASE_URL:
            return f"{base_url}/{storage_key}"
        else:
            return f"{base_url}/{self.bucket_name}/{storage_key}"
    
    def upload_file(
        self, 
        file_obj: BinaryIO, 
        storage_key: str, 
        mime_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Upload file to storage"""
        try:
            extra_args = {
                'ContentType': mime_type,
                'CacheControl': 'public, max-age=31536000, immutable'
            }
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                storage_key,
                ExtraArgs=extra_args
            )
            
            return True
            
        except ClientError as e:
            raise StorageError(f"Failed to upload file: {str(e)}")
    
    def delete_file(self, storage_key: str) -> bool:
        """Delete file from storage"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=storage_key)
            return True
        except ClientError as e:
            raise StorageError(f"Failed to delete file: {str(e)}")
    
    def file_exists(self, storage_key: str) -> bool:
        """Check if file exists in storage"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=storage_key)
            return True
        except ClientError:
            return False
    
    def get_file_info(self, storage_key: str) -> Optional[Dict]:
        """Get file metadata from storage"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=storage_key)
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response['ContentType'],
                'etag': response['ETag'].strip('"'),
                'metadata': response.get('Metadata', {})
            }
        except ClientError:
            return None
    
    def validate_file(self, file_obj: BinaryIO, filename: str, mime_type: str) -> Tuple[bool, str]:
        """Validate uploaded file"""
        # Check file size
        file_obj.seek(0, 2)  # Seek to end
        file_size = file_obj.tell()
        file_obj.seek(0)  # Reset to beginning
        
        if file_size > settings.S3_MAX_FILE_SIZE:
            return False, f"File size {file_size} exceeds maximum {settings.S3_MAX_FILE_SIZE}"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Check MIME type
        allowed_types = settings.allowed_mime_types_list
        if mime_type not in allowed_types:
            return False, f"MIME type {mime_type} not allowed. Allowed: {allowed_types}"
        
        # Validate actual file type using magic bytes
        try:
            # Read first 1024 bytes for magic detection
            file_obj.seek(0)
            magic_bytes = file_obj.read(1024)
            file_obj.seek(0)
            
            detected_mime = magic.from_buffer(magic_bytes, mime=True)
            if detected_mime != mime_type:
                return False, f"File content doesn't match declared MIME type. Expected: {mime_type}, Detected: {detected_mime}"
                
        except Exception as e:
            return False, f"Failed to validate file content: {str(e)}"
        
        return True, "File is valid"
    
    def calculate_file_hash(self, file_obj: BinaryIO) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        file_obj.seek(0)
        
        # Read file in chunks to handle large files
        for chunk in iter(lambda: file_obj.read(4096), b""):
            sha256_hash.update(chunk)
        
        file_obj.seek(0)  # Reset to beginning
        return sha256_hash.hexdigest()
    
    def get_image_dimensions(self, file_obj: BinaryIO) -> Tuple[Optional[int], Optional[int]]:
        """Get image dimensions"""
        try:
            file_obj.seek(0)
            with Image.open(file_obj) as img:
                width, height = img.size
                file_obj.seek(0)  # Reset to beginning
                return width, height
        except Exception:
            file_obj.seek(0)  # Reset to beginning
            return None, None
    
    def extract_dominant_color(self, file_obj: BinaryIO) -> Optional[str]:
        """Extract dominant color from image"""
        if not settings.MEDIA_DOMINANT_COLOR:
            return None
            
        try:
            file_obj.seek(0)
            with Image.open(file_obj) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to small size for faster processing
                img = img.resize((150, 150))
                
                # Get color histogram
                colors = img.getcolors(maxcolors=256*256*256)
                if colors:
                    # Get the most frequent color
                    most_frequent = max(colors, key=lambda x: x[0])
                    r, g, b = most_frequent[1]
                    return f"#{r:02x}{g:02x}{b:02x}"
                
                file_obj.seek(0)  # Reset to beginning
                return None
        except Exception:
            file_obj.seek(0)  # Reset to beginning
            return None


# Global storage service instance
storage_service = StorageService()
