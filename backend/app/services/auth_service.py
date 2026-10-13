from dataclasses import dataclass
from datetime import timedelta
from uuid import uuid4

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.constants import Roles
from app.core.rate_limit import rate_limiter
from app.core.security import (
    create_access_token,
    generate_otp_code,
    generate_refresh_token,
    hash_secret,
    utcnow,
    verify_secret,
)
from app.db.session import SessionLocal
from app.models.audit_log import AuditLog
from app.models.customer_profile import CustomerProfile
from app.models.loyalty_account import LoyaltyAccount
from app.models.otp_request import OTPRequest
from app.models.session import Session as UserSession
from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.loyalty_repo import LoyaltyRepository
from app.repositories.otp_repo import OTPRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import (
    AuthUserOut,
    MessageOut,
    OTPRequestIn,
    OTPRequestOut,
    OTPVerifyIn,
    OTPVerifyOut,
    RefreshTokenIn,
    RefreshTokenOut,
)
from app.services.sms_service import SMSDeliveryError, SMSService


@dataclass
class OTPRequestContext:
    request_ip: str | None = None
    device_fingerprint: str | None = None


class AuthService:
    def __init__(self, db) -> None:
        self.db = db
        self.otp_repo = OTPRepository(db)
        self.user_repo = UserRepository(db)
        self.loyalty_repo = LoyaltyRepository(db)
        self.session_repo = SessionRepository(db)
        self.audit_repo = AuditRepository(db)
        self.sms_service = SMSService()

    def request_otp(
        self,
        payload: OTPRequestIn,
        request_ip: str | None = None,
        device_fingerprint: str | None = None,
    ) -> OTPRequestOut:
        context = OTPRequestContext(request_ip=request_ip, device_fingerprint=device_fingerprint)

        recent_requests = self.otp_repo.count_recent_by_phone(
            payload.phone_number,
            minutes=settings.rate_limit_otp_phone_window_minutes,
        )
        if recent_requests >= settings.rate_limit_otp_per_phone:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OTP requests for this phone number",
            )

        self._enforce_rate_limits(payload.phone_number, context)

        otp_code = generate_otp_code()
        otp_request = OTPRequest(
            phone_number=payload.phone_number,
            otp_hash=hash_secret(otp_code),
            purpose=payload.purpose,
            expires_at=utcnow() + timedelta(seconds=settings.otp_ttl_seconds),
            max_attempts=settings.otp_max_attempts,
            request_ip=context.request_ip,
            device_fingerprint=context.device_fingerprint,
        )
        self.otp_repo.create(otp_request)
        try:
            delivery = self.sms_service.send_otp(payload.phone_number, otp_code)
            self.db.commit()
            self._write_system_audit_event(
                action="auth.send_otp",
                entity_type="otp_request",
                entity_id=otp_request.id,
                after_data={
                    "phone_number": payload.phone_number,
                    "provider": delivery.provider,
                    "delivery_status": delivery.status,
                    "external_id": delivery.external_id,
                },
                ip_address=context.request_ip,
            )
        except SMSDeliveryError as exc:
            self.db.rollback()
            self._write_system_audit_event(
                action="auth.send_otp_failed",
                entity_type="otp_request",
                entity_id=None,
                after_data={
                    "phone_number": payload.phone_number,
                    "provider": settings.sms_provider,
                    "error": str(exc),
                },
                ip_address=context.request_ip,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        message = "OTP sent"
        if settings.app_env != "production":
            message = f"OTP sent to {payload.phone_number}. Demo code: {otp_code}"
        return OTPRequestOut(
            message=message,
            expires_in_seconds=settings.otp_ttl_seconds,
        )

    def verify_otp(self, payload: OTPVerifyIn) -> OTPVerifyOut:
        otp_request = self.otp_repo.latest_active_for_phone(payload.phone_number)
        if not otp_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OTP request not found")

        if otp_request.used_at is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP already used")

        if otp_request.expires_at < utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")

        if otp_request.attempts_count >= otp_request.max_attempts:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP max attempts exceeded")

        otp_request.attempts_count += 1
        if not verify_secret(payload.otp_code, otp_request.otp_hash):
            self.db.add(otp_request)
            self.db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

        otp_request.used_at = utcnow()
        user = self.user_repo.get_by_phone(payload.phone_number)
        is_new_user = user is None
        if is_new_user:
            user = self.user_repo.create_user(
                User(phone_number=payload.phone_number, role=Roles.CUSTOMER, is_active=True, phone_verified_at=utcnow())
            )
            profile = self.user_repo.create_profile(
                CustomerProfile(
                    user_id=user.id,
                    referral_code=f"GB-{str(uuid4()).split('-')[0].upper()}",
                )
            )
            self.loyalty_repo.create_account(
                LoyaltyAccount(
                    customer_profile_id=profile.id,
                    member_id=self._build_member_id(),
                    qr_code_value=str(user.id),
                    barcode_value=str(user.id.int)[:12],
                )
            )
        else:
            user.phone_verified_at = utcnow()

        refresh_token = generate_refresh_token()
        self.session_repo.create(
            UserSession(
                user_id=user.id,
                refresh_token_hash=hash_secret(refresh_token),
                expires_at=utcnow() + timedelta(days=settings.refresh_token_ttl_days),
            )
        )
        self.audit_repo.create(
            AuditLog(
                actor_user_id=user.id,
                actor_role=user.role,
                action="auth.verify_otp",
                entity_type="user",
                entity_id=user.id,
                after_data={"phone_number": user.phone_number},
            )
        )
        self.db.add(otp_request)
        self.db.commit()
        self.db.refresh(user)
        return OTPVerifyOut(
            access_token=create_access_token(str(user.id), user.role),
            refresh_token=refresh_token,
            user=AuthUserOut(id=str(user.id), role=user.role),
            is_new_user=is_new_user,
        )

    def refresh_session(self, payload: RefreshTokenIn) -> RefreshTokenOut:
        now = utcnow()
        for session in self.session_repo.list_active():
            if session.expires_at < now:
                continue
            if verify_secret(payload.refresh_token, session.refresh_token_hash):
                user = self.db.get(User, session.user_id)
                if not user or not user.is_active:
                    break
                return RefreshTokenOut(access_token=create_access_token(str(user.id), user.role))

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    def logout(self, payload: RefreshTokenIn) -> MessageOut:
        for session in self.session_repo.list_active():
            if verify_secret(payload.refresh_token, session.refresh_token_hash):
                session.revoked_at = utcnow()
                self.db.add(session)
                self.db.commit()
                return MessageOut(message="Logged out")

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    def _build_member_id(self) -> str:
        count = self.db.query(LoyaltyAccount).count() + 100001
        return f"GB-{count}"

    def _enforce_rate_limits(self, phone_number: str, context: OTPRequestContext) -> None:
        phone_key = f"otp:phone:{phone_number}"
        phone_result = rate_limiter.allow(
            phone_key,
            limit=settings.rate_limit_otp_per_phone,
            window_seconds=settings.rate_limit_otp_phone_window_minutes * 60,
        )
        if not phone_result.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OTP requests for this phone number",
            )

        if context.request_ip:
            ip_key = f"otp:ip:{context.request_ip}"
            ip_result = rate_limiter.allow(
                ip_key,
                limit=settings.rate_limit_otp_per_ip,
                window_seconds=settings.rate_limit_otp_ip_window_minutes * 60,
            )
            if not ip_result.allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many OTP requests from this IP",
                )

        if context.device_fingerprint:
            device_key = f"otp:device:{context.device_fingerprint}"
            device_result = rate_limiter.allow(
                device_key,
                limit=settings.rate_limit_otp_per_device,
                window_seconds=settings.rate_limit_otp_ip_window_minutes * 60,
            )
            if not device_result.allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many OTP requests from this device",
                )

    def _write_system_audit_event(
        self,
        action: str,
        entity_type: str,
        entity_id,
        after_data: dict,
        ip_address: str | None,
    ) -> None:
        audit_db = SessionLocal()
        try:
            AuditRepository(audit_db).create(
                AuditLog(
                    actor_user_id=None,
                    actor_role="system",
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    after_data=after_data,
                    ip_address=ip_address,
                )
            )
            audit_db.commit()
        except Exception:
            audit_db.rollback()
        finally:
            audit_db.close()
