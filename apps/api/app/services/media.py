"""Media service"""
import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.media import Media
from app.core.config import settings
import aiofiles


class MediaService:
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    MAX_SIZE = 50 * 1024 * 1024

    @staticmethod
    async def save_file(session, user_id, file_bytes, filename, content_type):
        if len(file_bytes) > MediaService.MAX_SIZE:
            raise ValueError("File too large")
        media_type = "image" if content_type in MediaService.ALLOWED_IMAGE_TYPES else "other"
        ext = Path(filename).suffix or ".jpg"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        rel_path = f"{media_type}s/{datetime.utcnow().strftime('%Y/%m/%d')}/{unique_name}"
        full_path = Path(settings.MEDIA_ROOT) / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(file_bytes)
        url = f"{settings.API_URL}/media/{rel_path}"
        media = Media(user_id=user_id, type=media_type, filename=filename, url=url, size_bytes=len(file_bytes), content_type=content_type, sha256=hashlib.sha256(file_bytes).hexdigest())
        session.add(media)
        await session.commit()
        await session.refresh(media)
        return media
