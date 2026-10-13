from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import (
    MessageOut,
    OTPRequestIn,
    OTPRequestOut,
    OTPVerifyIn,
    OTPVerifyOut,
    RefreshTokenIn,
    RefreshTokenOut,
)
from app.services.auth_service import AuthService


router = APIRouter()


@router.post("/request-otp", response_model=OTPRequestOut)
def request_otp(
    payload: OTPRequestIn,
    request: Request,
    x_device_fingerprint: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> OTPRequestOut:
    return AuthService(db).request_otp(
        payload,
        request_ip=request.client.host if request.client else None,
        device_fingerprint=x_device_fingerprint,
    )


@router.post("/verify-otp", response_model=OTPVerifyOut)
def verify_otp(payload: OTPVerifyIn, db: Session = Depends(get_db)) -> OTPVerifyOut:
    return AuthService(db).verify_otp(payload)


@router.post("/refresh", response_model=RefreshTokenOut)
def refresh_session(payload: RefreshTokenIn, db: Session = Depends(get_db)) -> RefreshTokenOut:
    return AuthService(db).refresh_session(payload)


@router.post("/logout", response_model=MessageOut)
def logout(payload: RefreshTokenIn, db: Session = Depends(get_db)) -> MessageOut:
    return AuthService(db).logout(payload)
