"""Gamification API - coins, achievements, streaks, missions, gifts, leaderboard, spin"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timedelta
import random
from app.core.deps import get_current_user, get_session
from app.models.user import User
from app.models.gamification import (
    CoinTransaction, Achievement, UserAchievement, Streak,
    Mission, UserMission, Gift, GiftTransaction, SpinReward, Leaderboard,
)
from app.models.swipe import Match

router = APIRouter(prefix="/gamification", tags=["gamification"])


# ===== Coins =====
@router.get("/coins/balance")
async def get_coin_balance(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(CoinTransaction).where(CoinTransaction.user_id == current_user.id))
    txs = r.scalars().all()
    balance = sum(tx.amount for tx in txs)
    return {"balance": balance, "transactions": [{"amount": t.amount, "type": t.type, "reason": t.reason, "created_at": t.created_at} for t in txs[-20:]]}


@router.post("/coins/add")
async def add_coins(amount: int, type: str, reason: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if current_user.is_premium and type == "earned":
        amount = int(amount * 1.5)  # Premium bonus
    session.add(CoinTransaction(user_id=current_user.id, amount=amount, type=type, reason=reason))
    await session.commit()
    return {"balance": await _get_balance(session, current_user.id)}


async def _get_balance(session, user_id):
    r = await session.execute(select(CoinTransaction).where(CoinTransaction.user_id == user_id))
    return sum(t.amount for t in r.scalars().all())


# ===== Achievements =====
@router.get("/achievements")
async def get_achievements(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(Achievement).order_by(Achievement.tier, Achievement.id))
    all_ach = r.scalars().all()
    r2 = await session.execute(select(UserAchievement).where(UserAchievement.user_id == current_user.id))
    user_ach = {ua.achievement_id: ua for ua in r2.scalars().all()}
    return [
        {
            "id": a.id, "code": a.code, "name": a.name, "description": a.description,
            "icon": a.icon, "tier": a.tier, "reward_coins": a.reward_coins,
            "condition_type": a.condition_type, "condition_value": a.condition_value,
            "progress": user_ach[a.id].progress if a.id in user_ach else 0,
            "unlocked": a.id in user_ach and user_ach[a.id].unlocked_at is not None,
            "unlocked_at": user_ach[a.id].unlocked_at if a.id in user_ach else None,
        }
        for a in all_ach
    ]


# ===== Streak =====
@router.post("/streak/checkin")
async def streak_checkin(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(Streak).where(Streak.user_id == current_user.id))
    streak = r.scalar_one_or_none()
    today = datetime.utcnow().date()
    if not streak:
        streak = Streak(user_id=current_user.id, current_streak=1, longest_streak=1, last_login=today, total_logins=1)
        session.add(streak)
        coins = 10
    else:
        if streak.last_login == today:
            return {"current_streak": streak.current_streak, "longest_streak": streak.longest_streak, "already_checked_in": True}
        elif streak.last_login == today - timedelta(days=1):
            streak.current_streak += 1
            streak.last_login = today
            streak.total_logins += 1
        else:
            streak.current_streak = 1
            streak.last_login = today
            streak.total_logins += 1
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        coins = min(10 + streak.current_streak * 2, 100)
    session.add(CoinTransaction(user_id=current_user.id, amount=coins, type="earned", reason=f"Daily streak: {streak.current_streak} days"))
    await session.commit()
    return {"current_streak": streak.current_streak, "longest_streak": streak.longest_streak, "coins_earned": coins, "already_checked_in": False}


# ===== Missions =====
@router.get("/missions")
async def get_missions(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(Mission).where(Mission.type == "daily"))
    all_m = r.scalars().all()
    r2 = await session.execute(select(UserMission).where(UserMission.user_id == current_user.id, UserMission.expires_at > datetime.utcnow()))
    user_m = {um.mission_id: um for um in r2.scalars().all()}
    return [
        {
            "id": m.id, "code": m.code, "name": m.name, "description": m.description,
            "type": m.type, "target": m.target,
            "reward_coins": m.reward_coins, "reward_superlikes": m.reward_superlikes, "reward_boost": m.reward_boost,
            "progress": user_m[m.id].progress if m.id in user_m else 0,
            "is_completed": user_m[m.id].is_completed if m.id in user_m else False,
        }
        for m in all_m
    ]


@router.post("/missions/{mission_id}/claim")
async def claim_mission(mission_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(UserMission).where(UserMission.user_id == current_user.id, UserMission.mission_id == mission_id, UserMission.is_completed == True))
    um = r.scalar_one_or_none()
    if not um:
        raise HTTPException(400, "Mission not completed or already claimed")
    m = await session.get(Mission, mission_id)
    if m.reward_coins:
        session.add(CoinTransaction(user_id=current_user.id, amount=m.reward_coins, type="earned", reason=f"Mission: {m.name}"))
    await session.delete(um)
    await session.commit()
    return {"coins_earned": m.reward_coins or 0}


# ===== Gifts =====
@router.get("/gifts")
async def list_gifts(session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(Gift).order_by(Gift.price_coins))
    return [{"id": g.id, "code": g.code, "name": g.name, "icon": g.icon, "price_coins": g.price_coins, "category": g.category, "image_url": g.image_url} for g in r.scalars().all()]


@router.post("/gifts/send")
async def send_gift(gift_id: int, recipient_id: int, message: str = None, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    gift = await session.get(Gift, gift_id)
    if not gift:
        raise HTTPException(404, "Gift not found")
    balance = await _get_balance(session, current_user.id)
    if balance < gift.price_coins:
        raise HTTPException(400, "Not enough coins")
    session.add(CoinTransaction(user_id=current_user.id, amount=-gift.price_coins, type="spent", reason=f"Gift: {gift.name}", ref_id=recipient_id))
    session.add(GiftTransaction(sender_id=current_user.id, recipient_id=recipient_id, gift_id=gift_id, message=message))
    session.add(CoinTransaction(user_id=recipient_id, amount=int(gift.price_coins * 0.3), type="earned", reason="Gift received"))
    await session.commit()
    return {"ok": True, "remaining_balance": balance - gift.price_coins}


# ===== Spin Wheel =====
@router.post("/spin")
async def spin_wheel(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    # Check cooldown (1 hour)
    r = await session.execute(select(SpinReward).where(SpinReward.user_id == current_user.id).order_by(desc(SpinReward.created_at)).limit(1))
    last = r.scalar_one_or_none()
    if last and last.created_at > datetime.utcnow() - timedelta(hours=1):
        remaining = 3600 - int((datetime.utcnow() - last.created_at).total_seconds())
        raise HTTPException(400, f"Try again in {remaining}s")
    rewards = [(10, "coins"), (20, "coins"), (50, "coins"), (100, "coins"), (1, "superlike"), (1, "boost"), (200, "coins"), (500, "coins")]
    value, rtype = random.choice(rewards)
    session.add(SpinReward(user_id=current_user.id, reward_type=rtype, reward_value=value))
    if rtype == "coins":
        session.add(CoinTransaction(user_id=current_user.id, amount=value, type="earned", reason="Spin wheel"))
    elif rtype == "superlike":
        current_user.superlikes_remaining = (current_user.superlikes_remaining or 0) + value
    elif rtype == "boost":
        from app.services.premium import PremiumService
        # Add boost
    await session.commit()
    return {"reward_type": rtype, "reward_value": value}


# ===== Leaderboard =====
@router.get("/leaderboard")
async def get_leaderboard(period: str = "weekly", limit: int = 100, session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(Leaderboard, User).join(User, User.id == Leaderboard.user_id).order_by(Leaderboard.total_score.desc()).limit(limit))
    return [
        {
            "rank": i + 1, "user_id": l.user_id,
            "nickname": u.nickname, "avatar": (u.photos or [None])[0] if u.photos else None,
            "score": l.total_score, "matches": l.matches, "messages_sent": l.messages_sent,
            "is_premium": u.is_premium,
        }
        for i, (l, u) in enumerate(r.all())
    ]
