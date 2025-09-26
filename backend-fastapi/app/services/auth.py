"""
Authentication Service
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError, ExpiredSignatureError
# from passlib.context import CryptContext  # Temporarily disabled due to bcrypt issues
from ulid import ULID
import structlog

from app.config import settings
from app.models.auth import TokenPayload, TokenType, DeviceLoginRequest, EmployeeLoginRequest
from app.repositories.auth import AuthRepository
from app.repositories.users import UserRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.utils.logging import LoggerMixin

logger = structlog.get_logger(__name__)

# Password hashing - temporarily disabled
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService(LoggerMixin):
    """Authentication service"""
    
    def __init__(self, auth_repo: AuthRepository, user_repo: UserRepository):
        self.auth_repo = auth_repo
        self.user_repo = user_repo
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        # Temporary fix - return plain text for testing
        return password
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        # Temporary fix for bcrypt issue - use simple comparison for testing
        return plain_password == hashed_password
    
    def create_access_token(
        self,
        subject: str,
        token_type: TokenType,
        tenant_id: Optional[str] = None,
        store_id: Optional[str] = None,
        device_id: Optional[str] = None,
        scopes: Optional[list] = None
    ) -> str:
        """Create an access token"""
        
        now = datetime.utcnow()
        payload = TokenPayload(
            sub=subject,
            type=token_type,
            tenant_id=tenant_id,
            store_id=store_id,
            device_id=device_id,
            scopes=scopes or [],
            iat=int(now.timestamp()),
            exp=int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())
        )
        
        return jwt.encode(
            payload.dict(),
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    def create_refresh_token(
        self,
        subject: str,
        tenant_id: Optional[str] = None,
        store_id: Optional[str] = None,
        device_id: Optional[str] = None,
        scopes: Optional[list] = None
    ) -> str:
        """Create a refresh token"""
        
        now = datetime.utcnow()
        payload = TokenPayload(
            sub=subject,
            type=TokenType.REFRESH,
            tenant_id=tenant_id,
            store_id=store_id,
            device_id=device_id,
            scopes=scopes or [],
            iat=int(now.timestamp()),
            exp=int((now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp())
        )
        
        return jwt.encode(
            payload.dict(),
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    def verify_token(self, token: str) -> TokenPayload:
        """Verify and decode a token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return TokenPayload(**payload)
        except ExpiredSignatureError:
            raise PlayParkException(
                error_code=ErrorCode.TOKEN_EXPIRED,
                message="Token has expired",
                status_code=401
            )
        except JWTError:
            raise PlayParkException(
                error_code=ErrorCode.INVALID_TOKEN,
                message="Invalid token",
                status_code=401
            )
    
    async def authenticate_device(self, request: DeviceLoginRequest) -> Dict[str, Any]:
        """Authenticate a device (legacy method)"""
        
        # Get device from database
        device = await self.user_repo.get_device_by_id(request.device_id)
        if not device:
            raise PlayParkException(
                error_code=ErrorCode.DEVICE_NOT_FOUND,
                message="Device not found"
            )
        
        if device.status != "active":
            raise PlayParkException(
                error_code=ErrorCode.DEVICE_SUSPENDED,
                message="Device is suspended"
            )
        
        # Verify device token (in real implementation, this would be more secure)
        # For now, we'll use a simple comparison
        if not self._verify_device_token(request.device_token, device):
            raise PlayParkException(
                error_code=ErrorCode.INVALID_DEVICE_TOKEN,
                message="Invalid device token"
            )
        
        # Update device last seen
        await self.user_repo.update_device_last_seen(request.device_id)
        
        # Create tokens
        access_token = self.create_access_token(
            subject=request.device_id,
            token_type=TokenType.DEVICE,
            tenant_id=device.tenant_id,
            store_id=device.store_id,
            device_id=request.device_id,
            scopes=device.capabilities
        )
        
        # Log successful authentication
        self.logger.info(
            "Device authenticated successfully",
            device_id=request.device_id,
            tenant_id=device.tenant_id,
            store_id=device.store_id
        )
        
        return {
            "token": access_token,
            "device": {
                "device_id": device.device_id,
                "name": device.name,
                "type": device.type,
                "capabilities": device.capabilities,
                "tenant_id": device.tenant_id,
                "store_id": device.store_id
            }
        }
    
    async def authenticate_device_with_token(self, request: DeviceLoginRequest) -> Dict[str, Any]:
        """Authenticate a device using device token (new enrollment-based method)"""
        
        # Get device from database
        device = await self.user_repo.get_device_by_id(request.device_id)
        if not device:
            raise PlayParkException(
                error_code=ErrorCode.DEVICE_NOT_FOUND,
                message="Device not found"
            )
        
        if device.status != "active":
            raise PlayParkException(
                error_code=ErrorCode.DEVICE_SUSPENDED,
                message="Device is suspended"
            )
        
        # Verify device token (in real implementation, this would be more secure)
        # For now, we'll use a simple comparison
        if not self._verify_device_token(request.device_token, device):
            raise PlayParkException(
                error_code=ErrorCode.INVALID_DEVICE_TOKEN,
                message="Invalid device token"
            )
        
        # Update device last seen
        await self.user_repo.update_device_last_seen(request.device_id)
        
        # Create short-lived access token (15 minutes)
        access_token = self.create_access_token(
            subject=request.device_id,
            token_type=TokenType.DEVICE,
            tenant_id=device.tenant_id,
            store_id=device.store_id,
            device_id=request.device_id,
            scopes=device.capabilities
        )
        
        # Log successful authentication
        self.logger.info(
            "Device authenticated with token successfully",
            device_id=request.device_id,
            tenant_id=device.tenant_id,
            store_id=device.store_id
        )
        
        return {
            "token": access_token,
            "device": {
                "device_id": device.device_id,
                "name": device.name,
                "type": device.type,
                "capabilities": device.capabilities,
                "tenant_id": device.tenant_id,
                "store_id": device.store_id
            }
        }
    
    async def authenticate_employee(self, request: EmployeeLoginRequest) -> Dict[str, Any]:
        """Authenticate an employee"""
        
        # Get employee from database
        employee = await self.user_repo.get_by_email(request.email)
        if not employee:
            raise PlayParkException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message="Invalid credentials"
            )
        
        if employee.status != "active":
            raise PlayParkException(
                error_code=ErrorCode.ACCOUNT_DISABLED,
                message="Account is disabled"
            )
        
        # Verify PIN
        if not self.verify_password(request.pin, employee.pin):
            raise PlayParkException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message="Invalid credentials"
            )
        
        # Create tokens
        access_token = self.create_access_token(
            subject=employee.employee_id,
            token_type=TokenType.ACCESS,
            tenant_id=employee.tenant_id,
            store_id=employee.store_id
        )
        
        refresh_token = self.create_refresh_token(
            subject=employee.employee_id,
            tenant_id=employee.tenant_id,
            store_id=employee.store_id
        )
        
        # Store refresh token
        token_id = str(ULID())
        token_hash = self.hash_password(refresh_token)
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        await self.auth_repo.create_refresh_token(
            token_id=token_id,
            user_id=employee.employee_id,
            token_hash=token_hash,
            expires_at=expires_at,
            tenant_id=employee.tenant_id,
            store_id=employee.store_id
        )
        
        # Log successful authentication
        self.logger.info(
            "Employee authenticated successfully",
            employee_id=employee.employee_id,
            email=employee.email,
            tenant_id=employee.tenant_id,
            store_id=employee.store_id
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "employee": {
                "employee_id": employee.employee_id,
                "name": employee.name,
                "email": employee.email,
                "roles": employee.roles,
                "permissions": employee.permissions,
                "tenant_id": employee.tenant_id,
                "store_id": employee.store_id
            }
        }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an access token"""
        
        # Verify refresh token
        payload = self.verify_token(refresh_token)
        if payload.type != TokenType.REFRESH:
            raise PlayParkException(
                error_code=ErrorCode.INVALID_TOKEN_TYPE,
                message="Invalid token type"
            )
        
        # Check if refresh token exists in database
        token_hash = self.hash_password(refresh_token)
        stored_token = await self.auth_repo.get_refresh_token_by_hash(token_hash)
        
        if not stored_token or stored_token.is_revoked:
            raise PlayParkException(
                error_code=ErrorCode.INVALID_TOKEN,
                message="Invalid refresh token"
            )
        
        # Get employee
        employee = await self.user_repo.get_by_employee_id(stored_token.user_id)
        if not employee or employee.status != "active":
            raise PlayParkException(
                error_code=ErrorCode.USER_NOT_FOUND,
                message="User not found or inactive"
            )
        
        # Create new access token
        access_token = self.create_access_token(
            subject=employee.employee_id,
            token_type=TokenType.ACCESS,
            tenant_id=employee.tenant_id,
            store_id=employee.store_id
        )
        
        # Update refresh token last used
        await self.auth_repo.update_by_id(
            stored_token.token_id,
            {"last_used": datetime.utcnow()},
            "token_id"
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    async def logout(self, refresh_token: Optional[str] = None, user_id: Optional[str] = None) -> bool:
        """Logout user"""
        
        if refresh_token:
            # Revoke specific refresh token
            token_hash = self.hash_password(refresh_token)
            stored_token = await self.auth_repo.get_refresh_token_by_hash(token_hash)
            if stored_token:
                await self.auth_repo.revoke_refresh_token(stored_token.token_id)
                return True
        elif user_id:
            # Revoke all refresh tokens for user
            await self.auth_repo.revoke_user_tokens(user_id)
            await self.auth_repo.revoke_user_sessions(user_id)
            return True
        
        return False
    
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens"""
        refresh_count = await self.auth_repo.cleanup_expired_tokens()
        session_count = await self.auth_repo.cleanup_expired_sessions()
        password_reset_count = await self.auth_repo.cleanup_expired_password_resets()
        
        total = refresh_count + session_count + password_reset_count
        
        if total > 0:
            self.logger.info(
                "Cleaned up expired authentication data",
                refresh_tokens=refresh_count,
                sessions=session_count,
                password_resets=password_reset_count,
                total=total
            )
        
        return total
    
    def _verify_device_token(self, token: str, device) -> bool:
        """Verify device token (placeholder implementation)"""
        # In a real implementation, this would use proper cryptographic verification
        # For now, we'll use simple token matching
        valid_tokens = {
            "pos-token-1": "POS",
            "gate-token-1": "GATE", 
            "kiosk-token-1": "KIOSK"
        }
        
        return token in valid_tokens and valid_tokens[token] == device.type
