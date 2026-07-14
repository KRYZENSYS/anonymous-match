"""Advanced endpoints - calls, AI matchmaking, photo scoring, translation, voice transcription"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from app.core.deps import get_current_user, get_session
from app.models.user import User
from app.models.advanced import (
    Call, PhotoScore, CompatibilityScore, TranslationCache,
    AIRecommendation, ConversationStarter, SentimentAnalysis,
    ChatInsight, ReferralProgram, ChatTranslation,
)
from app.services.ai import AIService
from app.services.media import MediaService

router = APIRouter(prefix="/advanced", tags=["advanced"])


# ===== Calls =====
@router.post("/calls/initiate")
async def initiate_call(chat_id: int, type: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    from app.models.chat import Chat
    chat = await session.get(Chat, chat_id)
    if not chat or current_user.id not in (chat.user1_id, chat.user2_id):
        raise HTTPException(403, "Access denied")
    callee_id = chat.user2_id if current_user.id == chat.user1_id else chat.user1_id
    channel = await AIService.create_call_channel(type)
    call = Call(chat_id=chat_id, caller_id=current_user.id, callee_id=callee_id, type=type, channel_name=channel, status="ringing")
    session.add(call)
    await session.commit()
    # Push to callee
    from app.core.redis import redis_client
    import json
    await redis_client.publish(f"user:{callee_id}", json.dumps({"type": "incoming_call", "data": {"call_id": call.id, "caller_id": current_user.id, "caller_name": current_user.nickname, "type": type, "channel": channel}}, default=str))
    return {"call_id": call.id, "channel": channel, "type": type}


@router.post("/calls/{call_id}/answer")
async def answer_call(call_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    c = await session.get(Call, call_id)
    if not c or c.callee_id != current_user.id:
        raise HTTPException(403)
    c.status = "ongoing"
    c.answered_at = datetime.utcnow()
    await session.commit()
    return {"ok": True}


@router.post("/calls/{call_id}/end")
async def end_call(call_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    c = await session.get(Call, call_id)
    if not c or current_user.id not in (c.caller_id, c.callee_id):
        raise HTTPException(403)
    c.status = "ended"
    c.ended_at = datetime.utcnow()
    if c.answered_at:
        c.duration = int((c.ended_at - c.answered_at).total_seconds())
    await session.commit()
    return {"duration": c.duration}


@router.get("/calls/history")
async def call_history(limit: int = 50, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    from sqlalchemy import or_, and_
    r = await session.execute(select(Call).where(or_(Call.caller_id == current_user.id, Call.callee_id == current_user.id)).order_by(Call.started_at.desc()).limit(limit))
    return [{"id": c.id, "type": c.type, "status": c.status, "duration": c.duration, "started_at": c.started_at, "ended_at": c.ended_at} for c in r.scalars().all()]


# ===== AI Matchmaking =====
@router.get("/ai/feed")
async def ai_feed(limit: int = 20, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    recs = await AIService.ai_matchmaking(session, current_user, limit)
    return recs


@router.get("/ai/compatibility/{target_id}")
async def compatibility(target_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    target = await session.get(User, target_id)
    if not target:
        raise HTTPException(404)
    score = await AIService.calculate_compatibility(session, current_user, target)
    return score


# ===== Photo AI Scoring =====
@router.post("/photo/score")
async def score_photo(photo_url: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    score = await AIService.score_photo(photo_url)
    ps = PhotoScore(user_id=current_user.id, photo_url=photo_url, ai_score=score)
    session.add(ps)
    # Check if best photo
    r = await session.execute(select(PhotoScore).where(PhotoScore.user_id == current_user.id).order_by(PhotoScore.ai_score.desc()))
    photos = r.scalars().all()
    if photos:
        for p in photos:
            p.is_best_photo = False
        photos[0].is_best_photo = True
    await session.commit()
    return {"score": score}


@router.get("/photo/best")
async def best_photo(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(PhotoScore).where(PhotoScore.user_id == current_user.id, PhotoScore.is_best_photo == True).limit(1))
    p = r.scalar_one_or_none()
    return {"url": p.photo_url if p else None, "score": p.ai_score if p else 0}


# ===== Translation =====
@router.post("/translate")
async def translate(text: str, source_lang: str, target_lang: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if source_lang == target_lang:
        return {"translated": text}
    r = await session.execute(select(TranslationCache).where(TranslationCache.source_text == text, TranslationCache.source_lang == source_lang, TranslationCache.target_lang == target_lang))
    cached = r.scalar_one_or_none()
    if cached:
        return {"translated": cached.translated_text, "cached": True}
    translated = await AIService.translate_text(text, source_lang, target_lang)
    session.add(TranslationCache(source_text=text, source_lang=source_lang, target_lang=target_lang, translated_text=translated))
    await session.commit()
    return {"translated": translated, "cached": False}


@router.post("/chats/{chat_id}/translate")
async def enable_chat_translation(chat_id: int, target_lang: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(ChatTranslation).where(ChatTranslation.user_id == current_user.id, ChatTranslation.chat_id == chat_id))
    existing = r.scalar_one_or_none()
    if existing:
        existing.target_lang = target_lang
        existing.is_enabled = True
    else:
        session.add(ChatTranslation(user_id=current_user.id, chat_id=chat_id, target_lang=target_lang, is_enabled=True))
    await session.commit()
    return {"ok": True}


# ===== Voice Transcription =====
@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    content = await file.read()
    media = await MediaService.save_file(session, current_user.id, content, file.filename, file.content_type)
    text = await AIService.transcribe_audio(media.url)
    return {"text": text, "media_url": media.url}


# ===== Conversation Starters =====
@router.get("/starters")
async def conversation_starters(category: str = None, language: str = "uz", limit: int = 10, session: AsyncSession = Depends(get_session)):
    stmt = select(ConversationStarter).where(ConversationStarter.is_active == True, ConversationStarter.language == language)
    if category:
        stmt = stmt.where(ConversationStarter.category == category)
    r = await session.execute(stmt.order_by(desc(ConversationStarter.uses)).limit(limit))
    return [{"id": s.id, "text": s.text, "category": s.category} for s in r.scalars().all()]


# ===== Sentiment Insights =====
@router.get("/chats/{chat_id}/insights")
async def chat_insights(chat_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(ChatInsight).where(ChatInsight.chat_id == chat_id))
    i = r.scalar_one_or_none()
    if not i:
        return {"total_messages": 0, "compatibility_pct": 0, "sentiment_avg": 0}
    return {"total_messages": i.total_messages, "response_time_avg": i.response_time_avg, "sentiment_avg": i.sentiment_avg, "conversation_streak": i.conversation_streak, "compatibility_pct": i.compatibility_pct}


# ===== Referral =====
@router.get("/referral/code")
async def my_referral_code(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    import secrets
    if not current_user.referral_code:
        current_user.referral_code = f"AM{current_user.id}{secrets.token_hex(3).upper()}"
        await session.commit()
    r = await session.execute(select(ReferralProgram).where(ReferralProgram.referrer_id == current_user.id, ReferralProgram.status == "completed"))
    completed = r.scalars().all()
    return {"code": current_user.referral_code, "completed_referrals": len(completed), "total_reward": sum(c.referrer_reward for c in completed)}


@router.post("/referral/apply")
async def apply_referral(code: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    from sqlalchemy import select as sel
    r = await session.execute(sel(User).where(User.referral_code == code))
    referrer = r.scalar_one_or_none()
    if not referrer or referrer.id == current_user.id:
        raise HTTPException(400, "Invalid code")
    ref = ReferralProgram(referrer_id=referrer.id, referee_id=current_user.id, code=code, status="pending", referrer_reward=500, referee_reward=300)
    session.add(ref)
    await session.commit()
    return {"ok": True, "coins_after_completion": 300}
