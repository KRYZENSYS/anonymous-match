"""Chats router."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models import User
from app.schemas.chat import (
    MessageCreate, MessageUpdate,
    MessagePublic, MessageListResponse,
    ChatListResponse, ChatPublic,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.get("", response_model=ChatListResponse)
async def list_chats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Mening chatlarim."""
    chats = await ChatService.get_user_chats(db, user)
    return ChatListResponse(
        chats=[ChatPublic(**c) for c in chats],
        total=len(chats),
        has_more=False,
    )


@router.post("/{other_user_id}")
async def create_or_get_chat(
    other_user_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Foydalanuvchi bilan chat yaratish yoki olish."""
    try:
        chat = await ChatService.get_or_create_chat(db, user, other_user_id)
        return {"chat_id": chat.id, "success": True}
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.get("/{chat_id}/messages", response_model=MessageListResponse)
async def get_messages(
    chat_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=200),
    before: Optional[datetime] = Query(None),
):
    """Chat xabarlari."""
    try:
        messages = await ChatService.get_messages(db, user, chat_id, limit, before)
        # O'qilgan deb belgilash
        await ChatService.mark_as_read(db, user, chat_id)
        return MessageListResponse(
            messages=messages,
            total=len(messages),
            has_more=len(messages) == limit,
            next_cursor=messages[0].created_at if messages else None,
        )
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))


@router.post("/{chat_id}/messages", response_model=MessagePublic)
async def send_message(
    chat_id: int,
    data: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Yangi xabar yuborish."""
    try:
        msg = await ChatService.send_message(db, user, chat_id, data)
        return MessagePublic(
            id=msg.id, chat_id=msg.chat_id, sender_id=msg.sender_id,
            sender_public_id=user.public_id, type=msg.type,
            content=msg.content, media=None, reply_to=None,
            is_edited=msg.is_edited, is_deleted=msg.is_deleted,
            is_mine=True, read_at=msg.read_at, delivered_at=msg.delivered_at,
            created_at=msg.created_at,
        )
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.post("/{chat_id}/read")
async def mark_read(
    chat_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Xabarlarni o'qilgan deb belgilash."""
    count = await ChatService.mark_as_read(db, user, chat_id)
    return {"success": True, "marked_count": count}


@router.post("/{chat_id}/typing")
async def typing(
    chat_id: int,
    is_typing: bool,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Typing indicator."""
    await ChatService.set_typing(db, user, chat_id, is_typing)
    return {"success": True}


@router.patch("/messages/{message_id}", response_model=MessagePublic)
async def edit_message(
    message_id: int,
    data: MessageUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Xabarni tahrirlash."""
    try:
        msg = await ChatService.edit_message(db, user, message_id, data)
        return MessagePublic(
            id=msg.id, chat_id=msg.chat_id, sender_id=msg.sender_id,
            sender_public_id=user.public_id, type=msg.type,
            content=msg.content, media=None, reply_to=None,
            is_edited=msg.is_edited, is_deleted=msg.is_deleted,
            is_mine=True, read_at=msg.read_at, delivered_at=msg.delivered_at,
            created_at=msg.created_at,
        )
    except (ValueError, PermissionError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    for_everyone: bool = False,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Xabarni o'chirish."""
    try:
        success = await ChatService.delete_message(db, user, message_id, for_everyone)
        return {"success": success}
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
