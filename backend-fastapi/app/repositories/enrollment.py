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
        token_dict = token.dict(by_alias=True, exclude={"id"})
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
        """Get enrollment token by manual key"""
        logger.info("get_enroll_token_by_manual_key called", manual_key=manual_key[:10] + "...")
        
        # Parse the manual key to get the key part and checksum
        if not manual_key.startswith('PP.'):
            logger.warning("Manual key does not start with PP.", manual_key=manual_key[:10] + "...")
            return None
        
        parts = manual_key[3:].split('.')
        logger.info("Manual key parts", parts=parts, count=len(parts))
        
        if len(parts) != 6:
            logger.warning("Manual key does not have 6 parts", parts=parts, count=len(parts))
            return None
        
        key_part = ''.join(parts[:5])  # 20 characters
        checksum = int(parts[5])
        
        # Verify checksum
        expected_checksum = sum(ord(c) for c in key_part) % 100
        if expected_checksum != checksum:
            return None
        
        # Search for enrollment token that matches the cleaned key part
        # Remove trailing zeros from key_part to get the actual token prefix
        token_prefix = key_part.rstrip('0')
        
        # Find enrollment token that, when cleaned, starts with this prefix
        # We need to search through all tokens and check if their cleaned version matches
        cursor = self.collection.find({
            "status": {"$in": ["unused", "active", "pending"]}
        })
        
        logger.info("Searching for enrollment token by manual key", 
                   manual_key=manual_key[:10] + "...",
                   token_prefix=token_prefix)
        
        async for token_doc in cursor:
            original_token = token_doc["token"]
            # Clean the original token the same way as in generation
            clean_token = original_token.replace('-', '').replace('_', '').replace('=', '')
            logger.info("Checking token", 
                       original_token=original_token[:10] + "...",
                       clean_token=clean_token[:20] + "...",
                       token_prefix=token_prefix,
                       matches=clean_token.startswith(token_prefix))
            if clean_token.startswith(token_prefix):
                logger.info("Found matching token", token=original_token[:10] + "...")
                return EnrollToken(**token_doc)
        
        logger.info("No matching token found", token_prefix=token_prefix)
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
