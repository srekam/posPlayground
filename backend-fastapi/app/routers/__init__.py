"""
API Routers Package
"""
from .auth import router as auth_router
from .users import router as users_router
from .roles import router as roles_router
from .catalog import router as catalog_router
from .sales import router as sales_router
from .tickets import router as tickets_router
from .shifts import router as shifts_router
from .reports import router as reports_router
from .settings import router as settings_router
from .webhooks import router as webhooks_router
from .sync import router as sync_router
from .provider import router as provider_router

__all__ = [
    "auth_router",
    "users_router", 
    "roles_router",
    "catalog_router",
    "sales_router",
    "tickets_router",
    "shifts_router",
    "reports_router",
    "settings_router",
    "webhooks_router",
    "sync_router",
    "provider_router",
]
