"""Chat handlers (bot side notification only)"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from app.db.session import async_session_maker
from app.core.config import settings

router = Router(name="chat")


@router.message(Command("chats"))
async def cmd_chats(message: Message, user):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Chatlarni ochish", web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}/chats"))],
    ])
    await message.answer("💬 Barcha chatlaringiz WebApp'da", reply_markup=kb)


@router.callback_query(F.data == "open_chats")
async def cb_open_chats(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ochish", web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}/chats"))],
    ]))
    await call.answer()
