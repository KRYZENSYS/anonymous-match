"""Stories API - 24-hour ephemeral content"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta
from app.core.deps import get_current_user, get_session
from app.models.story import Story, StoryView, StoryReaction, StoryReply
from app.models.user import User
from app.services.media import MediaService
import json

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("/")
async def create_story(
    file: UploadFile = File(...),
    text_overlay: str = None,
    background_color: str = "#000000",
    duration: int = 5,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    content = await file.read()
    media = await MediaService.save_file(session, current_user.id, content, file.filename, file.content_type)
    story = Story(
        user_id=current_user.id, media_type="image" if "image" in file.content_type else "video",
        media_url=media.url, text_overlay=text_overlay, background_color=background_color, duration=duration,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    session.add(story)
    await session.commit()
    await session.refresh(story)
    return {"id": story.id, "media_url": story.media_url, "expires_at": story.expires_at}


@router.get("/feed")
async def get_stories_feed(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get active stories from user + matches"""
    from app.models.swipe import Match
    matched_ids_subq = select(Match.user1_id).where(Match.user2_id == current_user.id).union(
        select(Match.user2_id).where(Match.user1_id == current_user.id)
    )
    stmt = select(Story, User).join(User, User.id == Story.user_id).where(
        Story.expires_at > datetime.utcnow(),
        or_(Story.user_id == current_user.id, Story.user_id.in_(matched_ids_subq)),
    ).order_by(Story.created_at.desc())
    result = await session.execute(stmt)
    rows = result.all()
    return [
        {
            "id": s.id, "user_id": s.user_id,
            "user_nickname": u.nickname, "user_avatar": (u.photos or [None])[0] if u.photos else None,
            "media_type": s.media_type, "media_url": s.media_url, "text_overlay": s.text_overlay,
            "background_color": s.background_color, "duration": s.duration,
            "views_count": s.views_count, "is_viewed": await _is_viewed(session, s.id, current_user.id),
            "is_mine": s.user_id == current_user.id, "created_at": s.created_at,
        }
        for s, u in rows
    ]


async def _is_viewed(session, story_id, user_id):
    r = await session.execute(select(StoryView).where(and_(StoryView.story_id == story_id, StoryView.viewer_id == user_id)))
    return r.scalar_one_or_none() is not None


@router.post("/{story_id}/view")
async def view_story(story_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    story = await session.get(Story, story_id)
    if not story or story.expires_at < datetime.utcnow():
        raise HTTPException(404, "Story not found or expired")
    existing = await session.execute(select(StoryView).where(and_(StoryView.story_id == story_id, StoryView.viewer_id == current_user.id)))
    if not existing.scalar_one_or_none():
        session.add(StoryView(story_id=story_id, viewer_id=current_user.id))
        story.views_count = (story.views_count or 0) + 1
        await session.commit()
    return {"ok": True}


@router.post("/{story_id}/react")
async def react_story(story_id: int, reaction: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    session.add(StoryReaction(story_id=story_id, user_id=current_user.id, reaction=reaction))
    await session.commit()
    return {"ok": True}


@router.post("/{story_id}/reply")
async def reply_story(story_id: int, content: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    from app.models.swipe import Match
    from app.models.chat import Chat
    story = await session.get(Story, story_id)
    if not story or story.user_id == current_user.id:
        raise HTTPException(400, "Cannot reply")
    session.add(StoryReply(story_id=story_id, user_id=current_user.id, content=content))
    # Send to chat if matched
    r = await session.execute(select(Match).where(or_(and_(Match.user1_id == current_user.id, Match.user2_id == story.user_id), and_(Match.user1_id == story.user_id, Match.user2_id == current_user.id))))
    match = r.scalar_one_or_none()
    if match and match.chat_id:
        from app.services.chat import ChatService
        await ChatService.send_message(session, match.chat_id, current_user.id, "text", f"💬 Sizning story'ingizga: {content}")
    await session.commit()
    return {"ok": True}


@router.get("/me")
async def my_stories(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(Story).where(Story.user_id == current_user.id, Story.expires_at > datetime.utcnow()).order_by(Story.created_at.desc()))
    return [{"id": s.id, "media_url": s.media_url, "views_count": s.views_count, "created_at": s.created_at, "expires_at": s.expires_at} for s in r.scalars().all()]


@router.delete("/{story_id}")
async def delete_story(story_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    story = await session.get(Story, story_id)
    if not story or story.user_id != current_user.id:
        raise HTTPException(403, "Not allowed")
    await session.delete(story)
    await session.commit()
    return {"ok": True}
