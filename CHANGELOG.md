# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.15.12] - 2024-12-27

### Added
- Multi-language support (English/Thai) for admin interface
- i18next integration with React
- Language switcher component in Layout
- Browser language detection with localStorage persistence
- Complete Items module translations (EN/TH)
- Complete Settings module translations (EN/TH)
- Translation files for all UI components:
  - `locales/en/items.json`
  - `locales/th/items.json`
  - `locales/en/settings.json`
  - `locales/th/settings.json`

### Changed
- All hardcoded strings replaced with translation keys
- Enhanced accessibility with localized aria-label attributes
- Enum values now use dynamic translation mapping
- Language switching without page reload

### Fixed
- Settings page runtime error ("Cannot read properties of undefined")
- Improved null safety across Settings component
- Better error handling and user feedback

## [1.15.11] - 2024-12-26

### Added
- Items Management System with complete CRUD operations
- Image upload functionality with drag & drop interface
- Item Editor wizard with 3-step process
- Support for all item types (STOCKED_GOOD, PASS_TIME, BUNDLE, etc.)
- Bulk operations for item management
- Item cloning functionality
- Integration with Media API backend
- Test endpoints for development workflow

### Changed
- Enhanced UX with success/error feedback
- Improved form validation and error messages
- Optimistic updates for better responsiveness

### Fixed
- API response handling improvements
- Better error handling throughout the application

## [1.15.1] - 2024-12-25

### Added
- Complete media storage backbone implementation
- S3/MinIO-based object storage integration
- Presigned URL upload system
- Automatic image variant generation (thumbnail, small, medium, large)
- WebP format conversion for optimal performance
- CDN integration for fast global delivery
- Security & validation with MIME type checking
- Background processing with Redis queue
- 8 new API endpoints for media management

### Changed
- Migrated to FastAPI backend architecture
- Enhanced security with tenant isolation
- Improved performance with WebP variants

### Fixed
- File upload security vulnerabilities
- Image processing performance issues

## [1.15.0] - 2024-12-24

### Added
- FastAPI backend migration
- MongoDB integration
- Modern API architecture
- Comprehensive API documentation

### Changed
- Backend framework from Express.js to FastAPI
- Database integration improvements

### Removed
- Legacy Express.js backend components

## [1.14.x] - Previous Versions

### Added
- Flutter mobile application
- Basic web interface
- Express.js backend foundation

---

*For more detailed version information, see [VERSION.md](VERSION.md)*