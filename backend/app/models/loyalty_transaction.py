from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampedModel


class LoyaltyTransaction(TimestampedModel, Base):
    __tablename__ = "loyalty_transactions"

    loyalty_account_id: Mapped[UUID] = mapped_column(ForeignKey("loyalty_accounts.id", ondelete="CASCADE"))
    transaction_type: Mapped[str] = mapped_column(String(40), nullable=False)
    points_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    rub_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    order_reference: Mapped[str | None] = mapped_column(String(60), nullable=True)
    source: Mapped[str] = mapped_column(String(30), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    branch_id: Mapped[UUID | None] = mapped_column(nullable=True)
