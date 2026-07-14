"""Xavfsizlik — JWT, Telegram initData, password hashing, CSRF."""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS)


# ===== Password (ixtiyoriy, Telegram bilan kelajakda) =====
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ===== JWT =====
def create_access_token(
    subject: str | int,
    extra: dict[str, Any] | None = None,
    ttl_hours: int | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=ttl_hours or settings.JWT_ACCESS_TTL_HOURS)).timestamp()),
        "jti": secrets.token_urlsafe(16),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e


# ===== Telegram initData validation =====
def validate_telegram_init_data(init_data: str) -> dict | None:
    """
    Telegram WebApp initData'ni tekshiradi.
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    if not init_data or not settings.BOT_TOKEN:
        return None

    try:
        parsed = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
    except Exception:
        return None

    if "hash" not in parsed:
        return None

    received_hash = parsed.pop("hash")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))

    secret_key = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    # Vaqt tekshirish (24 soat ichida bo'lishi kerak)
    if "auth_date" in parsed:
        try:
            auth_time = int(parsed["auth_date"])
            if abs(time.time() - auth_time) > 86400:
                return None
        except ValueError:
            return None

    if "user" in parsed:
        try:
            parsed["user"] = json.loads(parsed["user"])
        except Exception:
            return None

    parsed["_validated_at"] = int(time.time())
    return parsed


# ===== CSRF token =====
def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected: str) -> bool:
    return hmac.compare_digest(token, expected)


# ===== Anonim identifikator =====
def generate_public_id() -> str:
    """Foydalanuvchiga ko'rinadigan, lekin ID'ni oshkor qilmaydigan identifikator.
    Masalan: #kryzen-A1B2C3
    """
    return f"kryzen-{secrets.token_hex(3).upper()}"


# ===== Tasodifiy token =====
def random_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)
