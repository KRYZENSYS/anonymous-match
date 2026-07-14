"""Chat features endpoints - stickers, themes, reactions, scheduled, polls, pinned, saved"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.core.deps import get_current_user, get_session
from app.models.user import User
from app.models.chat_features import (
    StickerPack, Sticker, UserStickerPack, MessageReaction,
    ChatTheme, UserChatTheme, ScheduledMessage, Poll, PollVote,
    PinnedMessage, SavedMessage, ForwardedMessage,
)
from app.models.chat import Message

router = APIRouter(prefix="/chat-features", tags=["chat-features"])


# ===== Stickers =====
@router.get("/stickers/packs")
async def list_sticker_packs(session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(StickerPack).order_by(StickerPack.is_free.desc(), StickerPack.id))
    return [{"id": p.id, "name": p.name, "description": p.description, "cover_url": p.cover_url, "category": p.category, "price_coins": p.price_coins, "is_free": p.is_free, "is_animated": p.is_animated, "sticker_count": p.sticker_count, "downloads": p.downloads} for p in r.scalars().all()]


@router.get("/stickers/packs/{pack_id}")
async def get_sticker_pack(pack_id: int, session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(Sticker).where(Sticker.pack_id == pack_id).order_by(Sticker.order))
    return [{"id": s.id, "emoji": s.emoji, "image_url": s.image_url} for s in r.scalars().all()]


@router.post("/stickers/packs/{pack_id}/install")
async def install_sticker_pack(pack_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(UserStickerPack).where(UserStickerPack.user_id == current_user.id, UserStickerPack.pack_id == pack_id))
    if r.scalar_one_or_none():
        return {"ok": True, "already_installed": True}
    session.add(UserStickerPack(user_id=current_user.id, pack_id=pack_id))
    p = await session.get(StickerPack, pack_id)
    if p:
        p.downloads = (p.downloads or 0) + 1
    await session.commit()
    return {"ok": True}


@router.get("/stickers/installed")
async def my_sticker_packs(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(StickerPack, UserStickerPack).join(UserStickerPack, UserStickerPack.pack_id == StickerPack.id).where(UserStickerPack.user_id == current_user.id))
    return [{"id": p.id, "name": p.name, "cover_url": p.cover_url, "is_animated": p.is_animated, "sticker_count": p.sticker_count} for p, _ in r.all()]


# ===== Themes =====
@router.get("/themes")
async def list_chat_themes(session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(ChatTheme).order_by(ChatTheme.is_free.desc()))
    return [{"id": t.id, "name": t.name, "code": t.code, "preview_url": t.preview_url, "background_url": t.background_url, "price_coins": t.price_coins, "is_free": t.is_free, "is_seasonal": t.is_seasonal} for t in r.scalars().all()]


@router.post("/themes/{theme_id}/apply")
async def apply_chat_theme(theme_id: int, chat_id: int = None, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(UserChatTheme).where(UserChatTheme.user_id == current_user.id, UserChatTheme.chat_id == chat_id if chat_id else UserChatTheme.chat_id.is_(None)))
    existing = r.scalar_one_or_none()
    if existing:
        existing.theme_id = theme_id
    else:
        session.add(UserChatTheme(user_id=current_user.id, theme_id=theme_id, chat_id=chat_id, is_active=True))
    await session.commit()
    return {"ok": True}


# ===== Message Reactions =====
@router.post("/messages/{message_id}/react")
async def react_to_message(message_id: int, emoji: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(MessageReaction).where(MessageReaction.message_id == message_id, MessageReaction.user_id == current_user.id, MessageReaction.emoji == emoji))
    if r.scalar_one_or_none():
        return {"ok": True, "already_reacted": True}
    session.add(MessageReaction(message_id=message_id, user_id=current_user.id, emoji=emoji))
    await session.commit()
    return {"ok": True}


@router.delete("/messages/{message_id}/react")
async def remove_reaction(message_id: int, emoji: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(MessageReaction).where(MessageReaction.message_id == message_id, MessageReaction.user_id == current_user.id, MessageReaction.emoji == emoji))
    rx = r.scalar_one_or_none()
    if rx:
        await session.delete(rx)
        await session.commit()
    return {"ok": True}


@router.get("/messages/{message_id}/reactions")
async def get_reactions(message_id: int, session: AsyncSession = Depends(get_session)):
    from sqlalchemy import func
    r = await session.execute(select(MessageReaction.emoji, func.count(MessageReaction.id).label("count")).where(MessageReaction.message_id == message_id).group_by(MessageReaction.emoji))
    return [{"emoji": e, "count": c} for e, c in r.all()]


# ===== Scheduled Messages =====
@router.post("/schedule")
async def schedule_message(chat_id: int, content: str, send_at: str, type: str = "text", media_url: str = None, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    sm = ScheduledMessage(chat_id=chat_id, sender_id=current_user.id, type=type, content=content, media_url=media_url, send_at=datetime.fromisoformat(send_at))
    session.add(sm)
    await session.commit()
    return {"id": sm.id, "send_at": sm.send_at}


@router.get("/scheduled")
async def my_scheduled(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(ScheduledMessage).where(ScheduledMessage.sender_id == current_user.id, ScheduledMessage.is_sent == False).order_by(ScheduledMessage.send_at))
    return [{"id": s.id, "chat_id": s.chat_id, "content": s.content, "send_at": s.send_at} for s in r.scalars().all()]


@router.delete("/scheduled/{schedule_id}")
async def cancel_scheduled(schedule_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    s = await session.get(ScheduledMessage, schedule_id)
    if not s or s.sender_id != current_user.id:
        raise HTTPException(403, "Not allowed")
    await session.delete(s)
    await session.commit()
    return {"ok": True}


# ===== Polls =====
@router.post("/polls")
async def create_poll(chat_id: int, question: str, options: list[str], is_multi: bool = False, expires_at: str = None, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    p = Poll(chat_id=chat_id, creator_id=current_user.id, question=question, options=options, is_multi=is_multi, expires_at=datetime.fromisoformat(expires_at) if expires_at else None)
    session.add(p)
    await session.commit()
    return {"id": p.id, "options": options}


@router.post("/polls/{poll_id}/vote")
async def vote_poll(poll_id: int, option_indices: list[int], current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    for idx in option_indices:
        session.add(PollVote(poll_id=poll_id, user_id=current_user.id, option_index=idx))
    await session.commit()
    return {"ok": True}


@router.get("/polls/{poll_id}/results")
async def poll_results(poll_id: int, session: AsyncSession = Depends(get_session)):
    from sqlalchemy import func
    p = await session.get(Poll, poll_id)
    if not p:
        raise HTTPException(404)
    r = await session.execute(select(PollVote.option_index, func.count(PollVote.id).label("count")).where(PollVote.poll_id == poll_id).group_by(PollVote.option_index))
    votes = {idx: count for idx, count in r.all()}
    return {"question": p.question, "options": p.options, "votes": votes, "is_multi": p.is_multi}


# ===== Pinned Messages =====
@router.post("/chats/{chat_id}/pin/{message_id}")
async def pin_message(chat_id: int, message_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    session.add(PinnedMessage(chat_id=chat_id, message_id=message_id, pinned_by=current_user.id))
    await session.commit()
    return {"ok": True}


@router.get("/chats/{chat_id}/pinned")
async def get_pinned(chat_id: int, session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(PinnedMessage, Message).join(Message, Message.id == PinnedMessage.message_id).where(PinnedMessage.chat_id == chat_id).order_by(PinnedMessage.pinned_at.desc()))
    return [{"id": pm.id, "message_id": m.id, "content": m.content, "type": m.type, "sender_id": m.sender_id, "pinned_at": pm.pinned_at} for pm, m in r.all()]


# ===== Saved Messages =====
@router.post("/messages/{message_id}/save")
async def save_message(message_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    session.add(SavedMessage(user_id=current_user.id, message_id=message_id))
    await session.commit()
    return {"ok": True}


@router.get("/saved")
async def my_saved(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(SavedMessage, Message).join(Message, Message.id == SavedMessage.message_id).where(SavedMessage.user_id == current_user.id).order_by(SavedMessage.saved_at.desc()))
    return [{"id": s.id, "message_id": m.id, "content": m.content, "type": m.type, "saved_at": s.saved_at} for s, m in r.all()]
