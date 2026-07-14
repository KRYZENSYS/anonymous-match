"""New bot handlers - inline mode, AI assistant, daily matches, gamification, admin broadcast, support"""
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import json

from app.models.user import User
from app.models.swipe import Match
from app.models.gamification import Achievement, UserAchievement, CoinTransaction
from app.models.seasonal import SeasonalEvent
from app.services.ai import AIService
from app.services.gamification import GamificationService
from app.services.notifications import NotificationService
from app.services.safety import SafetyService
from app.core.config import settings
from app.db.session import get_session

router = Router(name="new_handlers")


class SupportState(StatesGroup):
    waiting_message = State()
    waiting_response = State()


# === Inline Mode ===
@router.inline_query()
async def inline_handler(query: types.InlineQuery):
    """Handle inline queries @bot match, etc."""
    text = query.query.lower().strip()
    results = []
    if "match" in text or "find" in text or text == "":
        results.append(types.InlineQueryResultArticle(
            id="1",
            title="Yangi odamlar topish",
            description="Telegram orqali anonim tanishuvni boshlang",
            input_message_content=types.InputTextMessageContent(
                message_text="🌹 Anonymous Match botidan foydalanib ko'ring!\n\n👉 @AnonymousMatchBot"
            ),
        ))
        results.append(types.InlineQueryResultArticle(
            id="2",
            title="Profilim",
            description="Profilingizni ko'rish",
            input_message_content=types.InputTextMessageContent(
                message_text="💕 Mening profilim: https://anonymous-match.uz/profile"
            ),
        ))
    if "premium" in text or "vip" in text:
        results.append(types.InlineQueryResultArticle(
            id="3",
            title="Premium obuna",
            description="VIP imkoniyatlarga ega bo'ling",
            input_message_content=types.InputTextMessageContent(
                message_text="👑 Premium: https://anonymous-match.uz/premium"
            ),
        ))
    await query.answer(results, cache_time=60, is_personal=True)


# === AI Assistant - First Message Suggestion ===
@router.message(Command("icebreaker"))
async def cmd_icebreaker(message: types.Message, session: AsyncSession):
    """Generate icebreaker for last match"""
    user = await _get_user(session, message.from_user.id)
    if not user:
        return await message.answer("❌ Avval ro'yxatdan o'ting: /start")
    r = await session.execute(select(Match).where((Match.user1_id == user.id) | (Match.user2_id == user.id)).order_by(Match.created_at.desc()).limit(1))
    m = r.scalar_one_or_none()
    if not m:
        return await message.answer("❌ Hali matchingiz yo'q")
    other_id = m.user2_id if m.user1_id == user.id else m.user1_id
    other = await session.get(User, other_id)
    starter = await AIService.generate_icebreaker(other, user.language_code or "uz")
    await message.answer(f"💡 Yangi xabar g'oyasi:\n\n<i>{starter}</i>\n\n👤 {other.nickname or 'Match'}")


# === Daily Match Notification ===
@router.message(Command("daily"))
async def cmd_daily(message: types.Message, session: AsyncSession):
    """Show daily matches"""
    user = await _get_user(session, message.from_user.id)
    if not user:
        return await message.answer("❌ Avval /start")
    await message.answer("🔍 Sizning kunlik tavsiyalaringiz qidirilmoqda...")
    recs = await AIService.ai_matchmaking(session, user, 5)
    if not recs:
        return await message.answer("😔 Hozircha mos odamlar topilmadi. Keyinroq urinib ko'ring.")
    text = "🌹 <b>Bugungi tavsiyalar:</b>\n\n"
    for i, r in enumerate(recs, 1):
        text += f"{i}. <b>{r['nickname']}</b>, {r.get('age', '?')}\n"
        text += f"   📊 Moslik: {r['match_score']}%\n"
        if r.get('is_verified'):
            text += "   ✅ Tasdiqlangan\n"
        text += "\n"
    text += "👀 Batafsil ko'rish: @AnonymousMatchBot"
    await message.answer(text)


# === Achievements ===
@router.message(Command("achievements"))
async def cmd_achievements(message: types.Message, session: AsyncSession):
    user = await _get_user(session, message.from_user.id)
    if not user:
        return await message.answer("❌ Avval /start")
    r = await session.execute(select(Achievement).order_by(Achievement.tier).limit(10))
    achievements = r.scalars().all()
    r2 = await session.execute(select(UserAchievement).where(UserAchievement.user_id == user.id))
    user_ach = {ua.achievement_id: ua for ua in r2.scalars().all()}
    text = "🏆 <b>Sizning yutuqlaringiz:</b>\n\n"
    unlocked = sum(1 for a in achievements if a.id in user_ach and user_ach[a.id].unlocked_at)
    text += f"📊 Jami: {unlocked}/{len(achievements)} ta\n\n"
    for a in achievements[:8]:
        is_unlocked = a.id in user_ach and user_ach[a.id].unlocked_at
        text += f"{a.icon} <b>{a.name}</b>\n"
        text += f"   {a.description}\n"
        if is_unlocked:
            text += "   ✅ Qo'lga kiritilgan\n"
        else:
            text += f"   🔒 Progress: {user_ach[a.id].progress if a.id in user_ach else 0}/{a.condition_value}\n"
        text += "\n"
    text += "💰 Mukofot: har bir yutuq uchun tangalar!"
    await message.answer(text)


# === Daily Streak ===
@router.message(Command("streak"))
async def cmd_streak(message: types.Message, session: AsyncSession):
    user = await _get_user(session, message.from_user.id)
    if not user:
        return await message.answer("❌ Avval /start")
    coins = await GamificationService.update_streak(session, user)
    from app.models.gamification import Streak
    r = await session.execute(select(Streak).where(Streak.user_id == user.id))
    streak = r.scalar_one_or_none()
    if not streak:
        return await message.answer("❌ Xatolik yuz berdi")
    text = f"🔥 <b>Streak:</b> {streak.current_streak} kun\n"
    text += f"📅 Eng uzun: {streak.longest_streak} kun\n"
    text += f"📊 Jami loginlar: {streak.total_logins}\n\n"
    if coins > 0:
        text += f"💰 Bugun +{coins} tanga qo'shildi!"
    else:
        text += "✅ Bugun allaqachon tizimga kirgansiz. Ertaga qayting!"
    await message.answer(text)


# === Coin Balance ===
@router.message(Command("coins"))
async def cmd_coins(message: types.Message, session: AsyncSession):
    user = await _get_user(session, message.from_user.id)
    if not user:
        return await message.answer("❌ Avval /start")
    balance = await GamificationService.get_coin_balance(session, user.id)
    text = f"💰 <b>Coin Balance:</b> {balance} tanga\n\n"
    text += "Tanga olish usullari:\n"
    text += "• 🔥 Kunlik streak: +10-100 tanga\n"
    text += "• 💕 Match: +5 tanga\n"
    text += "• 💬 Xabar: +1 tanga\n"
    text += "• 🏆 Yutuq: 10-10000 tanga\n"
    text += "• 📅 Missiyalar: 10-100 tanga\n\n"
    text += "Tanga sarflash:\n"
    text += "• ⭐ Super Like: 5 tanga\n"
    text += "• 🚀 Boost: 50 tanga\n"
    text += "• 🎁 Sovg'a: 10-1000 tanga\n"
    text += "• 💎 Premium: tanga bilan"
    await message.answer(text)


# === Profile Completeness ===
@router.message(Command("profile"))
async def cmd_profile(message: types.Message, session: AsyncSession):
    user = await _get_user(session, message.from_user.id)
    if not user:
        return await message.answer("❌ Avval /start")
    score = await SafetyService.calculate_profile_completeness(user)
    text = f"📊 <b>Profil to'liqligi:</b> {score}%\n\n"
    missing = []
    if not user.nickname: missing.append("📝 Ism qo'ying")
    if not user.bio: missing.append("✍️ Bio yozing")
    if not user.photos or len(user.photos) < 3: missing.append(f"📸 {3 - len(user.photos or [])} ta rasm qo'shing")
    if not user.age: missing.append("🎂 Yosh ko'rsating")
    if not user.city: missing.append("📍 Shahar ko'rsating")
    if not user.interests: missing.append("❤️ Qiziqishlar qo'shing")
    if not user.is_verified: missing.append("✅ Rasmlarni tasdiqlang")
    if missing:
        text += "<b>Yaxshilash uchun:</b>\n"
        for m in missing[:5]:
            text += f"• {m}\n"
        text += f"\n💡 To'liq profil = ko'proq match!"
    else:
        text += "✅ Ajoyib! Profilingiz to'liq."
    await message.answer(text)


# === Spin Wheel ===
@router.message(Command("spin"))
async def cmd_spin(message: types.Message, session: AsyncSession):
    user = await _get_user(session, message.from_user.id)
    if not user:
        return await message.answer("❌ Avval /start")
    from app.models.gamification import SpinReward
    from datetime import timedelta
    from sqlalchemy import desc as d
    r = await session.execute(select(SpinReward).where(SpinReward.user_id == user.id).order_by(d(SpinReward.created_at)).limit(1))
    last = r.scalar_one_or_none()
    if last and last.created_at > datetime.utcnow() - timedelta(hours=1):
        remaining = 3600 - int((datetime.utcnow() - last.created_at).total_seconds())
        mins = remaining // 60
        return await message.answer(f"⏰ Keyingi spin: {mins} daqiqadan so'ng")
    import random
    rewards = [(10, "🪙 10 tanga"), (20, "🪙 20 tanga"), (50, "🪙 50 tanga"), (1, "⭐ 1 Super Like"), (200, "🪙 200 tanga! 🎉"), (100, "🪙 100 tanga")]
    value, text = random.choice(rewards)
    is_coins = "tanga" in text
    session.add(SpinReward(user_id=user.id, reward_type="coins" if is_coins else "superlike", reward_value=value))
    if is_coins:
        session.add(CoinTransaction(user_id=user.id, amount=value, type="earned", reason="Spin wheel"))
    await session.commit()
    await message.answer(f"🎰 <b>Spin natijasi:</b>\n\n{text}\n\n💡 1 soatdan keyin yana urinib ko'ring!")


# === Seasonal Events ===
@router.message(Command("events"))
async def cmd_events(message: types.Message, session: AsyncSession):
    from app.services.seasons import SeasonService
    events = await SeasonService.get_active_seasons(session)
    if not events:
        return await message.answer("📅 Hozir faol tadbirlar yo'q")
    text = "🎉 <b>Faol tadbirlar:</b>\n\n"
    for e in events:
        text += f"{e.icon} <b>{e.name}</b>\n"
        text += f"   {e.description}\n"
        text += f"   💰 Bonus: x{e.bonus_multiplier}\n\n"
    text += "👀 Bot ichida qatnashing!"
    await message.answer(text)


# === Safety Report ===
@router.message(Command("report"))
async def cmd_report(message: types.Message, session: AsyncSession):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.answer("❌ Foydalanish: /report [sabab]\n\nMasalan: /report Spam yuboradi")
    reason = args[1]
    user = await _get_user(session, message.from_user.id)
    if not user:
        return await message.answer("❌ Avval /start")
    await message.answer("✅ Xabar qabul qilindi. Tekshirib ko'ramiz.\n\n⚠️ Soxta xabar uchun siz ham bloklanishingiz mumkin.")


# === Support / Contact ===
@router.message(Command("support"))
async def cmd_support(message: types.Message, state: FSMContext):
    await state.set_state(SupportState.waiting_message)
    await message.answer("📩 Yordam kerakmi? Xabaringizni yozing:")


@router.message(SupportState.waiting_message)
async def support_message(message: types.Message, state: FSMContext, session: AsyncSession):
    user = await _get_user(session, message.from_user.id)
    # Forward to admin
    admin_id = settings.ADMIN_IDS[0] if settings.ADMIN_IDS else None
    if admin_id:
        try:
            await message.bot.send_message(
                admin_id,
                f"📩 Yangi support xabari\n\n👤 User: {message.from_user.id}\n📛 Name: {message.from_user.full_name}\n\n{message.text}",
            )
        except Exception:
            pass
    await message.answer("✅ Xabaringiz yuborildi! Tez orada javob beramiz.")
    await state.clear()


# === Bot Info / Help ===
@router.message(Command("help"))
async def cmd_help(message: types.Message):
    text = """🤖 <b>Anonymous Match Bot</b>

<b>Asosiy buyruqlar:</b>
/start - Botni boshlash
/profile - Profilingiz
/daily - Bugungi tavsiyalar
/icebreaker - Yangi xabar g'oyasi
/achievements - Yutuqlar
/streak - Kunlik streak
/coins - Tanga balansi
/spin - Spin wheel
/events - Tadbirla
/report - Shikoyat
/support - Yordam
/help - Yordam

<b>Imkoniyatlar:</b>
💕 Tinder-style swipe
💬 Real-time chat
⭐ Super Like
🔥 Boost
🎁 Virtual sovg'alar
📹 Video qo'ng'iroq
🎤 Ovozli xabar
🌹 Story/Reels
🏆 Gamification
🎉 Maxsus tadbirlar

📱 Mini App: @AnonymousMatchBot"""
    await message.answer(text)


# === Referral ===
@router.message(Command("referral"))
async def cmd_referral(message: types.Message, session: AsyncSession):
    user = await _get_user(session, message.from_user.id)
    if not user:
        return await message.answer("❌ Avval /start")
    import secrets
    if not user.referral_code:
        user.referral_code = f"AM{user.id}{secrets.token_hex(3).upper()}"
        await session.commit()
    text = f"""🎁 <b>Referal dasturi</b>

Sizning kodingiz: <code>{user.referral_code}</code>

📤 Do'stlaringizga yuboring:
https://t.me/AnonymousMatchBot?start=ref_{user.referral_code}

<b>Mukofotlar:</b>
• Siz: +500 tanga
• Do'st: +300 tanga

💡 Cheksiz do'st taklif qiling!"""
    await message.answer(text)


# === Privacy / Delete Account ===
@router.message(Command("delete_account"))
async def cmd_delete_account(message: types.Message, session: AsyncSession):
    user = await _get_user(session, message.from_user.id)
    if not user:
        return await message.answer("❌ Avval /start")
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data="confirm_delete")],
        [types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_delete")],
    ])
    await message.answer("⚠️ Hisobingizni o'chirishni xohlaysizmi?\n\nBu amalni qaytarib bo'lmaydi!", reply_markup=kb)


@router.callback_query(F.data == "confirm_delete")
async def confirm_delete(callback: types.CallbackQuery, session: AsyncSession):
    user = await _get_user(session, callback.from_user.id)
    if user:
        user.is_active = False
        user.is_deleted = True
        await session.commit()
    await callback.message.edit_text("✅ Hisobingiz o'chirildi. Xayr! 👋")
    await callback.answer()


@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: types.CallbackQuery):
    await callback.message.edit_text("✅ Bekor qilindi.")
    await callback.answer()


async def _get_user(session: AsyncSession, telegram_id: int) -> User:
    r = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return r.scalar_one_or_none()
