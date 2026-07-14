"""Media router — fayl yuklash (Cloudinary + lokal fallback)."""
from __future__ import annotations

import os
import secrets
import shutil
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_session
from app.core.deps import get_current_user
from app.models import User, Media
from app.schemas.notification import MediaUploadResponse

router = APIRouter(prefix="/media", tags=["Media"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/ogg", "audio/wav", "audio/webm", "audio/mp4"}


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    type: Literal["avatar", "photo", "video", "voice", "sticker", "gif", "file"] = Form(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Fayl yuklash (Cloudinary yoki lokal)."""
    # Hajm tekshirish
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Fayl juda katta. Maksimum: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Tur tekshirish
    if type in ("avatar", "photo", "sticker", "gif") and file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Rasm formati noto'g'ri")
    if type == "video" and file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Video formati noto'g'ri")
    if type == "voice" and file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Audio formati noto'g'ri")

    # Cloudinary ga yuklash (agar sozlangan bo'lsa)
    url = None
    thumbnail_url = None
    public_id = None
    width = None
    height = None
    duration = None

    if settings.CLOUDINARY_URL or (settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY):
        try:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True,
            )
            folder = f"anonymous_match/{type}"
            resource_type = "image" if type in ("avatar", "photo", "sticker", "gif") else (
                "video" if type == "video" else "raw"
            )
            result = cloudinary.uploader.upload(
                contents,
                folder=folder,
                resource_type=resource_type,
                public_id=secrets.token_hex(8),
            )
            url = result.get("secure_url")
            public_id = result.get("public_id")
            thumbnail_url = result.get("thumbnail_url") or result.get("secure_url")
            width = result.get("width")
            height = result.get("height")
            duration = result.get("duration")
        except Exception as e:
            # Cloudinary ishlamasa, lokal saqlash
            url = None

    if not url:
        # Lokal saqlash (development uchun)
        media_dir = Path(settings.MEDIA_DIR)
        media_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(file.filename or "file").suffix or ".bin"
        filename = f"{secrets.token_hex(16)}{ext}"
        file_path = media_dir / filename
        file_path.write_bytes(contents)

        url = f"/media/{filename}"
        public_id = filename

    # DB ga saqlash
    media = Media(
        user_id=user.id,
        type=type,
        url=url,
        thumbnail_url=thumbnail_url,
        public_id=public_id,
        filename=file.filename,
        mime_type=file.content_type,
        size_bytes=len(contents),
        width=width,
        height=height,
        duration_sec=duration,
        is_moderated=True,  # TODO: AI moderatsiya
        is_safe=True,
    )
    db.add(media)
    await db.flush()

    return MediaUploadResponse(
        id=media.id,
        type=media.type,
        url=media.url,
        thumbnail_url=media.thumbnail_url,
        width=media.width,
        height=media.height,
        size_bytes=media.size_bytes,
        duration_sec=media.duration_sec,
    )


@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    from sqlalchemy import select
    res = await db.execute(select(Media).where(Media.id == media_id, Media.user_id == user.id))
    media = res.scalar_one_or_none()
    if not media:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Media topilmadi")

    # Cloudinary dan o'chirish
    if media.public_id and (settings.CLOUDINARY_CLOUD_NAME):
        try:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
            )
            resource_type = "image" if media.type in ("avatar", "photo", "sticker", "gif") else (
                "video" if media.type == "video" else "raw"
            )
            cloudinary.uploader.destroy(media.public_id, resource_type=resource_type)
        except Exception:
            pass

    await db.delete(media)
    return {"success": True}
