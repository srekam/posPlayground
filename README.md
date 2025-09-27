# PlayPark POS System

**Version 1.15.1 - Media Foundation** 🎉

A comprehensive Point of Sale (POS) system for indoor playgrounds and entertainment venues, built with Flutter and FastAPI.

## 🆕 What's New in v1.15.1

### 🎯 Version Breakdown
- **App (1)**: Flutter mobile application - No changes
- **API (15)**: FastAPI backend - **Major media storage backbone implementation**
- **Web UI (1)**: Web interface - No changes

### 🚀 Media Storage Backbone
This release introduces a comprehensive media storage system featuring:
- **S3/MinIO Integration**: Direct client-to-storage uploads with presigned URLs
- **Image Processing**: Automatic variant generation (thumb, sm, md, lg) in WebP format
- **Background Processing**: Redis-powered async image processing
- **Security**: MIME validation, file size limits, EXIF stripping, and deduplication
- **CDN Support**: Fast global delivery with proper caching headers
- **8 New API Endpoints**: Complete media management capabilities

👉 **[Read Full Release Notes](RELEASE_NOTES_v1.15.1.md)**  
👉 **[Complete API Reference Guide](API_REFERENCE_GUIDE.md)**  
👉 **[Developer Onboarding Guide](DEVELOPER_ONBOARDING.md)** *(Start Here!)*  
👉 **[API Quick Reference](API_QUICK_REFERENCE.md)** *(Developer Cheat Sheet)*  
👉 **[Media API Documentation](backend-fastapi/MEDIA_API_DOCUMENTATION.md)**  
👉 **[POS API Documentation](backend-fastapi/POS_API_DOCUMENTATION.md)**

## 🚀 Quick Start

### Flutter App (Client)
```bash
# Install dependencies
flutter pub get

# Run on Chrome (recommended for development)
flutter run -d chrome --debug

# Run on Android
flutter run -d android --debug
```

### Backend Server (FastAPI)
```bash
# Navigate to backend-fastapi directory
cd backend-fastapi

# Setup media infrastructure (MinIO, Redis, MongoDB)
./setup_media.sh

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn app.main:app --reload --port 48080

# Or start with Docker
docker-compose -f docker-compose.media.yml up -d
```

### Legacy Backend (Node.js)
```bash
# Navigate to backend directory (legacy)
cd backend

# Start with Docker (recommended)
docker-compose up -d

# Or start manually
npm install
npm run seed  # Seed database
npm run dev   # Start development server
```

## 📚 Complete Documentation

**👉 [Read the complete project documentation](PROJECT_DOCUMENTATION.md)**

The comprehensive documentation includes:
- **Architecture Overview** - System design and components
- **Flutter App Guide** - Client application features and setup
- **Backend API** - Server implementation and endpoints
- **RBAC System** - Role-based access control
- **Adaptive Integration** - Offline/online capabilities
- **Development Guide** - Setup and development workflow
- **Deployment** - Production deployment instructions
- **Troubleshooting** - Common issues and solutions

## 🎯 Key Features

- **Multi-platform POS** - Flutter app for Android, iOS, and Web
- **Offline-First** - SQLite database with sync capabilities
- **Multi-tenant** - Support for multiple tenants and stores
- **RBAC Security** - Role-based access control with permissions
- **Real-time Sync** - Adaptive connectivity with backend
- **QR Code System** - Ticket generation and redemption
- **Admin Dashboard** - Web-based administration panel

## 🔧 Demo Credentials

### FastAPI Backend (v1.15.1)
- **Backend URL**: `http://localhost:48080/api/v1`
- **API Docs**: `http://localhost:48080/docs`
- **Media API**: `http://localhost:48080/api/v1/media`
- **MinIO Console**: `http://localhost:9001` (admin/minioadmin)

### Legacy Backend (Node.js)
- **Backend URL**: `http://localhost:48080/v1`
- **Site Key**: `tenant_demo_01:store_demo_01:demo-secret-key`
- **Manager Email**: `manager@playpark.demo`
- **Manager PIN**: `1234`

## 📞 Support

For detailed information, troubleshooting, and development guides, please refer to the [complete project documentation](PROJECT_DOCUMENTATION.md).