from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()

HELP_TEXT = (
    "Men SIRA — Nematodalar va biopreparat texnologiyasi bo'yicha ixtisoslashgan AI yordamchiman.\n\n"
    "Buyruqlar:\n"
    "/start — botni ishga tushirish\n"
    "/help — yordam\n"
    "/clear — suhbat tarixini tozalash"
)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Salom, {message.from_user.first_name}! {HELP_TEXT}"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT)
