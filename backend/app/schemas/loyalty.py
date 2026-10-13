from datetime import datetime

from app.schemas.common import AppBaseModel


class LoyaltyDashboardOut(AppBaseModel):
    member_id: str
    points_balance: int
    lifetime_points: int
    tier: str
    discount_percent: float
    qr_code_value: str
    barcode_value: str
    wallet_status: str

    @classmethod
    def example(cls) -> "LoyaltyDashboardOut":
        return cls(
            member_id="GB-100001",
            points_balance=1280,
            lifetime_points=1540,
            tier="silver",
            discount_percent=5,
            qr_code_value="GB-100001",
            barcode_value="100001",
            wallet_status="active",
        )


class LoyaltyTransactionOut(AppBaseModel):
    transaction_type: str
    points_delta: int
    rub_amount: float | None = None
    source: str
    comment: str | None = None
    created_at: datetime

    @classmethod
    def example(cls) -> "LoyaltyTransactionOut":
        return cls(
            transaction_type="earn",
            points_delta=135,
            rub_amount=1350.0,
            source="staff",
            comment="Order ORDER-1055",
            created_at=datetime(2026, 3, 25, 12, 0, 0),
        )


class LoyaltyCardOut(AppBaseModel):
    member_id: str
    qr_code_value: str
    barcode_value: str
    tier: str
    points_balance: int

    @classmethod
    def example(cls) -> "LoyaltyCardOut":
        return cls(
            member_id="GB-100001",
            qr_code_value="GB-100001",
            barcode_value="100001",
            tier="silver",
            points_balance=1280,
        )
