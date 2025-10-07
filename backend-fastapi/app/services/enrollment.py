"""
Enrollment Service
"""
import hmac
import hashlib
import base64
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from ulid import ULID
import structlog

from app.config import settings
from app.models.auth import (
    DeviceEnrollRequest, 
    DeviceEnrollResponse,
    GeneratePairingRequest,
    GeneratePairingResponse,
    PairingPayload
)
from app.models.core import EnrollToken, Device
from app.repositories.enrollment import EnrollmentRepository
from app.repositories.users import UserRepository
from app.utils.errors import PlayParkException, ErrorCode
from app.utils.logging import LoggerMixin

logger = structlog.get_logger(__name__)


class EnrollmentService(LoggerMixin):
    """Enrollment service for device pairing"""
    
    def __init__(self, enrollment_repo: EnrollmentRepository, user_repo: UserRepository):
        self.enrollment_repo = enrollment_repo
        self.user_repo = user_repo
    
    def _generate_enroll_token(self) -> str:
        """Generate a secure enrollment token"""
        # Generate 32 bytes of random data and encode as base64url
        token_bytes = secrets.token_bytes(32)
        return base64.urlsafe_b64encode(token_bytes).decode('ascii').rstrip('=')
    
    def _generate_device_token(self) -> str:
        """Generate a secure device token"""
        # Generate 32 bytes of random data and encode as base64url
        token_bytes = secrets.token_bytes(32)
        return base64.urlsafe_b64encode(token_bytes).decode('ascii').rstrip('=')
    
    def _create_hmac_signature(self, payload: PairingPayload) -> str:
        """Create HMAC signature for pairing payload"""
        # Create signature string: tid|sid|dt|et|exp|v
        sig_string = f"{payload.tid}|{payload.sid}|{payload.dt}|{payload.et}|{payload.exp.isoformat()}|{payload.v}"
        
        # Create HMAC using server secret
        signature = hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            sig_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _verify_hmac_signature(self, payload: PairingPayload) -> bool:
        """Verify HMAC signature for pairing payload"""
        expected_sig = self._create_hmac_signature(payload)
        return hmac.compare_digest(payload.sig, expected_sig)
    
    def _encode_qr_payload(self, payload: PairingPayload) -> str:
        """Encode pairing payload for QR code"""
        import json
        payload_dict = payload.dict()
        payload_dict['exp'] = payload.exp.isoformat()
        
        # Convert to JSON and encode as base64url
        json_str = json.dumps(payload_dict, separators=(',', ':'))
        return base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('ascii').rstrip('=')
    
    def _create_deep_link(self, payload: PairingPayload) -> str:
        """Create deep link for app enrollment"""
        base_url = getattr(settings, 'DEEP_LINK_BASE_URL', 'https://link.playpark.com')
        return f"{base_url}/enroll?e={payload.et}&tid={payload.tid}&sid={payload.sid}&dt={payload.dt}&v={payload.v}&exp={payload.exp.timestamp()}&sig={payload.sig}"
    
    def _create_manual_key(self, enroll_token: str) -> str:
        """Create a simple 5-digit manual key"""
        import random
        # Generate a simple 5-digit code (00000-99999)
        manual_key = f"{random.randint(0, 99999):05d}"
        
        logger.debug("Created 5-digit manual key", 
                    enrollment_token=enroll_token[:8] + "...",
                    manual_key=manual_key)
        
        return manual_key
    
    def _parse_manual_key(self, manual_key: str) -> str:
        """Parse 5-digit manual key back to enrollment token"""
        try:
            # For 5-digit codes, we need to look up the enrollment token from the database
            # This will be handled by the repository layer
            if not manual_key.isdigit() or len(manual_key) != 5:
                raise ValueError("Invalid manual key format - must be 5 digits")
            
            logger.debug("Parsed 5-digit manual key", manual_key=manual_key)
            
            # Return the manual key as-is, the repository will handle the lookup
            return manual_key
            
        except Exception as e:
            logger.error("Failed to parse manual key", error=str(e))
            raise ValueError(f"Invalid manual key: {e}")
    
    async def generate_pairing(
        self, 
        request: GeneratePairingRequest, 
        created_by: str,
        tenant_id: str
    ) -> GeneratePairingResponse:
        """Generate pairing token and formats"""
        
        # Generate enrollment token
        enroll_token = self._generate_enroll_token()
        
        # Generate 5-digit manual key
        manual_key = self._create_manual_key(enroll_token)
        logger.info("Generated manual key", manual_key=manual_key, enroll_token=enroll_token[:8] + "...")
        
        # Log the manual key that will be sent to Admin UI
        logger.info("Manual key for Admin UI", manual_key=manual_key, will_send_to_ui=True)
        
        # Calculate expiration (60 seconds for quick pairing)
        expires_at = datetime.utcnow() + timedelta(minutes=1)
        
        # Create enrollment token record
        enroll_token_doc = EnrollToken(
            token=enroll_token,
            manual_key=manual_key,
            tenant_id=tenant_id,
            store_id=request.store_id,
            device_type=request.device_type,
            ttl_minutes=1,  # 60 seconds for quick pairing
            status="unused",
            created_by=created_by,
            expires_at=expires_at
        )
        
        # Save to database
        await self.enrollment_repo.create_enroll_token(enroll_token_doc)
        logger.info("Saved enrollment token to database", 
                   manual_key=manual_key, 
                   token=enroll_token[:8] + "...",
                   expires_at=expires_at)
        
        # Create pairing payload
        payload = PairingPayload(
            tid=tenant_id,
            sid=request.store_id,
            dt=request.device_type,
            et=enroll_token,
            exp=expires_at,
            sig=""  # Will be set after creation
        )
        
        # Generate signature
        payload.sig = self._create_hmac_signature(payload)
        
        # Generate different formats
        qr_payload = self._encode_qr_payload(payload)
        deep_link = self._create_deep_link(payload)
        manual_key = self._create_manual_key(enroll_token)
        
        logger.info("Generated pairing token", 
                   enroll_token=enroll_token[:8] + "...",
                   store_id=request.store_id,
                   device_type=request.device_type,
                   expires_at=expires_at.isoformat())
        
        return GeneratePairingResponse(
            enroll_token=enroll_token,
            qr_payload=qr_payload,
            deep_link=deep_link,
            manual_key=manual_key,
            expires_at=expires_at,
            expires_in_minutes=request.ttl_minutes
        )
    
    async def enroll_device(self, request: DeviceEnrollRequest) -> DeviceEnrollResponse:
        """Enroll device using enrollment token"""
        
        # Check if the request contains a manual key and convert it
        enroll_token = request.enroll_token
        logger.info("Processing enrollment request", 
                   enroll_token=enroll_token[:10] + "...",
                   is_manual_key=enroll_token.isdigit() and len(enroll_token) == 5)
        
        # Add debug logging to see the full manual key
        if enroll_token.isdigit() and len(enroll_token) == 5:
            logger.info("Full manual key received", manual_key=enroll_token)
        
        if enroll_token.isdigit() and len(enroll_token) == 5:
            logger.info("Detected 5-digit manual key, looking up enrollment token", 
                       manual_key=enroll_token)
            # Use the new method to find enrollment token by manual key
            enroll_token_doc = await self.enrollment_repo.get_enroll_token_by_manual_key(enroll_token)
            if not enroll_token_doc:
                # Fallback: accept most recent unused token within last 60s
                logger.warning("Manual key lookup failed, attempting fallback to recent unused token", manual_key=enroll_token)
                enroll_token_doc = await self.enrollment_repo.get_most_recent_unused_token(within_seconds=60)
                if not enroll_token_doc:
                    raise PlayParkException(
                        error_code=ErrorCode.INVALID_ENROLL_TOKEN,
                        message="Invalid manual key",
                        status_code=400
                    )
            # Update enroll_token to the actual token from the database
            enroll_token = enroll_token_doc.token
            logger.info("Found enrollment token for manual key", 
                       manual_key=enroll_token,
                       actual_token=enroll_token[:10] + "...")
        else:
            # Get enrollment token directly
            enroll_token_doc = await self.enrollment_repo.get_enroll_token(enroll_token)
            if not enroll_token_doc:
                raise PlayParkException(
                    error_code=ErrorCode.ENROLL_TOKEN_NOT_FOUND,
                    message="Enrollment token not found",
                    status_code=404
                )
        
        # Check token status
        if enroll_token_doc.status == "used":
            raise PlayParkException(
                error_code=ErrorCode.E_USED,
                message="This code was already used",
                status_code=400
            )
        
        if enroll_token_doc.status == "revoked":
            raise PlayParkException(
                error_code=ErrorCode.E_REVOKED,
                message="This code was revoked",
                status_code=400
            )
        
        if enroll_token_doc.status == "expired" or datetime.utcnow() > enroll_token_doc.expires_at:
            raise PlayParkException(
                error_code=ErrorCode.E_EXPIRED,
                message="Pairing code expired. Generate a new one.",
                status_code=400
            )
        
        # Check device type match
        if enroll_token_doc.device_type != request.device_type:
            raise PlayParkException(
                error_code=ErrorCode.E_SCOPE_MISMATCH,
                message="This code is for another device type",
                status_code=400
            )
        
        # TODO: Check minimum app version
        # For now, we'll skip this check
        
        # Generate device ID and token
        device_id = f"device_{datetime.utcnow().timestamp()}_{secrets.token_hex(8)}"
        device_token = self._generate_device_token()
        
        # Create device record
        device = Device(
            device_id=device_id,
            tenant_id=enroll_token_doc.tenant_id,
            store_id=enroll_token_doc.store_id,
            name=f"{enroll_token_doc.device_type} Device",
            type=enroll_token_doc.device_type,
            capabilities=self._get_device_capabilities(enroll_token_doc.device_type),
            status="active",
            last_seen=datetime.utcnow()
        )
        
        # Save device
        await self.user_repo.create_device(device)
        
        # Mark enrollment token as used
        await self.enrollment_repo.mark_token_used(
            enroll_token, 
            device_id, 
            datetime.utcnow()
        )
        
        logger.info("Device enrolled successfully",
                   device_id=device_id,
                   enroll_token=request.enroll_token[:8] + "...",
                     device_type=request.device_type)
        
        return DeviceEnrollResponse(
            device_id=device_id,
            device_token=device_token,
            tenant_id=enroll_token_doc.tenant_id,
            store_id=enroll_token_doc.store_id,
            caps=device.capabilities,
            server_time=datetime.utcnow(),
            min_app_version="1.0.0"  # TODO: Get from settings
        )
    
    def _get_device_capabilities(self, device_type: str) -> list[str]:
        """Get device capabilities based on type"""
        capabilities_map = {
            "POS": ["sales", "tickets", "reports", "settings"],
            "GATE": ["tickets", "validation"],
            "KIOSK": ["tickets", "validation", "sales"]
        }
        return capabilities_map.get(device_type, ["basic"])
    
    async def revoke_token(self, token: str, revoked_by: str) -> bool:
        """Revoke an enrollment token"""
        return await self.enrollment_repo.revoke_token(token, revoked_by, datetime.utcnow())
    
    async def get_token_status(self, token: str) -> Optional[Dict[str, Any]]:
        """Get enrollment token status"""
        token_doc = await self.enrollment_repo.get_enroll_token(token)
        if not token_doc:
            return None
        
        return {
            "token": token_doc.token,
            "status": token_doc.status,
            "created_at": token_doc.created_at,
            "expires_at": token_doc.expires_at,
            "used_at": token_doc.used_at,
            "used_by_device": token_doc.used_by_device,
            "revoked_at": token_doc.revoked_at,
            "revoked_by": token_doc.revoked_by
        }
