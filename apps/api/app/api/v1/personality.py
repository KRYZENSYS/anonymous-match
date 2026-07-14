"""Personality, prompts, voice intro, top5, social, lifestyle"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.core.deps import get_current_user, get_session
from app.models.user import User
from app.models.personality import (
    PersonalityTest, Prompt, UserPrompt, TopFive, VoiceIntro, VideoIntro,
    SocialLink, LifestyleTag, UserLifestyleTag,
)
from app.services.media import MediaService
from app.services.ai import AIService

router = APIRouter(prefix="/personality", tags=["personality"])


# ===== Personality Test =====
@router.post("/test/start")
async def start_test(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return {"questions": AIService.get_test_questions(current_user.language_code or "uz")}


@router.post("/test/submit")
async def submit_test(answers: dict, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    result = await AIService.calculate_personality(answers)
    await session.execute(delete(PersonalityTest).where(PersonalityTest.user_id == current_user.id))
    test = PersonalityTest(
        user_id=current_user.id, mbti_type=result["mbti"], big_five=result["big_five"],
        love_language=result["love_language"], answers=answers, completed=True,
    )
    session.add(test)
    await session.commit()
    return result


@router.get("/test/result")
async def test_result(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(PersonalityTest).where(PersonalityTest.user_id == current_user.id, PersonalityTest.completed == True).order_by(PersonalityTest.created_at.desc()).limit(1))
    t = r.scalar_one_or_none()
    if not t:
        return None
    return {"mbti": t.mbti_type, "big_five": t.big_five, "love_language": t.love_language, "created_at": t.created_at}


# ===== Prompts (Hinge-style) =====
@router.get("/prompts")
async def get_prompts(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(Prompt).where(Prompt.is_active == True).order_by(Prompt.order))
    prompts = r.scalars().all()
    r2 = await session.execute(select(UserPrompt).where(UserPrompt.user_id == current_user.id))
    user_answers = {up.prompt_id: up.answer for up in r2.scalars().all()}
    return [
        {"id": p.id, "question": p.question, "category": p.category, "placeholder": p.placeholder,
         "answer": user_answers.get(p.id)}
        for p in prompts
    ]


@router.post("/prompts/{prompt_id}/answer")
async def answer_prompt(prompt_id: int, answer: str, order: int = 0, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(UserPrompt).where(UserPrompt.user_id == current_user.id, UserPrompt.prompt_id == prompt_id))
    existing = r.scalar_one_or_none()
    if existing:
        existing.answer = answer
    else:
        session.add(UserPrompt(user_id=current_user.id, prompt_id=prompt_id, answer=answer, order=order))
    await session.commit()
    return {"ok": True}


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await session.execute(delete(UserPrompt).where(UserPrompt.user_id == current_user.id, UserPrompt.prompt_id == prompt_id))
    await session.commit()
    return {"ok": True}


# ===== Top 5 (Spotify-style) =====
@router.get("/top5")
async def get_top5(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(TopFive).where(TopFive.user_id == current_user.id))
    t = r.scalar_one_or_none()
    if not t:
        return {"movies": [], "songs": [], "books": [], "foods": [], "travel": []}
    return {"movies": t.movies, "songs": t.songs, "books": t.books, "foods": t.foods, "travel": t.travel}


@router.post("/top5")
async def update_top5(data: dict, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(TopFive).where(TopFive.user_id == current_user.id))
    t = r.scalar_one_or_none()
    if not t:
        t = TopFive(user_id=current_user.id, **data)
        session.add(t)
    else:
        for k, v in data.items():
            setattr(t, k, v)
    await session.commit()
    return {"ok": True}


# ===== Voice Intro =====
@router.post("/voice-intro")
async def upload_voice_intro(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    content = await file.read()
    media = await MediaService.save_file(session, current_user.id, content, file.filename, file.content_type)
    # Optional: transcribe via AI
    from app.services.ai import AIService
    transcript = await AIService.transcribe_audio(media.url)
    r = await session.execute(select(VoiceIntro).where(VoiceIntro.user_id == current_user.id))
    vi = r.scalar_one_or_none()
    if vi:
        vi.audio_url = media.url
        vi.transcript = transcript
    else:
        session.add(VoiceIntro(user_id=current_user.id, audio_url=media.url, transcript=transcript))
    await session.commit()
    return {"audio_url": media.url, "transcript": transcript}


@router.delete("/voice-intro")
async def delete_voice_intro(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await session.execute(delete(VoiceIntro).where(VoiceIntro.user_id == current_user.id))
    await session.commit()
    return {"ok": True}


# ===== Video Intro =====
@router.post("/video-intro")
async def upload_video_intro(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    content = await file.read()
    media = await MediaService.save_file(session, current_user.id, content, file.filename, file.content_type)
    r = await session.execute(select(VideoIntro).where(VideoIntro.user_id == current_user.id))
    vi = r.scalar_one_or_none()
    if vi:
        vi.video_url = media.url
    else:
        session.add(VideoIntro(user_id=current_user.id, video_url=media.url))
    await session.commit()
    return {"video_url": media.url}


# ===== Social Links =====
@router.get("/social")
async def get_social(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(SocialLink).where(SocialLink.user_id == current_user.id))
    s = r.scalar_one_or_none()
    if not s:
        return {}
    return {"instagram": s.instagram, "tiktok": s.tiktok, "spotify": s.spotify, "telegram": s.telegram, "twitter": s.twitter, "youtube": s.youtube, "linkedin": s.linkedin, "website": s.website}


@router.post("/social")
async def update_social(data: dict, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(SocialLink).where(SocialLink.user_id == current_user.id))
    s = r.scalar_one_or_none()
    if not s:
        s = SocialLink(user_id=current_user.id, **data)
        session.add(s)
    else:
        for k, v in data.items():
            if hasattr(s, k):
                setattr(s, k, v)
    await session.commit()
    return {"ok": True}


# ===== Lifestyle Tags =====
@router.get("/lifestyle/tags")
async def get_lifestyle_tags(session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(LifestyleTag).order_by(LifestyleTag.category, LifestyleTag.name))
    return [{"id": t.id, "code": t.code, "name": t.name, "icon": t.icon, "category": t.category} for t in r.scalars().all()]


@router.post("/lifestyle/tags")
async def set_lifestyle_tags(tag_ids: list[int], current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await session.execute(delete(UserLifestyleTag).where(UserLifestyleTag.user_id == current_user.id))
    for tid in tag_ids:
        session.add(UserLifestyleTag(user_id=current_user.id, tag_id=tid))
    await session.commit()
    return {"ok": True}
