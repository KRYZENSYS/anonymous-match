"""API v1 router — barcha endpointlar birlashtirilgan."""
from fastapi import APIRouter

from app.routers import auth, users, discover, chats, notifications, premium, reports, admin, media, ws

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(discover.router)
api_router.include_router(chats.router)
api_router.include_router(notifications.router)
api_router.include_router(premium.router)
api_router.include_router(reports.router)
api_router.include_router(admin.router)
api_router.include_router(media.router)
api_router.include_router(ws.router)
