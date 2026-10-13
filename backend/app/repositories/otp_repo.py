from datetime import timedelta

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.core.security import utcnow
from app.models.otp_request import OTPRequest


class OTPRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count_recent_by_phone(self, phone_number: str, minutes: int) -> int:
        since = utcnow() - timedelta(minutes=minutes)
        stmt = select(func.count()).select_from(OTPRequest).where(
            OTPRequest.phone_number == phone_number,
            OTPRequest.created_at >= since,
        )
        return int(self.db.scalar(stmt) or 0)

    def latest_active_for_phone(self, phone_number: str) -> OTPRequest | None:
        stmt = (
            select(OTPRequest)
            .where(OTPRequest.phone_number == phone_number)
            .order_by(desc(OTPRequest.created_at))
        )
        return self.db.scalars(stmt).first()

    def create(self, otp_request: OTPRequest) -> OTPRequest:
        self.db.add(otp_request)
        self.db.flush()
        return otp_request
