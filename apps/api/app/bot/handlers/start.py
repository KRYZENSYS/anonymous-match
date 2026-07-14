"""Start and welcome handlers"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

router = Router(name="start")


WELCOME = """💖 <b>Anonymous Match</b> ga xush kelibsiz!

Bu yerda siz:
🔹 Anonim ravishda yangi odamlar bilan tanishasiz
🔹 Real vaqtda chat qilasiz
🔹 Hech qachon shaxsingiz oshkor bo'lmaydi

Boshlash uchun tugmani bosing 👇"""


@router.message(CommandStart(deep_link=False))
async def cmd_start(message: Message, user, is_new: bool):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Boshlash", web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}?start=app"))],
        [InlineKeyboardButton(text="💎 Premium", callback_data="premium")],
        [InlineKeyboardButton(text="ℹ️ Yordam", callback_data="help")],
    ])
    await message.answer(WELCOME, reply_markup=kb)

    if is_new:
        # Send welcome bonus notification later
        pass


@router.message(CommandStart(deep_link=True))
async def cmd_start_deeplink(message: Message, user):
    args = message.text.split()
    if len(args) > 1:
        payload = args[1]
        # Handle invite codes, payment confirmations, etc.
        if payload.startswith("ref_"):
            await message.answer(f"🎁 Siz <code>{payload[4:]}</code> taklifi orqali kirdingiz!")
        elif payload.startswith("premium_"):
            await message.answer("💎 Premium tasdiqlanmoqda...")
    await cmd_start(message, user, False)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("""
ℹ️ <b>Yordam</b>

🔹 /start — Asosiy menyu
🔹 /profile — Profilingiz
🔹 /discover — Yangi odamlar
🔹 /matches — Matchlaringiz
🔹 /premium — Premium tariflar
🔹 /settings — Sozlamalar
🔹 /help — Yordam

Savol: @kryzen_support
""")


@router.callback_query(F.data == "help")
async def cb_help(call: CallbackQuery):
    await call.message.answer("/help buyrug'ini ishlating")
    await call.answer()


from app.core.config import settings
