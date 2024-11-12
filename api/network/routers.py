from fastapi import APIRouter
from .admin_endpoints import admin_router
from .user_endpoints import user_router
from .debug_endpoints import debug_router
from .settings_endpoints import settings_router
from .rally_endpoints import rally_router

api_router = APIRouter()

api_router.include_router(
    debug_router,
    prefix="/debug",
    tags=["Debug"]
)
api_router.include_router(
    settings_router,
    prefix="/settings",
    tags=["Settings"]
)
api_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin"]
)
api_router.include_router(
    user_router,
    prefix="/user",
    tags=["User"]
)
api_router.include_router(
    rally_router,
    prefix="/rally",
    tags=["Rally"]
)