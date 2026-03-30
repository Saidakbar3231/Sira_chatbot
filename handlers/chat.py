import logging
from aiogram import Bot, Router, F
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from database.db import save_message
from rag.document_loader import load_documents
from rag.embeddings import index_documents, get_collection_count
from rag.retriever import retrieve
from services.gemini_service import ask_gemini
from utils.history import add_to_history, get_history, clear_history
from utils.language_detect import detect_language

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_message(message: Message, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text
    lang = detect_language(text)

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        context = await retrieve(text)
        history = get_history(user_id)
        answer = await ask_gemini(text, history=history, context=context)

        add_to_history(user_id, "user", text)
        add_to_history(user_id, "assistant", answer)

        await save_message(user_id, username, text, lang)
        await message.answer(answer)

    except RuntimeError as e:
        # All 3 keys exhausted
        logger.error(f"All Groq keys exhausted for user {user_id}: {e}")
        await message.answer("Bot hozir band, 1 daqiqadan keyin urinib ko'ring.")
    except Exception as e:
        logger.error(f"Error handling message from user {user_id}: {e}", exc_info=True)
        await message.answer("Xatolik yuz berdi, qayta urinib ko'ring.")


@router.message(Command("clear"))
async def cmd_clear(message: Message):
    clear_history(message.from_user.id)
    await message.answer("Suhbat tarixi tozalandi.")


@router.message(Command("index"))
async def cmd_index(message: Message):
    if message.from_user.id not in settings.ADMIN_IDS:
        return

    status = await message.answer("📂 Fayllar yuklanmoqda...")
    try:
        docs = load_documents("data")
        if not docs:
            await status.edit_text(
                "⚠️ data/ papkasida hech qanday fayl topilmadi (PDF, TXT yoki DOCX)."
            )
            return

        await status.edit_text(f"⚙️ {len(docs)} bo'lak indekslanmoqda...")
        count = await index_documents(docs)
        total = await get_collection_count()
        await status.edit_text(
            f"✅ Indekslash tugadi!\n"
            f"• Yangi bo'laklar: {count}\n"
            f"• Jami bazada: {total}"
        )
    except Exception as e:
        logger.error(f"Indexing error: {e}", exc_info=True)
        await status.edit_text("❌ Indekslashda xatolik yuz berdi.")
