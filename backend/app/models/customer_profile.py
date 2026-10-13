from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampedModel


class CustomerProfile(TimestampedModel, Base):
    __tablename__ = "customer_profiles"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    full_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True)
    referral_code: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    referred_by_profile_id: Mapped[UUID | None] = mapped_column(ForeignKey("customer_profiles.id"), nullable=True)
    marketing_sms_consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    privacy_policy_accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    terms_accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
