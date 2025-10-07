"""
Enrollment Repository
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from app.models.core import EnrollToken
from app.repositories.base import BaseRepository
from app.utils.logging import LoggerMixin

logger = structlog.get_logger(__name__)


class EnrollmentRepository(BaseRepository):
    """Enrollment repository for managing enrollment tokens"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__("enroll_tokens", EnrollToken)
    
    async def create_enroll_token(self, token: EnrollToken) -> EnrollToken:
        """Create a new enrollment token"""
        token_dict = token.dict(by_alias=True, exclude={"id"}, exclude_none=False)
        logger.info("Saving enrollment token to database", 
                   token_dict=token_dict,
                   manual_key=token_dict.get("manual_key"))
        result = await self.collection.insert_one(token_dict)
        
        if result.inserted_id:
            token.id = result.inserted_id
            logger.info("Created enrollment token", 
                       token=token.token[:8] + "...",
                       store_id=token.store_id,
                       device_type=token.device_type)
            return token
        else:
            raise Exception("Failed to create enrollment token")
    
    async def get_enroll_token(self, token: str) -> Optional[EnrollToken]:
        """Get enrollment token by token string"""
        token_doc = await self.collection.find_one({"token": token})
        if token_doc:
            return EnrollToken(**token_doc)
        return None
    
    async def get_enroll_token_by_manual_key(self, manual_key: str) -> Optional[EnrollToken]:
        """Get enrollment token by 5-digit manual key"""
        logger.info("get_enroll_token_by_manual_key called", manual_key=manual_key)
        
        # For 5-digit codes, directly search by manual_key field
        if not manual_key.isdigit() or len(manual_key) != 5:
            logger.warning("Invalid manual key format - must be 5 digits", manual_key=manual_key)
            return None
        
        # Find enrollment token by manual_key field
        query = {
            "manual_key": manual_key,
            "status": {"$in": ["active", "pending", "unused"]},
            "expires_at": {"$gt": datetime.utcnow()}
        }
        
        logger.info("Database query details", 
                   query=query,
                   manual_key_type=type(manual_key).__name__,
                   manual_key_length=len(manual_key))
        
        # Also check what's actually in the database - get recent tokens with manual_key
        all_tokens = await self.collection.find(
            {"manual_key": {"$exists": True}}, 
            {"manual_key": 1, "status": 1, "expires_at": 1, "created_at": 1}
        ).sort("created_at", -1).limit(5).to_list(5)
        logger.info("Recent tokens with manual_key in database", tokens=all_tokens)
        
        token_doc = await self.collection.find_one(query)
        
        # Also try a direct lookup by manual_key only to debug
        direct_lookup = await self.collection.find_one({"manual_key": manual_key})
        logger.info("Direct manual_key lookup", 
                   manual_key=manual_key,
                   found=direct_lookup is not None,
                   token_data=direct_lookup)
        
        logger.info("Database query result", 
                   manual_key=manual_key,
                   found=token_doc is not None,
                   current_time=datetime.utcnow())
        
        if token_doc:
            logger.info("Found enrollment token by manual key",
                       manual_key=manual_key,
                       token=token_doc.get("token", "")[:8] + "...",
                       status=token_doc.get("status"),
                       expires_at=token_doc.get("expires_at"))
            return EnrollToken(**token_doc)
        
        logger.warning("No enrollment token found for manual key", manual_key=manual_key)
        return None

    async def get_most_recent_unused_token(self, within_seconds: int = 60) -> Optional[EnrollToken]:
        """Fallback: get the most recent unused token created within the last N seconds.
        This helps pair devices when the UI/app code drifts but timing is correct.
        """
        cutoff = datetime.utcnow() - timedelta(seconds=within_seconds)
        logger.info("Fallback lookup: most recent unused token", cutoff=cutoff)
        doc = await self.collection.find_one(
            {
                "status": {"$in": ["unused", "pending", "active"]},
                "created_at": {"$gte": cutoff},
                "expires_at": {"$gt": datetime.utcnow()},
            },
            sort=[("created_at", -1)],
        )
        if doc:
            logger.info(
                "Fallback token selected",
                token=doc.get("token", "")[:8] + "...",
                created_at=doc.get("created_at"),
                expires_at=doc.get("expires_at"),
            )
            return EnrollToken(**doc)
        logger.warning("Fallback lookup found no usable token")
        return None
    
    async def mark_token_used(
        self, 
        token: str, 
        device_id: str, 
        used_at: datetime
    ) -> bool:
        """Mark enrollment token as used"""
        result = await self.collection.update_one(
            {"token": token},
            {
                "$set": {
                    "status": "used",
                    "used_at": used_at,
                    "used_by_device": device_id,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info("Marked enrollment token as used",
                       token=token[:8] + "...",
                       device_id=device_id)
            return True
        return False
    
    async def revoke_token(
        self, 
        token: str, 
        revoked_by: str, 
        revoked_at: datetime
    ) -> bool:
        """Revoke an enrollment token"""
        result = await self.collection.update_one(
            {"token": token},
            {
                "$set": {
                    "status": "revoked",
                    "revoked_at": revoked_at,
                    "revoked_by": revoked_by,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info("Revoked enrollment token",
                       token=token[:8] + "...",
                       revoked_by=revoked_by)
            return True
        return False
    
    async def expire_tokens(self) -> int:
        """Mark expired tokens as expired"""
        now = datetime.utcnow()
        result = await self.collection.update_many(
            {
                "status": "unused",
                "expires_at": {"$lt": now}
            },
            {
                "$set": {
                    "status": "expired",
                    "updated_at": now
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info("Expired enrollment tokens", count=result.modified_count)
        
        return result.modified_count
    
    async def get_tokens_by_store(
        self, 
        store_id: str, 
        limit: int = 50, 
        skip: int = 0
    ) -> List[EnrollToken]:
        """Get enrollment tokens by store"""
        cursor = self.collection.find(
            {"store_id": store_id}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        tokens = []
        async for token_doc in cursor:
            tokens.append(EnrollToken(**token_doc))
        
        return tokens
    
    async def get_tokens_by_creator(
        self, 
        created_by: str, 
        limit: int = 50, 
        skip: int = 0
    ) -> List[EnrollToken]:
        """Get enrollment tokens by creator"""
        cursor = self.collection.find(
            {"created_by": created_by}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        tokens = []
        async for token_doc in cursor:
            tokens.append(EnrollToken(**token_doc))
        
        return tokens
    
    async def get_token_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Get enrollment token statistics"""
        pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        stats = {}
        async for result in self.collection.aggregate(pipeline):
            stats[result["_id"]] = result["count"]
        
        return stats
    
    async def cleanup_old_tokens(self, days_old: int = 30) -> int:
        """Clean up old enrollment tokens"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        result = await self.collection.delete_many({
            "created_at": {"$lt": cutoff_date},
            "status": {"$in": ["used", "revoked", "expired"]}
        })
        
        if result.deleted_count > 0:
            logger.info("Cleaned up old enrollment tokens", 
                       count=result.deleted_count,
                       days_old=days_old)
        
        return result.deleted_count
