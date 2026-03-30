import asyncio
import logging
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from config import settings
from database.db import init_db
from handlers import router

# Console handler
_console = logging.StreamHandler()
_console.setLevel(logging.INFO)

# File handler — errors only
_file = RotatingFileHandler("errors.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
_file.setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[_console, _file],
)
logger = logging.getLogger(__name__)


USER_COMMANDS = [
    BotCommand(command="start", description="Botni ishga tushirish"),
    BotCommand(command="help", description="Yordam"),
    BotCommand(command="clear", description="Suhbatni tozalash"),
]

ADMIN_COMMANDS = USER_COMMANDS + [
    BotCommand(command="stats", description="Statistika"),
    BotCommand(command="logs", description="So'nggi xabarlar"),
    BotCommand(command="users", description="Foydalanuvchilar"),
    BotCommand(command="index", description="Fayllarni indekslash"),
]


async def setup_commands(bot: Bot):
    await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeDefault())
    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.set_my_commands(
                ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=admin_id)
            )
        except Exception as e:
            logger.warning(f"Could not set admin commands for {admin_id}: {e}")


async def main():
    await init_db()
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await setup_commands(bot)
    logger.info("Starting SIRA bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
