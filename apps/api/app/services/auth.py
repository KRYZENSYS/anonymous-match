"""Auth service - JWT, telegram initData verification"""
import hashlib
import hmac
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
import bcrypt
from app.core.config import settings


def verify_telegram_init_data(init_data: str, bot_token: str) -> Optional[Dict[str, Any]]:
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data))
        hash_value = parsed.pop("hash", None)
        if not hash_value:
            return None
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        calculated = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if calculated != hash_value:
            return None
        if int(parsed.get("auth_date", 0)) < time.time() - 86400:
            return None
        return parsed
    except Exception:
        return None


def create_access_token(user_id: int, **extra) -> str:
    payload = {
        "sub": str(user_id),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_ACCESS_TTL_HOURS),
        **extra,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False
