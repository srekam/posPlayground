"""
Deep Link Resolver Router
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse, HTMLResponse
import structlog

from app.services.enrollment import EnrollmentService
from app.deps import get_enrollment_service
from app.utils.errors import PlayParkException, ErrorCode

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/link/enroll")
async def resolve_enroll_link(
    request: Request,
    e: str = Query(..., description="Enrollment token"),
    tid: Optional[str] = Query(None, description="Tenant ID"),
    sid: Optional[str] = Query(None, description="Store ID"),
    dt: Optional[str] = Query(None, description="Device type"),
    v: Optional[int] = Query(1, description="Version"),
    exp: Optional[float] = Query(None, description="Expiration timestamp"),
    sig: Optional[str] = Query(None, description="HMAC signature"),
    enrollment_service: EnrollmentService = Depends(get_enrollment_service)
) -> RedirectResponse:
    """Resolve deep link for device enrollment"""
    
    try:
        # Log deep link access
        logger.info("Deep link access attempt",
                   enroll_token=e[:8] + "..." if e else "none",
                   tenant_id=tid,
                   store_id=sid,
                   device_type=dt,
                   client_ip=request.client.host if request.client else "unknown",
                   user_agent=request.headers.get("user-agent", "unknown"))
        
        # Basic validation
        if not e:
            return _create_fallback_page("Missing enrollment token")
        
        # Check if we have all required parameters for signature validation
        if all([tid, sid, dt, exp, sig]):
            # Validate signature if all parameters are present
            from app.models.auth import PairingPayload
            from datetime import datetime
            
            try:
                payload = PairingPayload(
                    v=v or 1,
                    tid=tid,
                    sid=sid,
                    dt=dt,
                    et=e,
                    exp=datetime.fromtimestamp(exp),
                    sig=sig
                )
                
                # Verify signature
                if not enrollment_service._verify_hmac_signature(payload):
                    logger.warning("Invalid signature in deep link",
                                 enroll_token=e[:8] + "...",
                                 client_ip=request.client.host if request.client else "unknown")
                    return _create_fallback_page("Invalid pairing code signature")
                
                # Check expiration
                if datetime.utcnow().timestamp() > exp:
                    logger.warning("Expired deep link",
                                 enroll_token=e[:8] + "...",
                                 client_ip=request.client.host if request.client else "unknown")
                    return _create_fallback_page("Pairing code expired. Generate a new one.")
                
            except Exception as ex:
                logger.warning("Deep link validation failed",
                             enroll_token=e[:8] + "...",
                             error=str(ex),
                             client_ip=request.client.host if request.client else "unknown")
                return _create_fallback_page("Invalid pairing code format")
        
        # Check token status
        token_status = await enrollment_service.get_token_status(e)
        if not token_status:
            return _create_fallback_page("Pairing code not found")
        
        if token_status["status"] == "used":
            return _create_fallback_page("This code was already used")
        
        if token_status["status"] == "revoked":
            return _create_fallback_page("This code was revoked")
        
        if token_status["status"] == "expired":
            return _create_fallback_page("Pairing code expired. Generate a new one.")
        
        # Create deep link for app
        app_deep_link = f"playpark://enroll?e={e}"
        if tid:
            app_deep_link += f"&tid={tid}"
        if sid:
            app_deep_link += f"&sid={sid}"
        if dt:
            app_deep_link += f"&dt={dt}"
        if v:
            app_deep_link += f"&v={v}"
        if exp:
            app_deep_link += f"&exp={exp}"
        if sig:
            app_deep_link += f"&sig={sig}"
        
        # Log successful resolution
        logger.info("Deep link resolved successfully",
                   enroll_token=e[:8] + "...",
                   app_link=app_deep_link,
                   client_ip=request.client.host if request.client else "unknown")
        
        # Redirect to app deep link
        return RedirectResponse(url=app_deep_link, status_code=302)
    
    except Exception as e:
        logger.error("Deep link resolution failed",
                    enroll_token=e[:8] + "..." if e else "none",
                    error=str(e),
                    client_ip=request.client.host if request.client else "unknown")
        return _create_fallback_page("Failed to process pairing code")


@router.get("/link/enroll/fallback")
async def enroll_fallback_page(
    request: Request,
    error: Optional[str] = Query(None, description="Error message")
) -> HTMLResponse:
    """Fallback page for when app is not installed"""
    
    error_message = error or "Unable to open the PlayPark app"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PlayPark Device Pairing</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: white;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 400px;
                width: 100%;
                text-align: center;
            }}
            .logo {{
                width: 80px;
                height: 80px;
                background: #667eea;
                border-radius: 20px;
                margin: 0 auto 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 32px;
                font-weight: bold;
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
                font-size: 24px;
            }}
            .error {{
                color: #e74c3c;
                background: #fdf2f2;
                border: 1px solid #fecaca;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
                font-size: 14px;
            }}
            .instructions {{
                color: #666;
                line-height: 1.6;
                margin: 20px 0;
            }}
            .download-btn {{
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                text-decoration: none;
                display: inline-block;
                margin: 10px;
                transition: background 0.2s;
            }}
            .download-btn:hover {{
                background: #5a6fd8;
            }}
            .manual-key {{
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 14px;
                word-break: break-all;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">PP</div>
            <h1>PlayPark Device Pairing</h1>
            
            <div class="error">
                {error_message}
            </div>
            
            <div class="instructions">
                <p><strong>To pair your device:</strong></p>
                <ol style="text-align: left; margin: 20px 0;">
                    <li>Install the PlayPark app from the App Store or Google Play</li>
                    <li>Open the app and tap "Pair Device"</li>
                    <li>Scan the QR code or enter the manual key</li>
                </ol>
            </div>
            
            <a href="https://play.google.com/store/apps/details?id=com.playpark.app" class="download-btn">
                Download for Android
            </a>
            
            <a href="https://apps.apple.com/app/playpark/id123456789" class="download-btn">
                Download for iOS
            </a>
            
            <div class="instructions">
                <p><strong>Or enter this code manually in the app:</strong></p>
                <div class="manual-key">
                    Manual pairing code will be shown here
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content, status_code=200)


def _create_fallback_page(error_message: str) -> HTMLResponse:
    """Create a fallback page with error message"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PlayPark Pairing Error</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: white;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 400px;
                width: 100%;
                text-align: center;
            }}
            .logo {{
                width: 80px;
                height: 80px;
                background: #e74c3c;
                border-radius: 20px;
                margin: 0 auto 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 32px;
                font-weight: bold;
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
                font-size: 24px;
            }}
            .error {{
                color: #e74c3c;
                background: #fdf2f2;
                border: 1px solid #fecaca;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
                font-size: 14px;
            }}
            .instructions {{
                color: #666;
                line-height: 1.6;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">!</div>
            <h1>Pairing Error</h1>
            
            <div class="error">
                {error_message}
            </div>
            
            <div class="instructions">
                <p>Please contact your administrator to generate a new pairing code.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content, status_code=400)
