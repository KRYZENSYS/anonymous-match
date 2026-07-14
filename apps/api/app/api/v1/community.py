"""Community endpoints - groups, events, forums, live streams, NFT, coins"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from app.core.deps import get_current_user, get_session
from app.models.user import User
from app.models.community import (
    Group, GroupMember, GroupPost, Event, EventAttendee,
    ForumThread, ForumReply, LiveStream, NFTAvatar, CoinPackage,
)
from app.services.media import MediaService
from app.services.ai import AIService

router = APIRouter(prefix="/community", tags=["community"])


# ===== Groups =====
@router.get("/groups")
async def list_groups(category: str = None, session: AsyncSession = Depends(get_session)):
    stmt = select(Group).where(Group.type == "public")
    if category:
        stmt = stmt.where(Group.category == category)
    r = await session.execute(stmt.order_by(desc(Group.member_count)))
    return [{"id": g.id, "name": g.name, "slug": g.slug, "description": g.description, "icon": g.icon, "cover_url": g.cover_url, "category": g.category, "member_count": g.member_count, "is_verified": g.is_verified} for g in r.scalars().all()]


@router.post("/groups/{group_id}/join")
async def join_group(group_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    g = await session.get(Group, group_id)
    if not g:
        raise HTTPException(404, "Group not found")
    r = await session.execute(select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id))
    if r.scalar_one_or_none():
        return {"ok": True, "already_member": True}
    session.add(GroupMember(group_id=group_id, user_id=current_user.id))
    g.member_count = (g.member_count or 0) + 1
    await session.commit()
    return {"ok": True}


@router.post("/groups/{group_id}/leave")
async def leave_group(group_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id))
    m = r.scalar_one_or_none()
    if m:
        await session.delete(m)
        g = await session.get(Group, group_id)
        if g:
            g.member_count = max(0, (g.member_count or 0) - 1)
        await session.commit()
    return {"ok": True}


@router.get("/groups/{group_id}/posts")
async def group_posts(group_id: int, limit: int = 30, session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(GroupPost, User).join(User, User.id == GroupPost.user_id).where(GroupPost.group_id == group_id).order_by(desc(GroupPost.created_at)).limit(limit))
    return [{"id": p.id, "user_nickname": u.nickname, "user_avatar": (u.photos or [None])[0] if u.photos else None, "content": p.content, "media_urls": p.media_urls, "likes_count": p.likes_count, "comments_count": p.comments_count, "is_pinned": p.is_pinned, "created_at": p.created_at} for p, u in r.all()]


@router.post("/groups/{group_id}/post")
async def create_group_post(group_id: int, content: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    p = GroupPost(group_id=group_id, user_id=current_user.id, content=content)
    session.add(p)
    await session.commit()
    return {"id": p.id}


# ===== Events =====
@router.get("/events")
async def list_events(limit: int = 30, session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(Event).where(Event.starts_at > datetime.utcnow()).order_by(Event.starts_at).limit(limit))
    return [{"id": e.id, "title": e.title, "description": e.description, "cover_url": e.cover_url, "category": e.category, "location_name": e.location_name, "starts_at": e.starts_at, "capacity": e.capacity, "attendees_count": e.attendees_count, "ticket_price": e.ticket_price, "is_online": e.is_online} for e in r.scalars().all()]


@router.post("/events/{event_id}/join")
async def join_event(event_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    e = await session.get(Event, event_id)
    if not e:
        raise HTTPException(404, "Event not found")
    if e.capacity and e.attendees_count >= e.capacity:
        raise HTTPException(400, "Event full")
    r = await session.execute(select(EventAttendee).where(EventAttendee.event_id == event_id, EventAttendee.user_id == current_user.id))
    if r.scalar_one_or_none():
        return {"ok": True, "already_joined": True}
    # Deduct coins if paid
    if e.ticket_price > 0:
        from app.models.gamification import CoinTransaction
        from sqlalchemy import select as sel
        r2 = await session.execute(sel(CoinTransaction).where(CoinTransaction.user_id == current_user.id))
        txs = r2.scalars().all()
        balance = sum(t.amount for t in txs)
        if balance < e.ticket_price:
            raise HTTPException(400, "Not enough coins")
        session.add(CoinTransaction(user_id=current_user.id, amount=-e.ticket_price, type="spent", reason=f"Event: {e.title}"))
    session.add(EventAttendee(event_id=event_id, user_id=current_user.id, ticket_paid=e.ticket_price))
    e.attendees_count = (e.attendees_count or 0) + 1
    await session.commit()
    return {"ok": True}


# ===== Forum =====
@router.get("/forum/threads")
async def list_threads(category: str = None, limit: int = 30, session: AsyncSession = Depends(get_session)):
    stmt = select(ForumThread)
    if category:
        stmt = stmt.where(ForumThread.category == category)
    r = await session.execute(stmt.order_by(desc(ForumThread.created_at)).limit(limit))
    return [{"id": t.id, "category": t.category, "title": t.title, "user_id": t.user_id, "replies": t.replies, "views": t.views, "is_pinned": t.is_pinned, "created_at": t.created_at} for t in r.scalars().all()]


@router.post("/forum/threads")
async def create_thread(category: str, title: str, content: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    t = ForumThread(category=category, title=title, content=content, user_id=current_user.id)
    session.add(t)
    await session.commit()
    return {"id": t.id}


@router.get("/forum/threads/{thread_id}/replies")
async def thread_replies(thread_id: int, session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(ForumReply, User).join(User, User.id == ForumReply.user_id).where(ForumReply.thread_id == thread_id).order_by(ForumReply.created_at))
    t = await session.get(ForumThread, thread_id)
    if t:
        t.views = (t.views or 0) + 1
        await session.commit()
    return [{"id": rep.id, "user_nickname": u.nickname, "user_avatar": (u.photos or [None])[0] if u.photos else None, "content": rep.content, "likes_count": rep.likes_count, "created_at": rep.created_at} for rep, u in r.all()]


@router.post("/forum/threads/{thread_id}/reply")
async def reply_thread(thread_id: int, content: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    t = await session.get(ForumThread, thread_id)
    if not t or t.is_locked:
        raise HTTPException(400, "Thread not found or locked")
    rep = ForumReply(thread_id=thread_id, user_id=current_user.id, content=content)
    session.add(rep)
    t.replies = (t.replies or 0) + 1
    await session.commit()
    return {"id": rep.id}


# ===== Live Streams =====
@router.post("/live/start")
async def start_live(title: str, description: str = None, visibility: str = "public", current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    # Generate stream channel via 100ms/Agora
    channel = f"live_{current_user.id}_{int(datetime.utcnow().timestamp())}"
    ls = LiveStream(host_id=current_user.id, title=title, description=description, stream_url=f"rtmp://stream.anonymous-match.uz/{channel}", visibility=visibility, is_live=True)
    session.add(ls)
    await session.commit()
    return {"id": ls.id, "channel": channel, "stream_url": ls.stream_url, "rtmp_url": f"rtmp://stream.anonymous-match.uz/live"}


@router.post("/live/{stream_id}/end")
async def end_live(stream_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    ls = await session.get(LiveStream, stream_id)
    if not ls or ls.host_id != current_user.id:
        raise HTTPException(403, "Not allowed")
    ls.is_live = False
    ls.ended_at = datetime.utcnow()
    await session.commit()
    return {"ok": True}


@router.get("/live/active")
async def active_streams(session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(LiveStream, User).join(User, User.id == LiveStream.host_id).where(LiveStream.is_live == True).order_by(desc(LiveStream.viewers_count)).limit(30))
    return [{"id": s.id, "host_nickname": u.nickname, "host_avatar": (u.photos or [None])[0] if u.photos else None, "title": s.title, "viewers_count": s.viewers_count, "stream_url": s.stream_url, "thumbnail_url": s.thumbnail_url, "visibility": s.visibility, "started_at": s.started_at} for s, u in r.all()]


# ===== NFT Avatar =====
@router.post("/nft-avatar/generate")
async def generate_nft_avatar(style: str, prompt: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    image_url = await AIService.generate_avatar(style, prompt)
    from sqlalchemy import select as sel
    r = await session.execute(sel(NFTAvatar).where(NFTAvatar.user_id == current_user.id))
    nft = r.scalar_one_or_none()
    if nft:
        nft.image_url = image_url
        nft.style = style
        nft.prompt = prompt
    else:
        session.add(NFTAvatar(user_id=current_user.id, image_url=image_url, style=style, prompt=prompt))
    await session.commit()
    return {"image_url": image_url}


@router.post("/nft-avatar/mint")
async def mint_nft_avatar(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(NFTAvatar).where(NFTAvatar.user_id == current_user.id))
    nft = r.scalar_one_or_none()
    if not nft:
        raise HTTPException(400, "Generate avatar first")
    # Mint via TON
    tx_hash = await AIService.mint_nft_ton(nft.image_url, current_user.telegram_id)
    nft.transaction_hash = tx_hash
    await session.commit()
    return {"tx_hash": tx_hash}


# ===== Coin Packages =====
@router.get("/coins/packages")
async def coin_packages(session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(CoinPackage).where(CoinPackage.is_active == True).order_by(CoinPackage.price_stars))
    return [{"id": p.id, "name": p.name, "coins": p.coins, "bonus_coins": p.bonus_coins, "price_stars": p.price_stars, "price_usd": p.price_usd, "is_popular": p.is_popular} for p in r.scalars().all()]


@router.post("/coins/purchase")
async def purchase_coins(package_id: int, telegram_payment_charge_id: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    p = await session.get(CoinPackage, package_id)
    if not p:
        raise HTTPException(404, "Package not found")
    total = p.coins + (p.bonus_coins or 0)
    from app.models.gamification import CoinTransaction
    from app.models.subscription import Payment
    session.add(CoinTransaction(user_id=current_user.id, amount=total, type="purchase", reason=f"Coin package: {p.name}"))
    session.add(Payment(user_id=current_user.id, tier=f"coins_{p.id}", amount_stars=p.price_stars, amount_usd=p.price_usd, telegram_payment_charge_id=telegram_payment_charge_id, status="completed"))
    await session.commit()
    return {"coins_added": total}
