"""Calls service - voice/video via Agora / 100ms / Daily.co"""
import secrets
import time
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_, and_
from app.models.advanced import Call
from app.models.user import User
from app.core.config import settings
from app.core.redis import redis_client


class CallService:
    """Voice / video calls"""

    @staticmethod
    async def initiate_call(
        session: AsyncSession, caller: User, callee_id: int, chat_id: int, call_type: str
    ) -> Call:
        """Start a call"""
        channel = f"am_{chat_id}_{int(time.time())}_{secrets.token_hex(4)}"
        call = Call(
            chat_id=chat_id, caller_id=caller.id, callee_id=callee_id, type=call_type,
            channel_name=channel, status="ringing", cost_coins=20 if call_type == "video" else 10,
        )
        session.add(call)
        await session.commit()
        await session.refresh(call)
        payload = {
            "type": "incoming_call",
            "data": {
                "call_id": call.id,
                "caller_id": caller.id,
                "caller_name": caller.nickname or f"User_{caller.id}",
                "caller_avatar": (caller.photos or [None])[0] if caller.photos else None,
                "call_type": call_type,
                "channel": channel,
                "token": CallService._generate_token(channel, callee_id),
            },
        }
        await redis_client.publish(f"user:{callee_id}", json.dumps(payload, default=str))
        return call

    @staticmethod
    async def answer_call(session: AsyncSession, call_id: int, user: User) -> Call:
        call = await session.get(Call, call_id)
        if not call or call.callee_id != user.id:
            raise ValueError("Call not found")
        call.status = "ongoing"
        call.answered_at = datetime.utcnow()
        await session.commit()
        payload = {
            "type": "call_answered",
            "data": {
                "call_id": call.id,
                "channel": call.channel_name,
                "token": CallService._generate_token(call.channel_name, call.caller_id),
            },
        }
        await redis_client.publish(f"user:{call.caller_id}", json.dumps(payload, default=str))
        return call

    @staticmethod
    async def reject_call(session: AsyncSession, call_id: int, user: User):
        call = await session.get(Call, call_id)
        if not call:
            return
        if call.callee_id == user.id:
            call.status = "rejected"
        elif call.caller_id == user.id:
            call.status = "ended"
        call.ended_at = datetime.utcnow()
        await session.commit()
        other_id = call.caller_id if call.callee_id == user.id else call.callee_id
        await redis_client.publish(f"user:{other_id}", json.dumps({"type": "call_ended", "data": {"call_id": call.id}}))

    @staticmethod
    async def end_call(session: AsyncSession, call_id: int, user: User) -> Call:
        call = await session.get(Call, call_id)
        if not call or user.id not in (call.caller_id, call.callee_id):
            raise ValueError("Not allowed")
        call.status = "ended"
        call.ended_at = datetime.utcnow()
        if call.answered_at:
            call.duration = int((call.ended_at - call.answered_at).total_seconds())
            from app.models.gamification import CoinTransaction
            session.add(CoinTransaction(user_id=user.id, amount=-call.cost_coins, type="spent", reason=f"{call.type} call", ref_id=call.id))
        await session.commit()
        other_id = call.caller_id if call.callee_id == user.id else call.callee_id
        await redis_client.publish(f"user:{other_id}", json.dumps({"type": "call_ended", "data": {"call_id": call.id, "duration": call.duration}}))
        return call

    @staticmethod
    def _generate_token(channel: str, user_id: int) -> str:
        if not settings.AGORA_APP_ID:
            return f"dev_token_{channel}_{user_id}"
        try:
            from agora_token_builder import RtcTokenBuilder, Role_Publisher
            expiration_time_in_seconds = 3600
            current_timestamp = int(time.time())
            privilege_expired_ts = current_timestamp + expiration_time_in_seconds
            return RtcTokenBuilder.buildTokenWithUid(
                settings.AGORA_APP_ID, settings.AGORA_APP_CERTIFICATE,
                channel, user_id, Role_Publisher, privilege_expired_ts,
            )
        except ImportError:
            return f"dev_token_{channel}_{user_id}"

    @staticmethod
    async def get_history(session: AsyncSession, user_id: int, limit: int = 50):
        r = await session.execute(select(Call).where(
            or_(Call.caller_id == user_id, Call.callee_id == user_id)
        ).order_by(desc(Call.started_at)).limit(limit))
        return r.scalars().all()
