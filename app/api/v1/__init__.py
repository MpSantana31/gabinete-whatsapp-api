from fastapi import APIRouter
from .endpoints import webhooks_router, contacts_router, ws_router, conversations_router

api_router = APIRouter()
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(contacts_router, prefix="/contacts", tags=["contacts"])
api_router.include_router(ws_router, prefix="/ws", tags=["ws"])
api_router.include_router(conversations_router, prefix="/conversations", tags=["conversations"])

__all__ = ["api_router"]