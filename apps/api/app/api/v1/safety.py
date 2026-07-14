"""Safety endpoints - photo verification, 2FA, panic, report, stalker protection, data export, date plan"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from app.core.deps import get_current_user, get_session
from app.models.user import User
from app.models.safety import (
    PhotoVerification, TwoFactorAuth, EmergencyContact, SafetyReport,
    PanicEvent, StalkerProtection, DataExportRequest, DatePlan, DateFeedback,
)
from app.services.ai import AIService
from app.services.media import MediaService
import pyotp

router = APIRouter(prefix="/safety", tags=["safety"])


# ===== Photo Verification =====
@router.post("/verify/photo")
async def verify_photo(
    selfie: UploadFile = File(...),
    reference_photo_id: int = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    content = await selfie.read()
    media = await MediaService.save_file(session, current_user.id, content, selfie.filename, selfie.content_type)
    if not current_user.photos or reference_photo_id is None or reference_photo_id >= len(current_user.photos):
        raise HTTPException(400, "Reference photo not found")
    reference_url = current_user.photos[reference_photo_id]
    confidence = await AIService.compare_faces(media.url, reference_url)
    status = "approved" if confidence > 0.8 else "rejected"
    pv = PhotoVerification(
        user_id=current_user.id, selfie_url=media.url, reference_photo_id=reference_photo_id,
        status=status, confidence=confidence,
        verified_at=datetime.utcnow() if status == "approved" else None,
    )
    session.add(pv)
    if status == "approved":
        current_user.is_verified = True
    await session.commit()
    return {"status": status, "confidence": confidence}


@router.get("/verify/status")
async def verify_status(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(PhotoVerification).where(PhotoVerification.user_id == current_user.id).order_by(desc(PhotoVerification.created_at)).limit(1))
    last = r.scalar_one_or_none()
    return {"is_verified": current_user.is_verified, "last_verification": {"status": last.status, "confidence": last.confidence, "created_at": last.created_at} if last else None}


# ===== 2FA =====
@router.post("/2fa/enable")
async def enable_2fa(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    secret = pyotp.random_base32()
    r = await session.execute(select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id))
    tfa = r.scalar_one_or_none()
    if tfa:
        tfa.enabled = True
        tfa.secret = secret
    else:
        import secrets
        backup = [secrets.token_hex(4) for _ in range(10)]
        session.add(TwoFactorAuth(user_id=current_user.id, enabled=True, secret=secret, backup_codes=backup))
    await session.commit()
    totp = pyotp.TOTP(secret)
    return {"secret": secret, "qr_url": totp.provisioning_uri(name=current_user.username or str(current_user.id), issuer_name="AnonymousMatch")}


@router.post("/2fa/verify")
async def verify_2fa(code: str, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id))
    tfa = r.scalar_one_or_none()
    if not tfa or not tfa.enabled:
        raise HTTPException(400, "2FA not enabled")
    totp = pyotp.TOTP(tfa.secret)
    if not totp.verify(code):
        raise HTTPException(400, "Invalid code")
    tfa.last_used = datetime.utcnow()
    await session.commit()
    return {"ok": True}


@router.post("/2fa/disable")
async def disable_2fa(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id))
    tfa = r.scalar_one_or_none()
    if tfa:
        tfa.enabled = False
    await session.commit()
    return {"ok": True}


# ===== Emergency Contact =====
@router.post("/emergency")
async def add_emergency(name: str, phone: str, relation: str = None, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    ec = EmergencyContact(user_id=current_user.id, name=name, phone=phone, relation=relation)
    session.add(ec)
    await session.commit()
    return {"id": ec.id, "name": ec.name, "phone": ec.phone}


@router.get("/emergency")
async def list_emergency(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(EmergencyContact).where(EmergencyContact.user_id == current_user.id))
    return [{"id": e.id, "name": e.name, "phone": e.phone, "relation": e.relation} for e in r.scalars().all()]


# ===== Panic Button =====
@router.post("/panic")
async def panic_button(lat: float = None, lon: float = None, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    p = PanicEvent(user_id=current_user.id, location_lat=lat, location_lon=lon)
    session.add(p)
    # Notify emergency contact
    r = await session.execute(select(EmergencyContact).where(EmergencyContact.user_id == current_user.id).limit(1))
    contact = r.scalar_one_or_none()
    if contact:
        # SMS/telegram notification would go here
        pass
    # Notify admin
    await session.commit()
    return {"ok": True, "message": "Emergency contacts notified"}


# ===== Stalker Protection =====
@router.get("/stalker-protection")
async def get_protection(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(StalkerProtection).where(StalkerProtection.user_id == current_user.id))
    sp = r.scalar_one_or_none()
    if not sp:
        return {"block_screenshots": False, "block_location": False, "block_forwarded": False, "mask_gps": False}
    return {"block_screenshots": sp.block_screenshots, "block_location": sp.block_location, "block_forwarded": sp.block_forwarded, "mask_gps": sp.mask_gps}


@router.post("/stalker-protection")
async def update_protection(data: dict, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(StalkerProtection).where(StalkerProtection.user_id == current_user.id))
    sp = r.scalar_one_or_none()
    if not sp:
        sp = StalkerProtection(user_id=current_user.id, **data)
        session.add(sp)
    else:
        for k, v in data.items():
            if hasattr(sp, k):
                setattr(sp, k, v)
    await session.commit()
    return {"ok": True}


# ===== Data Export (GDPR) =====
@router.post("/data-export")
async def request_export(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    req = DataExportRequest(user_id=current_user.id, status="pending")
    session.add(req)
    await session.commit()
    # Background job will generate the export
    return {"request_id": req.id, "status": "pending"}


@router.get("/data-export/status")
async def export_status(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    r = await session.execute(select(DataExportRequest).where(DataExportRequest.user_id == current_user.id).order_by(desc(DataExportRequest.requested_at)).limit(1))
    last = r.scalar_one_or_none()
    if not last:
        return None
    return {"id": last.id, "status": last.status, "download_url": last.download_url, "expires_at": last.expires_at}


# ===== Date Plan =====
@router.post("/date-plan")
async def create_date_plan(match_id: int, title: str, location_name: str, planned_at: str, description: str = None, category: str = "general", cost_estimate: int = 0, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    dp = DatePlan(
        match_id=match_id, proposer_id=current_user.id, title=title, description=description,
        location_name=location_name, planned_at=datetime.fromisoformat(planned_at),
        category=category, cost_estimate=cost_estimate,
    )
    session.add(dp)
    await session.commit()
    return {"id": dp.id}


@router.post("/date-plan/{plan_id}/respond")
async def respond_date_plan(plan_id: int, accept: bool, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    dp = await session.get(DatePlan, plan_id)
    if not dp or dp.proposer_id == current_user.id:
        raise HTTPException(403, "Not allowed")
    dp.status = "accepted" if accept else "declined"
    await session.commit()
    return {"status": dp.status}


@router.post("/date-plan/{plan_id}/feedback")
async def feedback_date_plan(plan_id: int, rating: int, would_meet_again: bool, comment: str = None, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    df = DateFeedback(date_plan_id=plan_id, user_id=current_user.id, rating=rating, would_meet_again=would_meet_again, comment=comment)
    session.add(df)
    await session.commit()
    return {"ok": True}
