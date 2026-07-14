"""Discover & swipe service"""
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.swipe import Like, Match
from app.models.chat import Chat, Message


class DiscoverService:
    @staticmethod
    async def get_profiles(session, user, limit=20):
        seen_subq = select(Like.target_user_id).where(Like.user_id == user.id)
        stmt = select(User).where(and_(User.id != user.id, User.is_banned == False, User.is_profile_complete == True, User.id.not_in(seen_subq)))
        if user.looking_for and user.looking_for != "everyone":
            stmt = stmt.where(User.gender == user.looking_for)
        elif user.gender == "male":
            stmt = stmt.where(or_(User.gender == "female", User.gender == "other"))
        elif user.gender == "female":
            stmt = stmt.where(or_(User.gender == "male", User.gender == "other"))
        today = datetime.utcnow().date()
        max_birth = today.replace(year=today.year - 18)
        min_birth = today.replace(year=today.year - 50)
        stmt = stmt.where(and_(User.birth_date <= max_birth, User.birth_date >= min_birth))
        if user.region and random.random() < 0.5:
            stmt = stmt.where(User.region == user.region)
        stmt = stmt.order_by(User.is_boosted.desc(), User.last_seen.desc()).limit(limit * 2)
        result = await session.execute(stmt)
        profiles = list(result.scalars().all())
        random.shuffle(profiles)
        return profiles[:limit]

    @staticmethod
    async def swipe(session, user_id, target_user_id, action):
        if user_id == target_user_id:
            return {"is_match": False, "error": "self_swipe"}
        user = await session.get(User, user_id)
        if action == "like" and not user.is_premium and (user.likes_sent_today or 0) >= 50:
            return {"is_match": False, "error": "daily_limit_reached"}
        existing = await session.execute(select(Like).where(and_(Like.user_id == user_id, Like.target_user_id == target_user_id)))
        if existing.scalar_one_or_none():
            return {"is_match": False, "error": "already_swiped"}
        like = Like(user_id=user_id, target_user_id=target_user_id, action=action, is_superlike=(action == "superlike"))
        session.add(like)
        user.likes_sent = (user.likes_sent or 0) + 1
        if action == "like":
            user.likes_sent_today = (user.likes_sent_today or 0) + 1
        target = await session.get(User, target_user_id)
        if target:
            target.likes_received = (target.likes_received or 0) + 1
        is_match, match_id = False, None
        if action in ("like", "superlike"):
            mutual = await session.execute(select(Like).where(and_(Like.user_id == target_user_id, Like.target_user_id == user_id, Like.action.in_(("like", "superlike")))))
            if mutual.scalar_one_or_none():
                match = Match(user1_id=min(user_id, target_user_id), user2_id=max(user_id, target_user_id), is_active=True)
                session.add(match)
                await session.flush()
                chat = Chat(user1_id=min(user_id, target_user_id), user2_id=max(user_id, target_user_id), match_id=match.id)
                session.add(chat)
                await session.flush()
                match.chat_id = chat.id
                match_id, is_match = match.id, True
                user.match_count = (user.match_count or 0) + 1
                if target:
                    target.match_count = (target.match_count or 0) + 1
        await session.commit()
        return {"is_match": is_match, "match_id": match_id, "action": action}

    @staticmethod
    async def get_matches(session, user_id, limit=20):
        stmt = select(Match, User).join(User, or_(and_(Match.user1_id == user_id, User.id == Match.user2_id), and_(Match.user2_id == user_id, User.id == Match.user1_id))).where(or_(Match.user1_id == user_id, Match.user2_id == user_id)).where(Match.is_active == True).order_by(Match.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        rows = result.all()
        matches = []
        for match, other in rows:
            last_msg_stmt = select(Message).where(Message.chat_id == match.chat_id).order_by(Message.created_at.desc()).limit(1)
            last_msg = (await session.execute(last_msg_stmt)).scalar_one_or_none()
            matches.append({"id": match.id, "chat_id": match.chat_id, "other_user_id": other.id, "other_user_nickname": other.nickname, "other_user_avatar": (other.photos or [None])[0] if other.photos else None, "is_online": other.last_seen and other.last_seen > datetime.utcnow() - timedelta(minutes=5), "last_message": last_msg.content if last_msg else None, "last_message_at": last_msg.created_at if last_msg else match.created_at, "created_at": match.created_at})
        return matches
