"""Discover, swipe, match handlers"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from app.services.discover import DiscoverService
from app.services.notification import NotificationService
from app.db.session import async_session_maker
from app.core.config import settings

router = Router(name="discover")


@router.message(Command("discover"))
async def cmd_discover(message: Message, user):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Kashf qilish", web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}/discover"))],
    ])
    await message.answer(
        "🔍 Yangi odamlarni kashf qiling!\n\n"
        "👆 Yuqoridagi tugma orqali WebApp oching va yoqtirganlaringizni tanlang.",
        reply_markup=kb,
    )


@router.message(Command("matches"))
async def cmd_matches(message: Message, user):
    async with async_session_maker() as session:
        matches = await DiscoverService.get_matches(session, user.id, limit=20)

    if not matches:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Boshlash", web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}/discover"))],
        ])
        await message.answer("💔 Hali matchlaringiz yo'q. Boshlash uchun bosing!", reply_markup=kb)
        return

    text = f"💕 <b>Matchlaringiz ({len(matches)})</b>\n\n"
    kb_rows = []
    for m in matches[:10]:
        text += f"• {m.other_user_nickname}\n"
        kb_rows.append([InlineKeyboardButton(text=f"💬 {m.other_user_nickname}", web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}/chat/{m.id}"))])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("view_profile_"))
async def cb_view_profile(call: CallbackQuery, user):
    target_id = int(call.data.split("_")[2])
    async with async_session_maker() as session:
        profile = await DiscoverService.get_profile(session, target_id, viewer_id=user.id)
    if not profile:
        await call.answer("❌ Profil topilmadi", show_alert=True)
        return

    text = f"""
<b>{profile.nickname}</b>, {profile.age}
📍 {profile.city or profile.region or 'Noma\'lum'}
"""
    if profile.bio:
        text += f"\n💭 {profile.bio}\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❤️ Yoqtirish", callback_data=f"like_{profile.user_id}"),
         InlineKeyboardButton(text="❌ O'tkazib yuborish", callback_data=f"pass_{profile.user_id}")],
        [InlineKeyboardButton(text="⭐ Super Like", callback_data=f"superlike_{profile.user_id}")],
    ])
    await call.message.answer(text, reply_markup=kb)
    await call.answer()


@router.callback_query(F.data.startswith("like_"))
async def cb_like(call: CallbackQuery, user):
    target_id = int(call.data.split("_")[1])
    async with async_session_maker() as session:
        result = await DiscoverService.swipe(session, user.id, target_id, "like")

    if result.get("is_match"):
        # Send match notification
        await NotificationService.send_match_notification(session, user.id, target_id)
        await call.message.answer(f"🎉 <b>MATCH!</b>\n\nYozishni boshlang! 💬")
    else:
        await call.answer("❤️ Yoqtirildi", show_alert=False)
    await call.answer()


@router.callback_query(F.data.startswith("pass_"))
async def cb_pass(call: CallbackQuery, user):
    target_id = int(call.data.split("_")[1])
    async with async_session_maker() as session:
        await DiscoverService.swipe(session, user.id, target_id, "pass")
    await call.answer("O'tkazib yuborildi")


@router.callback_query(F.data.startswith("superlike_"))
async def cb_superlike(call: CallbackQuery, user):
    target_id = int(call.data.split("_")[1])
    async with async_session_maker() as session:
        if not user.is_premium:
            await call.answer("⭐ Super Like faqat Premium uchun!", show_alert=True)
            return
        result = await DiscoverService.swipe(session, user.id, target_id, "superlike")
    if result.get("is_match"):
        await call.message.answer(f"🎉 <b>SUPER MATCH!</b>\n")
    else:
        await call.answer("⭐ Super Like yuborildi!")
