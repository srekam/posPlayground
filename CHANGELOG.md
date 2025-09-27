# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.15.11] - 2024-12-27

### Added
- **Items Management System**: Complete CRUD operations for all item types
- **Image Upload Integration**: Drag & drop image upload with progress tracking
- **Item Editor Wizard**: 3-step process (Basics, Type-specific fields, Preview)
- **Type-specific Forms**: Dynamic form fields based on item type (STOCKED_GOOD, PASS_TIME, BUNDLE, etc.)
- **Image Gallery**: Support for up to 5 images per item with primary image selection
- **Bulk Operations**: Activate/deactivate multiple items at once
- **Item Cloning**: Duplicate existing items with new names
- **Access Zones Management**: CRUD operations for access zones with test endpoints

### Changed
- **Settings Page**: Fixed runtime errors with null safety improvements
- **API Response Handling**: Improved error handling and success feedback
- **Form Validation**: Enhanced inline validation with better error messages

### Fixed
- **Settings Component**: Resolved "Cannot read properties of undefined (reading 'features')" error
- **Items CRUD**: Fixed "save ok but not appear in list" issue with in-memory persistence
- **Access Zones**: Fixed all CRUD operations with proper API integration
- **Form State Management**: Improved handling of nested object properties

### Technical
- **Test Endpoints**: Added authentication-bypass endpoints for development
- **Media API Integration**: Connected frontend image upload with backend Media API
- **In-memory Storage**: Implemented temporary storage for testing item persistence
- **Error Handling**: Comprehensive error handling with user-friendly messages

## [1.15.1] - 2024-12-01

### Added
- **Media Storage API**: Complete S3/MinIO-based media storage system
- **Image Processing**: Automatic variant generation (thumb, sm, md, lg) in WebP format
- **Presigned Upload URLs**: Secure direct-to-S3 uploads bypassing API server
- **CDN Integration**: Support for CDN-backed media delivery
- **Background Processing**: Async image processing with Redis queue support
- **Multi-tenant Storage**: Tenant-isolated storage paths for security
- **File Validation**: MIME type validation, size limits, and SHA256 deduplication
- **Product Image Management**: Ordering, primary image setting, and mapping
- **Comprehensive Documentation**: Full API documentation with examples
- **Docker Infrastructure**: MinIO, Redis, and MongoDB setup
- **Test Suite**: Complete API testing framework

### Technical Implementation
- **Models**: `MediaAsset`, `ProductImageMapping` with Beanie ODM
- **Repositories**: Full CRUD operations with soft deletes and processing status
- **Services**: Storage service, image processing, and background tasks
- **API Endpoints**: 8 new endpoints for media management
- **Security**: EXIF stripping, access control, and validation
- **Performance**: WebP variants, caching headers, and deduplication

### Infrastructure
- MinIO S3-compatible storage
- Redis for background processing
- MongoDB for metadata storage
- Docker Compose setup with health checks
- Automated setup script

## [1.15.0] - 2024-11-30

### Added
- FastAPI backend migration from Express.js
- MongoDB integration with Beanie ODM
- Comprehensive POS system APIs
- Authentication and authorization system
- Multi-tenant architecture
- Redis caching and session management

### Changed
- Backend architecture from Node.js to Python FastAPI
- Database from PostgreSQL to MongoDB
- API structure and response formats

## [1.14.x] - Previous versions
- Flutter mobile application
- Express.js backend
- PostgreSQL database
- Basic POS functionality

---

## Version Explanation

### Version 1.15.1 Breakdown:
- **1** = App (Flutter): No changes from previous version
- **15** = API (Backend): Major backbone implementation - Complete media storage system
- **1** = Web UI: No changes from previous version

### Major Features in v1.15.1:
1. **Media Storage Backbone**: Complete implementation of S3-based media storage
2. **Image Processing Pipeline**: Automated variant generation and optimization
3. **Security & Validation**: Comprehensive file validation and security measures
4. **Performance Optimization**: CDN integration and caching strategies
5. **Developer Experience**: Full documentation, testing, and setup automation

This version establishes the media storage foundation for the POS system, enabling product images, category images, and other media assets to be handled efficiently and securely.
