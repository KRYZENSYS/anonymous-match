"""Telegram bot — aiogram 3."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup,
    WebAppInfo,
)
from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_maker
from app.models import User, Log
from app.services.user_service import UserService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

bot_instance: Any = None


class BotHolder:
    """Bot reference saqlash uchun."""
    bot: Bot | None = None


async def start_bot():
    """Bot ishga tushirish."""
    if not settings.BOT_TOKEN:
        logger.info("BOT_TOKEN topilmadi — bot o'chirilgan")
        return

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    BotHolder.bot = bot
    bot_instance.bot = bot

    # ===== Handlers =====
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        args = message.text.split(maxsplit=1)
        ref = args[1] if len(args) > 1 and args[1].startswith("ref_") else None

        # User ro'yxatdan o'tkazish
        async with async_session_maker() as db:
            user, is_new = await UserService.get_or_create_from_telegram(
                db, {"user": {
                    "id": message.from_user.id,
                    "username": message.from_user.username,
                    "first_name": message.from_user.first_name,
                    "photo_url": None,
                    "language_code": message.from_user.language_code,
                    "is_premium": getattr(message.from_user, "is_premium", False),
                }},
                device_id="telegram",
            )

        # WebApp tugmasi
        webapp_url = f"{settings.WEBAPP_URL}?startapp={user.public_id}"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔥 Anonim Match",
                web_app=WebAppInfo(url=webapp_url),
            )],
            [
                InlineKeyboardButton(text="👤 Profilim", callback_data="profile"),
                InlineKeyboardButton(text="💎 Premium", callback_data="premium"),
            ],
            [
                InlineKeyboardButton(text="❓ Yordam", callback_data="help"),
                InlineKeyboardButton(text="🌐 Til", callback_data="language"),
            ],
        ])

        if is_new:
            text = (
                f"👋 <b>Salom, {message.from_user.first_name}!</b>\n\n"
                "Men <b>Anonymous Match</b> botiman — bu yerda siz anonim tarzda "
                "yangi odamlar bilan tanishishingiz mumkin.\n\n"
                "🔐 <b>Anonimlik kafolati:</b>\n"
                "• Hech kim sizning haqiqiy ismingizni ko'rmaydi\n"
                "• Telegram username'ngiz yashirin\n"
                "• Faqat siz tanlagan ma'lumotlar ko'rinadi\n\n"
                "Boshlash uchun quyidagi tugmani bosing 👇"
            )
        else:
            text = (
                f"👋 <b>Qaytib keldingiz, {message.from_user.first_name}!</b>\n\n"
                "Yangi odamlar bilan tanishishni davom ettiring 👇"
            )

        await message.answer(text, reply_markup=keyboard)

    @dp.message(Command("profile"))
    async def cmd_profile(message: types.Message):
        async with async_session_maker() as db:
            res = await db.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = res.scalar_one_or_none()
            if not user:
                await message.answer("Avval /start ni bosing")
                return
            profile = await UserService.get_profile(db, user)
            status = await __import__('app.services.premium_service', fromlist=['PremiumService']).PremiumService.get_status(db, user)

        text = (
            f"👤 <b>Sizning profilingiz</b>\n\n"
            f"🆔 ID: <code>{user.public_id}</code>\n"
            f"📛 Nickname: {profile.nickname if profile else 'Yoq'}\n"
            f"⭐ Premium: {'Ha' if status['is_premium'] else 'Yoq'}\n"
            f"❤️ Likes: {profile.likes_sent if profile else 0} / {profile.likes_received if profile else 0}\n"
            f"🎯 Matches: {profile.match_count if profile else 0}\n"
        )
        await message.answer(text)

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        text = (
            "❓ <b>Yordam</b>\n\n"
            "<b>Asosiy buyruqlar:</b>\n"
            "/start — Botni boshlash\n"
            "/profile — Profilingiz\n"
            "/premium — Premium tariflar\n"
            "/help — Yordam\n\n"
            "<b>Anonim Match</b> orqali:\n"
            "• Yangi odamlar bilan tanishing\n"
            "• Like / SuperLike bering\n"
            "• Mos kelganlar bilan chat qiling\n"
            "• Premium imkoniyatlardan foydalaning\n\n"
            "Savollar bo'lsa: @kryzen_support"
        )
        await message.answer(text)

    @dp.message(Command("premium"))
    async def cmd_premium(message: types.Message):
        text = (
            "💎 <b>Premium tariflar</b>\n\n"
            "🌟 <b>Plus</b> — 500 ⭐\n"
            "• Unlimited likes\n"
            "• 5 super likes / hafta\n"
            "• Reklama yo'q\n\n"
            "💫 <b>Gold</b> — 1200 ⭐\n"
            "• Plus hammasi\n"
            "• 10 super likes / hafta\n"
            "• Kim profilingni ko'rgan\n\n"
            "💠 <b>Platinum</b> — 2500 ⭐\n"
            "• Gold hammasi\n"
            "• Cheksiz super likes\n"
            "• VIP Badge\n\n"
            "Sotib olish uchun WebApp ga kiring 👇"
        )
        webapp_url = settings.WEBAPP_URL
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 Premium olish", web_app=WebAppInfo(url=webapp_url))],
        ])
        await message.answer(text, reply_markup=keyboard)

    @dp.callback_query(F.data == "profile")
    async def cb_profile(callback: types.CallbackQuery):
        await cmd_profile(callback.message)
        await callback.answer()

    @dp.callback_query(F.data == "premium")
    async def cb_premium(callback: types.CallbackQuery):
        await cmd_premium(callback.message)
        await callback.answer()

    @dp.callback_query(F.data == "help")
    async def cb_help(callback: types.CallbackQuery):
        await cmd_help(callback.message)
        await callback.answer()

    @dp.callback_query(F.data == "language")
    async def cb_language(callback: types.CallbackQuery):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            ],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        ])
        await callback.message.answer("Tilni tanlang:", reply_markup=keyboard)
        await callback.answer()

    @dp.callback_query(F.data.startswith("lang_"))
    async def cb_set_lang(callback: types.CallbackQuery):
        lang = callback.data.split("_")[1]
        async with async_session_maker() as db:
            res = await db.execute(
                select(User).where(User.telegram_id == callback.from_user.id)
            )
            user = res.scalar_one_or_none()
            if user:
                await UserService.set_preferred_language(db, user, lang)
        await callback.answer(f"Til o'zgartirildi: {lang.upper()}")
        await callback.message.edit_text(f"✅ Til: {lang.upper()}")

    @dp.pre_checkout_query()
    async def process_pre_checkout(pre_checkout: types.PreCheckoutQuery):
        await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)

    @dp.message(F.successful_payment)
    async def process_successful_payment(message: types.Message):
        payment = message.successful_payment
        async with async_session_maker() as db:
            res = await db.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = res.scalar_one_or_none()
            if user:
                # TODO: payment.invoice_payload ni parse qilib premium faollashtirish
                await NotificationService.create(
                    db, user.id, "premium_expiring",
                    "To'lov qabul qilindi!",
                    "Premium tez orada faollashadi",
                    "💎"
                )
        await message.answer("✅ To'lov qabul qilindi!")

    @dp.message()
    async def fallback(message: types.Message):
        await message.answer(
            "Buyruqlar:\n"
            "/start — Boshlash\n"
            "/profile — Profil\n"
            "/premium — Premium\n"
            "/help — Yordam"
        )

    logger.info("🤖 Telegram bot ishga tushmoqda...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Bot polling error: {e}")
    finally:
        await bot.session.close()


async def stop_bot(task):
    """Bot'ni to'xtatish."""
    if BotHolder.bot:
        try:
            await BotHolder.bot.session.close()
        except Exception:
            pass
    task.cancel()
    try:
        await task
    except (asyncio.CancelledError, Exception):
        pass
