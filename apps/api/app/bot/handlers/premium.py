"""Premium subscription handlers with Telegram Stars"""
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from app.services.premium import PremiumService
from app.db.session import async_session_maker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = Router(name="premium")


PREMIUM_PLANS = [
    {"tier": "plus", "name": "Plus", "stars": 500, "days": 30},
    {"tier": "gold", "name": "Gold", "stars": 1200, "days": 30},
    {"tier": "platinum", "name": "Platinum", "stars": 2500, "days": 30},
]


@router.message(Command("premium"))
async def cmd_premium(message: Message, user, bot: Bot):
    async with async_session_maker() as session:
        status = await PremiumService.get_status(session, user.id)

    text = f"""
💎 <b>Anonymous Match Premium</b>

Hozirgi holat: <b>{'Premium ✅' if status['is_premium'] else 'Oddiy'}</b>
"""
    if status['is_premium']:
        text += f"Tarif: {status['tier'].upper()}\n"
        text += f"Qolgan: {status['days_left']} kun\n"
        text += f"Boosts: {status['boost_count']}\n"

    text += "\n<b>Tariflar:</b>\n"
    kb_rows = []
    for plan in PREMIUM_PLANS:
        text += f"💫 {plan['name']} — <b>{plan['stars']} ⭐</b> ({plan['days']} kun)\n"
        kb_rows.append([InlineKeyboardButton(text=f"{plan['name']} — {plan['stars']}⭐", callback_data=f"buy_{plan['tier']}")])

    text += "\n⚡ Boost — har oyda 1 marta bepul"

    kb_rows.append([InlineKeyboardButton(text="⚡ Boost (30 daq)", callback_data="use_boost")])
    kb_rows.append([InlineKeyboardButton(text="🌐 WebApp'da ochish", web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}/premium"))])

    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))


@router.callback_query(F.data.startswith("buy_"))
async def cb_buy(call: CallbackQuery, user, bot: Bot):
    tier = call.data.split("_")[1]
    plan = next((p for p in PREMIUM_PLANS if p["tier"] == tier), None)
    if not plan:
        await call.answer("Tarif topilmadi", show_alert=True)
        return

    # Send invoice via Telegram Stars
    await bot.send_invoice(
        chat_id=call.message.chat.id,
        title=f"Anonymous Match Premium — {plan['name']}",
        description=f"{plan['days']} kunlik Premium obuna",
        payload=f"premium_{plan['tier']}_{plan['days']}_{plan['stars']}",
        provider_token="",  # Empty for Telegram Stars
        currency="XTR",
        prices=[LabeledPrice(label=plan['name'], amount=plan['stars'])],
    )
    await call.answer()


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_payment(message: Message, user):
    payload = message.successful_payment.invoice_payload
    if not payload.startswith("premium_"):
        return
    parts = payload.split("_")
    tier, days, stars = parts[1], int(parts[2]), int(parts[3])
    payment_id = message.successful_payment.telegram_payment_charge_id

    async with async_session_maker() as session:
        result = await PremiumService.verify_and_activate(
            session, user.id, tier, days, stars, payment_id
        )

    if result.get("success"):
        await message.answer(f"✅ <b>Premium faollashtirildi!</b>\n\nTarif: {tier.upper()}\nMuddat: {days} kun\n\nEndi barcha imkoniyatlardan foydalaning! 💎")
    else:
        await message.answer("❌ To'lov tasdiqlanmadi. Support: @kryzen_support")


@router.callback_query(F.data == "use_boost")
async def cb_use_boost(call: CallbackQuery, user):
    async with async_session_maker() as session:
        result = await PremiumService.use_boost(session, user.id)
    if result.get("success"):
        await call.answer(f"⚡ Boost faollashtirildi! 30 daqiqa eng yuqorida bo'lasiz", show_alert=True)
    else:
        await call.answer(result.get("message", "Boost ishlamadi"), show_alert=True)


from aiogram.types import WebAppInfo
