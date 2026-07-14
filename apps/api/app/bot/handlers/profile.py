"""Profile, settings, language handlers"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.services.user import UserService
from app.db.session import async_session_maker

router = Router(name="profile")


@router.message(Command("profile"))
async def cmd_profile(message: Message, user):
    await show_profile(message, user)


@router.callback_query(F.data == "my_profile")
async def cb_my_profile(call: CallbackQuery, user):
    await show_profile(call.message, user, edit=False)
    await call.answer()


async def show_profile(message: Message, user, edit: bool = False):
    premium_tag = "💎 Premium" if user.is_premium else ""
    text = f"""
👤 <b>{user.nickname or 'Anonim'}</b> {premium_tag}
🆔 <code>{user.public_id}</code>
"""

    if user.birth_date:
        from datetime import date
        age = date.today().year - user.birth_date.year
        text += f"🎂 {age} yosh\n"
    if user.region or user.city:
        text += f"📍 {[user.city, user.region].filter(None) if False else (user.city or user.region or '')}\n"
    if user.bio:
        text += f"\n💭 {user.bio}\n"
    if user.interests:
        text += f"\n🏷️ {', '.join(user.interests[:5])}\n"

    text += f"\n📊 Yoqtirishlar: {user.likes_sent}\n"
    text += f"💕 Matchlar: {user.match_count}\n"
    text += f"👁 Ko'rishlar: {user.profile_views}\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Tahrirlash", web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}/profile/edit"))],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")],
    ])
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "settings")
async def cb_settings(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🌙 Tema: Qorong'i", callback_data="theme_dark")],
        [InlineKeyboardButton(text="🔔 Bildirishnomalar", callback_data="notif_settings")],
        [InlineKeyboardButton(text="❌ Yopish", callback_data="close")],
    ])
    await call.message.answer("⚙️ <b>Sozlamalar</b>\n\nTil va mavzuni tanlang:", reply_markup=kb)
    await call.answer()


@router.callback_query(F.data.startswith("lang_"))
async def cb_lang(call: CallbackQuery, user):
    lang = call.data.split("_")[1]
    async with async_session_maker() as session:
        await UserService.update_language(session, user, lang)
    langs = {"uz": "O'zbek", "ru": "Русский", "en": "English"}
    await call.answer(f"✅ Til: {langs.get(lang, lang)}")
    await call.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data == "close")
async def cb_close(call: CallbackQuery):
    await call.message.delete()
    await call.answer()


from aiogram.types import WebAppInfo
from app.core.config import settings
