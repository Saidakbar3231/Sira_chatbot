from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from database.db import get_stats, get_recent_logs, get_recent_users

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not _is_admin(message.from_user.id):
        return
    await message.answer(
        "Admin panel:\n"
        "/stats — foydalanuvchilar statistikasi\n"
        "/logs — so'nggi 20 ta xabar\n"
        "/users — so'nggi 10 ta foydalanuvchi\n"
        "/index — hujjatlarni indekslash"
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not _is_admin(message.from_user.id):
        return

    s = await get_stats()

    lang_lines = "\n".join(
        f"  • {lang or 'unknown'}: {count}" for lang, count in s["top_langs"]
    )
    user_lines = "\n".join(
        f"  {i+1}. @{name}: {count} xabar"
        for i, (name, count) in enumerate(s["top_users"])
    )

    await message.answer(
        f"📊 SIRA Statistikasi\n\n"
        f"👥 Jami foydalanuvchilar: {s['total_users']}\n\n"
        f"💬 Xabarlar:\n"
        f"  • Bugun: {s['total_today']}\n"
        f"  • Bu hafta: {s['total_week']}\n"
        f"  • Jami: {s['total_all']}\n\n"
        f"🌐 Tillar:\n{lang_lines or '  —'}\n\n"
        f"🏆 Eng faol foydalanuvchilar:\n{user_lines or '  —'}"
    )


@router.message(Command("logs"))
async def cmd_logs(message: Message):
    if not _is_admin(message.from_user.id):
        return

    rows = await get_recent_logs(20)
    if not rows:
        await message.answer("Hali hech qanday xabar yo'q.")
        return

    lines = []
    for r in rows:
        name = f"@{r['username']}" if r["username"] else f"id:{r['user_id']}"
        ts = r["timestamp"][:16].replace("T", " ")
        text = r["message"][:80] + ("…" if len(r["message"]) > 80 else "")
        lines.append(f"[{ts}] {name}:\n  {text}")

    await message.answer("📋 So'nggi 20 xabar:\n\n" + "\n\n".join(lines))


@router.message(Command("users"))
async def cmd_users(message: Message):
    if not _is_admin(message.from_user.id):
        return

    rows = await get_recent_users(10)
    if not rows:
        await message.answer("Hali hech qanday foydalanuvchi yo'q.")
        return

    lines = []
    for i, r in enumerate(rows, 1):
        name = f"@{r['username']}" if r["username"] else f"id:{r['user_id']}"
        last = r["last_seen"][:16].replace("T", " ")
        lines.append(f"{i}. {name}\n   💬 {r['msg_count']} xabar | 🕐 {last}")

    await message.answer("👥 So'nggi 10 foydalanuvchi:\n\n" + "\n\n".join(lines))
