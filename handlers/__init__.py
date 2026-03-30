from aiogram import Router

from handlers.start import router as start_router
from handlers.chat import router as chat_router
from handlers.admin import router as admin_router

router = Router()
router.include_router(start_router)
router.include_router(chat_router)
router.include_router(admin_router)
