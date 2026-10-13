from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import Tiers
from app.db.base import Base, TimestampedModel


class LoyaltyAccount(TimestampedModel, Base):
    __tablename__ = "loyalty_accounts"

    customer_profile_id: Mapped[UUID] = mapped_column(ForeignKey("customer_profiles.id", ondelete="CASCADE"), unique=True)
    member_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    points_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lifetime_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tier: Mapped[str] = mapped_column(String(20), nullable=False, default=Tiers.BRONZE)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    qr_code_value: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    barcode_value: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    wallet_status: Mapped[str] = mapped_column(String(30), nullable=False, default="not_added")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
