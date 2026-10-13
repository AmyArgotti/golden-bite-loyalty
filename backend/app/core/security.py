from datetime import UTC, datetime, timedelta
from random import randint
from secrets import token_urlsafe

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def utcnow() -> datetime:
    return datetime.now(UTC)


def hash_secret(value: str) -> str:
    return pwd_context.hash(value)


def verify_secret(value: str, hashed_value: str) -> bool:
    return pwd_context.verify(value, hashed_value)


def generate_otp_code() -> str:
    return f"{randint(0, 999999):06d}"


def create_access_token(user_id: str, role: str) -> str:
    expires_at = utcnow() + timedelta(minutes=settings.access_token_ttl_min)
    payload = {"sub": user_id, "role": role, "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        return None


def generate_refresh_token() -> str:
    return token_urlsafe(32)
