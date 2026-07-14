"""Admin bot commands"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.core.config import settings
from app.db.session import async_session_maker
from sqlalchemy import text

router = Router(name="admin")


def is_admin(telegram_id: int) -> bool:
    return telegram_id in settings.ADMIN_TELEGRAM_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("""
🛡️ <b>Admin Panel</b>

/stats — Umumiy statistika
/users — Faol foydalanuvchilar
/broadcast [text] — Hammaga xabar
/ban [user_id] — Bloklash
/unban [user_id] — Blokdan olish
/reports — Yangi reportlar
/health — Tizim holati
""")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    async with async_session_maker() as session:
        users = (await session.execute(text("SELECT COUNT(*) FROM users"))).scalar()
        online = (await session.execute(text("SELECT COUNT(*) FROM users WHERE last_seen > NOW() - INTERVAL '5 minutes'"))).scalar()
        new_today = (await session.execute(text("SELECT COUNT(*) FROM users WHERE created_at::date = CURRENT_DATE"))).scalar()
        matches = (await session.execute(text("SELECT COUNT(*) FROM matches"))).scalar()
        messages = (await session.execute(text("SELECT COUNT(*) FROM messages"))).scalar()
        premium = (await session.execute(text("SELECT COUNT(*) FROM premium WHERE expires_at > NOW()"))).scalar()
        reports = (await session.execute(text("SELECT COUNT(*) FROM reports WHERE status = 'pending'"))).scalar()
    await message.answer(f"""
📊 <b>Statistika</b>

👥 Foydalanuvchilar: {users}
🟢 Online: {online}
🆕 Bugun yangi: {new_today}
💕 Matchlar: {matches}
💬 Xabarlar: {messages}
💎 Premium: {premium}
🚨 Reportlar: {reports}
""")


@router.message(Command("health"))
async def cmd_health(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        from app.core.redis import redis_client
        await redis_client.ping()
        await message.answer("✅ <b>Tizim sog'lom</b>\n\nDB: OK\nRedis: OK")
    except Exception as e:
        await message.answer(f"❌ <b>Xatolik:</b> {e}")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if not is_admin(message.from_user.id):
        return
    text_to_send = message.text.replace("/broadcast", "").strip()
    if not text_to_send:
        await message.answer("❌ Matn kiriting: /broadcast [matn]")
        return

    async with async_session_maker() as session:
        result = await session.execute(text("SELECT telegram_id FROM users WHERE telegram_id IS NOT NULL"))
        user_ids = [row[0] for row in result.fetchall()]

    sent = 0
    failed = 0
    for uid in user_ids:
        try:
            await message.bot.send_message(uid, text_to_send)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(f"📢 Broadcast tugadi\n✅ Yuborildi: {sent}\n❌ Xato: {failed}")


@router.message(Command("ban"))
async def cmd_ban(message: Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Foydalanish: /ban [telegram_id]")
        return
    try:
        tid = int(args[1])
        async with async_session_maker() as session:
            await session.execute(text("UPDATE users SET is_banned = TRUE, banned_at = NOW() WHERE telegram_id = :tid"), {"tid": tid})
            await session.commit()
        await message.answer(f"🚫 {tid} bloklandi")
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")
