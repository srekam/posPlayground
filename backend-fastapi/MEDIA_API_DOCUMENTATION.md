# Media API Documentation

This document describes the media storage and processing API for the PlayPark POS system. The API provides secure file upload, image processing, and CDN-friendly delivery for product images, category images, and other media assets.

## Architecture Overview

The media system uses a modern architecture with:
- **S3/MinIO** for object storage
- **MongoDB** for metadata storage
- **Background processing** for image variants
- **CDN integration** for fast delivery
- **Presigned URLs** for secure uploads

## Storage Layout

```
bucket: media
└── tenants/<tenant_id>/
    └── products/<product_id>/<asset_id>/
        ├── orig.jpg
        ├── lg.webp
        ├── md.webp
        ├── sm.webp
        └── thumb.webp
```

## API Endpoints

### 1. Generate Presigned Upload URL

**POST** `/api/v1/media/uploads/presign`

Generate a presigned URL for direct file upload to S3/MinIO.

**Request Body:**
```json
{
  "filename": "product-image.jpg",
  "mime_type": "image/jpeg",
  "owner_type": "product",
  "owner_id": "prod_123",
  "acl": "public"
}
```

**Response:**
```json
{
  "upload_url": "https://storage.example.com/bucket/tenants/tenant1/products/prod_123/asset_id/orig.jpg",
  "storage_key": "tenants/tenant1/products/prod_123/asset_id/orig.jpg",
  "headers": {
    "Content-Type": "image/jpeg",
    "x-amz-algorithm": "AWS4-HMAC-SHA256",
    "x-amz-credential": "...",
    "x-amz-date": "20231201T120000Z",
    "x-amz-signature": "..."
  },
  "max_bytes": 10485760,
  "asset_id": "01HZ8K9M2N3P4Q5R6S7T8U9V0W"
}
```

### 2. Complete Upload

**POST** `/api/v1/media/complete`

Finalize the upload process and create media asset record.

**Request Body:**
```json
{
  "asset_id": "01HZ8K9M2N3P4Q5R6S7T8U9V0W",
  "storage_key": "tenants/tenant1/products/prod_123/asset_id/orig.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "asset_id": "01HZ8K9M2N3P4Q5R6S7T8U9V0W",
  "processing_status": "pending"
}
```

### 3. List Media Assets

**GET** `/api/v1/media?owner_type=product&owner_id=prod_123`

List media assets with optional filtering.

**Query Parameters:**
- `owner_type`: Filter by owner type (product, category, etc.)
- `owner_id`: Filter by owner ID
- `limit`: Number of assets to return (default: 50, max: 100)
- `offset`: Number of assets to skip (default: 0)

**Response:**
```json
[
  {
    "asset_id": "01HZ8K9M2N3P4Q5R6S7T8U9V0W",
    "tenant_id": "tenant1",
    "store_id": "store1",
    "owner_type": "product",
    "owner_id": "prod_123",
    "filename_original": "product-image.jpg",
    "mime_type": "image/jpeg",
    "bytes": 2048576,
    "width": 1200,
    "height": 800,
    "hash_sha256": "a1b2c3d4e5f6...",
    "acl": "public",
    "variants": [
      {
        "variant": "thumb",
        "url": "https://cdn.example.com/tenants/tenant1/products/prod_123/asset_id/thumb.webp",
        "width": 150,
        "height": 150,
        "bytes": 15432,
        "format": "webp"
      },
      {
        "variant": "lg",
        "url": "https://cdn.example.com/tenants/tenant1/products/prod_123/asset_id/lg.webp",
        "width": 1200,
        "height": 800,
        "bytes": 89234,
        "format": "webp"
      }
    ],
    "created_at": "2023-12-01T12:00:00Z",
    "updated_at": "2023-12-01T12:01:00Z",
    "tags": ["product", "featured"],
    "alt_text": "Product image showing the main product",
    "dominant_color": "#ff6b6b",
    "processing_status": "completed"
  }
]
```

### 4. Get Media Asset

**GET** `/api/v1/media/{asset_id}`

Get a specific media asset by ID.

**Response:** Same format as list endpoint, single object.

### 5. Delete Media Asset

**DELETE** `/api/v1/media/{asset_id}`

Soft delete a media asset and remove files from storage.

**Response:**
```json
{
  "success": true,
  "message": "Asset deleted successfully"
}
```

### 6. Get Product Images

**GET** `/api/v1/media/products/{product_id}/images`

Get all images for a specific product, ordered by sort_order.

**Response:** Array of media assets (same format as list endpoint).

### 7. Reorder Product Images

**POST** `/api/v1/media/products/{product_id}/images/order`

Reorder images for a product.

**Request Body:**
```json
{
  "asset_ids": [
    "01HZ8K9M2N3P4Q5R6S7T8U9V0W",
    "01HZ8K9M2N3P4Q5R6S7T8U9V0X",
    "01HZ8K9M2N3P4Q5R6S7T8U9V0Y"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Images reordered successfully"
}
```

### 8. Set Primary Product Image

**POST** `/api/v1/media/products/{product_id}/images/primary`

Set the primary image for a product.

**Request Body:**
```json
{
  "asset_id": "01HZ8K9M2N3P4Q5R6S7T8U9V0W"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Primary image set successfully"
}
```

## Client Usage Examples

### JavaScript/TypeScript (Web)

```typescript
// 1. Request presigned URL
const presignResponse = await fetch('/api/v1/media/uploads/presign', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filename: file.name,
    mime_type: file.type,
    owner_type: 'product',
    owner_id: productId
  })
});

const { upload_url, headers, asset_id } = await presignResponse.json();

// 2. Upload file directly to S3
const formData = new FormData();
Object.entries(headers).forEach(([key, value]) => {
  formData.append(key, value);
});
formData.append('file', file);

const uploadResponse = await fetch(upload_url, {
  method: 'POST',
  body: formData
});

if (uploadResponse.ok) {
  // 3. Complete the upload
  await fetch('/api/v1/media/complete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      asset_id,
      storage_key: headers.key
    })
  });
}
```

### Flutter/Dart (Mobile)

```dart
// 1. Request presigned URL
final presignResponse = await http.post(
  Uri.parse('$baseUrl/api/v1/media/uploads/presign'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'filename': file.path.split('/').last,
    'mime_type': 'image/jpeg',
    'owner_type': 'product',
    'owner_id': productId,
  }),
);

final presignData = jsonDecode(presignResponse.body);

// 2. Upload file to S3
final uploadRequest = http.MultipartRequest(
  'POST',
  Uri.parse(presignData['upload_url']),
);

// Add form fields
presignData['headers'].forEach((key, value) {
  uploadRequest.fields[key] = value;
});

// Add file
uploadRequest.files.add(
  await http.MultipartFile.fromPath('file', file.path),
);

final uploadResponse = await uploadRequest.send();

if (uploadResponse.statusCode == 200) {
  // 3. Complete upload
  await http.post(
    Uri.parse('$baseUrl/api/v1/media/complete'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'asset_id': presignData['asset_id'],
      'storage_key': presignData['storage_key'],
    }),
  );
}
```

## Image Variants

The system automatically generates multiple image variants:

| Variant | Size | Use Case |
|---------|------|----------|
| `thumb` | 150x150 | Grid listings, thumbnails |
| `sm` | 300x300 | Small cards, previews |
| `md` | 600x600 | Product pages, medium displays |
| `lg` | 1200x1200 | Large displays, high-res |
| `orig` | Original | Full resolution, downloads |

All variants are generated in WebP format for optimal compression and performance.

## Configuration

### Environment Variables

```bash
# S3/MinIO Configuration
S3_ENDPOINT=http://localhost:9000
S3_REGION=us-east-1
S3_BUCKET=media
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_USE_SSL=false
S3_SIGNED_URL_TTL=3600
S3_MAX_FILE_SIZE=10485760

# Media Processing
MEDIA_CDN_BASE_URL=https://cdn.example.com
MEDIA_PROCESSING_ENABLED=true
MEDIA_VARIANT_SIZES=thumb:150x150,sm:300x300,md:600x600,lg:1200x1200
MEDIA_STRIP_EXIF=true
MEDIA_COMPRESS_QUALITY=85
MEDIA_DOMINANT_COLOR=true

# Allowed MIME Types
S3_ALLOWED_MIME_TYPES=image/jpeg,image/png,image/webp,image/avif,image/gif
```

### MinIO Setup (Development)

```yaml
# docker-compose.yml
version: '3.8'
services:
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

volumes:
  minio_data:
```

## Security Features

1. **MIME Type Validation**: Server-side validation of file types using magic bytes
2. **File Size Limits**: Configurable maximum file sizes
3. **SHA256 Deduplication**: Automatic detection of duplicate files
4. **Tenant Isolation**: All storage paths include tenant ID
5. **Access Control**: Support for public and signed URL access
6. **EXIF Stripping**: Automatic removal of metadata for privacy

## Performance Optimizations

1. **CDN Integration**: Optional CDN base URL for fast global delivery
2. **WebP Variants**: Automatic generation of optimized image formats
3. **Lazy Processing**: Background generation of image variants
4. **Caching Headers**: Proper cache headers for long-term caching
5. **Deduplication**: Automatic reuse of identical files

## Error Handling

The API returns structured error responses:

```json
{
  "error": {
    "code": "E_VALIDATION_ERROR",
    "message": "File size exceeds maximum allowed size",
    "details": {
      "max_size": 10485760,
      "actual_size": 15728640
    }
  }
}
```

Common error codes:
- `E_VALIDATION_ERROR`: Input validation failed
- `E_STORAGE_ERROR`: Storage operation failed
- `E_PROCESSING_ERROR`: Image processing failed
- `E_NOT_FOUND`: Asset not found
- `E_MIME_TYPE_NOT_ALLOWED`: File type not permitted

## Monitoring and Maintenance

### Background Tasks

The system includes background tasks for:
- Image variant generation
- Failed asset cleanup
- Processing queue management

### Health Checks

Monitor the following endpoints:
- `/healthz` - Basic health check
- `/readyz` - Readiness check (includes storage connectivity)

### Metrics

Key metrics to monitor:
- Upload success rate
- Processing queue length
- Storage usage
- CDN cache hit rate
- Error rates by endpoint

## Migration from Existing System

If migrating from an existing media system:

1. **Export existing media metadata** to the new format
2. **Upload files to S3/MinIO** with proper storage keys
3. **Update database records** with new asset IDs and storage keys
4. **Generate variants** for existing images using the processing service
5. **Update client applications** to use new API endpoints

## Troubleshooting

### Common Issues

1. **Upload fails**: Check S3 credentials and bucket permissions
2. **Variants not generating**: Verify image processing dependencies
3. **Slow performance**: Check CDN configuration and caching
4. **Memory issues**: Monitor image processing memory usage

### Debug Mode

Enable debug logging:
```bash
LOG_LEVEL=DEBUG
```

### Storage Verification

Check if files exist in storage:
```bash
# List objects in bucket
aws s3 ls s3://media/tenants/tenant1/products/prod_123/ --recursive
```

This media API provides a robust, scalable solution for handling product images and other media assets in your POS system, with modern best practices for security, performance, and maintainability.
