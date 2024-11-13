from .images import router as images_router 
from fastapi import APIRouter
from .auth import router as auth_router
from .subscription import router as subscription_router
from .chat import router as chat_router
from .user import router as user_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(subscription_router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(chat_router, prefix="/chats", tags=["chats"])
api_router.include_router(images_router, prefix="/images", tags=["images"])
api_router.include_router(user_router, prefix="/users", tags=["users"])



