from fastapi import APIRouter

from app.api import admin, auth, health, loyalty, me, staff, wallet


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(me.router, tags=["me"])
api_router.include_router(loyalty.router, tags=["loyalty"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
api_router.include_router(staff.router, prefix="/staff", tags=["staff"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
