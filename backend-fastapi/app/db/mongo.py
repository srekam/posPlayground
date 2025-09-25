"""
MongoDB Database Configuration and Connection Management
"""
from typing import Optional
import structlog
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError

from app.config import settings

logger = structlog.get_logger(__name__)

# Global database instance
_database: Optional[AsyncIOMotorDatabase] = None
_client: Optional[AsyncIOMotorClient] = None


async def get_database() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance"""
    global _database
    
    if _database is None:
        await connect_to_mongo()
    
    return _database


async def connect_to_mongo() -> None:
    """Create database connection"""
    global _client, _database
    
    try:
        logger.info("Connecting to MongoDB", uri=settings.MONGODB_URI)
        
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
            serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
            socketTimeoutMS=settings.MONGODB_SOCKET_TIMEOUT_MS,
            connectTimeoutMS=settings.MONGODB_CONNECT_TIMEOUT_MS,
            retryWrites=True,
        )
        
        # Test connection
        await _client.admin.command("ping")
        
        # Get database name from URI
        db_name = settings.MONGODB_URI.split("/")[-1].split("?")[0]
        _database = _client[db_name]
        
        logger.info("Successfully connected to MongoDB", database=db_name)
        
        # Ensure indexes
        await ensure_indexes()
        
    except ServerSelectionTimeoutError as e:
        logger.error("Failed to connect to MongoDB", error=str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error connecting to MongoDB", error=str(e))
        raise


async def close_database() -> None:
    """Close database connection"""
    global _client, _database
    
    if _client:
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed")


async def ensure_indexes() -> None:
    """Ensure database indexes are created"""
    if not _database:
        return
    
    logger.info("Ensuring database indexes")
    
    try:
        # Users collection indexes
        await _database.users.create_index("email", unique=True)
        await _database.users.create_index("employee_id", unique=True)
        await _database.users.create_index([("tenant_id", 1), ("store_id", 1)])
        
        # Devices collection indexes
        await _database.devices.create_index("device_id", unique=True)
        await _database.devices.create_index([("tenant_id", 1), ("store_id", 1)])
        
        # Sales collection indexes
        await _database.sales.create_index("sale_id", unique=True)
        await _database.sales.create_index("reference", unique=True)
        await _database.sales.create_index([("tenant_id", 1), ("store_id", 1), ("timestamp", -1)])
        await _database.sales.create_index([("shift_id", 1), ("timestamp", -1)])
        
        # Tickets collection indexes
        await _database.tickets.create_index("ticket_id", unique=True)
        await _database.tickets.create_index("qr_token", unique=True)
        await _database.tickets.create_index([("tenant_id", 1), ("store_id", 1)])
        await _database.tickets.create_index([("sale_id", 1), ("status", 1)])
        
        # Shifts collection indexes
        await _database.shifts.create_index("shift_id", unique=True)
        await _database.shifts.create_index([("tenant_id", 1), ("store_id", 1), ("status", 1)])
        
        # Packages collection indexes
        await _database.packages.create_index("package_id", unique=True)
        await _database.packages.create_index([("tenant_id", 1), ("store_id", 1), ("active", 1)])
        
        # Audit logs collection indexes
        await _database.audit_logs.create_index([("tenant_id", 1), ("timestamp", -1)])
        await _database.audit_logs.create_index([("event_type", 1), ("timestamp", -1)])
        await _database.audit_logs.create_index("actor_id")
        
        # Provider reporting indexes (Phase 6)
        await _database.report_templates.create_index("template_id", unique=True)
        await _database.report_templates.create_index([("category", 1), ("type", 1)])
        
        await _database.report_instances.create_index("instance_id", unique=True)
        await _database.report_instances.create_index([("template_id", 1), ("created_at", -1)])
        
        await _database.dashboard_widgets.create_index("widget_id", unique=True)
        await _database.dashboard_widgets.create_index([("category", 1), ("type", 1)])
        
        await _database.export_files.create_index("file_id", unique=True)
        await _database.export_files.create_index([("expires_at", 1)], expireAfterSeconds=0)
        
        logger.info("Database indexes ensured successfully")
        
    except Exception as e:
        logger.error("Error ensuring database indexes", error=str(e))
        raise


def get_collection(collection_name: str):
    """Get a specific collection from the database"""
    if not _database:
        raise RuntimeError("Database not initialized. Call get_database() first.")
    
    return _database[collection_name]
