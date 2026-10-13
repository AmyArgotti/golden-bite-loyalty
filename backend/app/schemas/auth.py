from pydantic import Field

from app.core.constants import Roles
from app.schemas.common import AppBaseModel


class OTPRequestIn(AppBaseModel):
    phone_number: str = Field(..., examples=["+79991234567"])
    purpose: str = Field(..., examples=["register"])


class OTPRequestOut(AppBaseModel):
    message: str
    expires_in_seconds: int


class AuthUserOut(AppBaseModel):
    id: str
    role: str = Roles.CUSTOMER


class OTPVerifyIn(AppBaseModel):
    phone_number: str
    otp_code: str


class OTPVerifyOut(AppBaseModel):
    access_token: str
    refresh_token: str
    user: AuthUserOut
    is_new_user: bool


class RefreshTokenIn(AppBaseModel):
    refresh_token: str


class RefreshTokenOut(AppBaseModel):
    access_token: str


class MessageOut(AppBaseModel):
    message: str
