"""
Authentication Repository
"""
from typing import Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.auth import RefreshToken, Session, PasswordReset
from app.repositories.base import BaseRepository


class AuthRepository(BaseRepository):
    """Authentication repository"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__("refresh_tokens", RefreshToken)
        self.db = db
        self.sessions_repo = BaseRepository("sessions", Session)
        self.password_resets_repo = BaseRepository("password_resets", PasswordReset)
    
    async def create_refresh_token(
        self,
        token_id: str,
        user_id: str,
        token_hash: str,
        expires_at: datetime,
        device_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        store_id: Optional[str] = None,
        scopes: Optional[List[str]] = None
    ) -> RefreshToken:
        """Create a new refresh token"""
        
        refresh_token = RefreshToken(
            token_id=token_id,
            user_id=user_id,
            token_hash=token_hash,
            device_id=device_id,
            tenant_id=tenant_id,
            store_id=store_id,
            scopes=scopes or [],
            expires_at=expires_at
        )
        
        return await self.create(refresh_token)
    
    async def get_refresh_token_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Get refresh token by hash"""
        return await self.get_by_field("token_hash", token_hash)
    
    async def revoke_refresh_token(self, token_id: str) -> bool:
        """Revoke a refresh token"""
        result = await self.update_by_id(
            token_id,
            {"is_revoked": True, "revoked_at": datetime.utcnow()},
            "token_id"
        )
        return result is not None
    
    async def revoke_user_tokens(self, user_id: str, device_id: Optional[str] = None) -> int:
        """Revoke all refresh tokens for a user"""
        query = {"user_id": user_id, "is_revoked": False}
        if device_id:
            query["device_id"] = device_id
        
        result = await self.collection.update_many(
            query,
            {"$set": {"is_revoked": True, "revoked_at": datetime.utcnow()}}
        )
        
        return result.modified_count
    
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired refresh tokens"""
        result = await self.collection.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        return result.deleted_count
    
    async def create_session(
        self,
        session_id: str,
        user_id: str,
        expires_at: datetime,
        device_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        store_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Session:
        """Create a new user session"""
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            device_id=device_id,
            tenant_id=tenant_id,
            store_id=store_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        
        return await self.sessions_repo.create(session)
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        return await self.sessions_repo.get_by_id(session_id, "session_id")
    
    async def update_session_activity(self, session_id: str) -> Optional[Session]:
        """Update session last activity"""
        return await self.sessions_repo.update_by_id(
            session_id,
            {"last_activity": datetime.utcnow()},
            "session_id"
        )
    
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke a session"""
        result = await self.sessions_repo.update_by_id(
            session_id,
            {"is_active": False, "revoked_at": datetime.utcnow()},
            "session_id"
        )
        return result is not None
    
    async def revoke_user_sessions(self, user_id: str, device_id: Optional[str] = None) -> int:
        """Revoke all sessions for a user"""
        query = {"user_id": user_id, "is_active": True}
        if device_id:
            query["device_id"] = device_id
        
        result = await self.sessions_repo.collection.update_many(
            query,
            {"$set": {"is_active": False, "revoked_at": datetime.utcnow()}}
        )
        
        return result.modified_count
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        result = await self.sessions_repo.collection.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        return result.deleted_count
    
    async def create_password_reset(
        self,
        reset_id: str,
        user_id: str,
        email: str,
        token_hash: str,
        expires_at: datetime
    ) -> PasswordReset:
        """Create a password reset request"""
        
        password_reset = PasswordReset(
            reset_id=reset_id,
            user_id=user_id,
            email=email,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        return await self.password_resets_repo.create(password_reset)
    
    async def get_password_reset_by_hash(self, token_hash: str) -> Optional[PasswordReset]:
        """Get password reset by token hash"""
        return await self.password_resets_repo.get_by_field("token_hash", token_hash)
    
    async def mark_password_reset_used(self, reset_id: str) -> bool:
        """Mark password reset as used"""
        result = await self.password_resets_repo.update_by_id(
            reset_id,
            {"is_used": True, "used_at": datetime.utcnow()},
            "reset_id"
        )
        return result is not None
    
    async def cleanup_expired_password_resets(self) -> int:
        """Clean up expired password reset requests"""
        result = await self.password_resets_repo.collection.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        return result.deleted_count
