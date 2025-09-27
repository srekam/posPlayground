"""
Secrets Repository
"""
from typing import List, Optional
from datetime import datetime

from .base import BaseRepository
from app.models.secrets import Secret


class SecretRepository(BaseRepository[Secret]):
    """Secret repository"""
    
    def __init__(self):
        super().__init__("secrets", Secret)
    
    async def get_active_by_kind(self, kind: str) -> Optional[Secret]:
        """Get active secret by kind"""
        now = datetime.utcnow()
        query = {
            "kind": kind,
            "active": True,
            "$or": [
                {"expires_at": {"$gt": now}},
                {"expires_at": None}
            ]
        }
        sort = [("version", -1)]
        results = await self.get_many(query, limit=1, sort=sort)
        return results[0] if results else None
    
    async def get_by_kind_and_version(self, kind: str, version: int) -> Optional[Secret]:
        """Get secret by kind and version"""
        query = {"kind": kind, "version": version}
        return await self.get_many(query, limit=1)[0] if await self.count(query) > 0 else None
    
    async def rotate_secret(
        self,
        secret_id: str,
        kind: str,
        key_hash: str,
        created_by: str,
        expires_at: Optional[datetime] = None,
        meta: Optional[dict] = None
    ) -> Secret:
        """Rotate secret (deactivate old, create new)"""
        # Get current active secret to determine next version
        current = await self.get_active_by_kind(kind)
        next_version = (current.version + 1) if current else 1
        
        # Deactivate current secret
        if current:
            await self.update_by_id(current.id, {"active": False})
        
        # Create new secret
        now = datetime.utcnow()
        secret_data = {
            "secret_id": secret_id,
            "kind": kind,
            "version": next_version,
            "key_hash": key_hash,
            "active": True,
            "created_by": created_by,
            "expires_at": expires_at,
            "meta": meta or {},
            "created_at": now,
            "updated_at": now
        }
        
        result = await self.collection.insert_one(secret_data)
        secret_data["_id"] = result.inserted_id
        return Secret(**secret_data)
    
    async def deactivate(self, secret_id: str) -> Optional[Secret]:
        """Deactivate secret"""
        return await self.update_by_id(secret_id, {"active": False}, "secret_id")
    
    async def get_secret_history(self, kind: str, limit: int = 10) -> List[Secret]:
        """Get secret history for a kind"""
        query = {"kind": kind}
        sort = [("version", -1)]
        return await self.get_many(query, limit=limit, sort=sort)
    
    async def cleanup_expired_secrets(self) -> int:
        """Clean up expired secrets"""
        now = datetime.utcnow()
        query = {
            "active": False,
            "expires_at": {"$lt": now}
        }
        
        result = await self.collection.delete_many(query)
        return result.deleted_count
