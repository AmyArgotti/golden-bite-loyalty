from uuid import UUID

from app.schemas.common import AppBaseModel
from app.schemas.loyalty import LoyaltyTransactionOut


class CustomerSearchOut(AppBaseModel):
    customer_id: str
    member_id: str
    phone_number: str
    points_balance: int
    tier: str

    @classmethod
    def example(cls) -> "CustomerSearchOut":
        return cls(
            customer_id="00000000-0000-0000-0000-000000000101",
            member_id="GB-100001",
            phone_number="+79991234567",
            points_balance=1280,
            tier="silver",
        )


class PurchaseCreateIn(AppBaseModel):
    customer_id: UUID
    purchase_amount: float
    branch_id: UUID | None = None
    order_reference: str | None = None


class PurchaseCreateOut(AppBaseModel):
    earned_points: int
    bonus_points: int
    total_points_added: int
    new_points_balance: int
    new_tier: str
    discount_percent: float

    @classmethod
    def from_purchase(cls, payload: PurchaseCreateIn) -> "PurchaseCreateOut":
        earned_points = int(payload.purchase_amount // 10)
        new_points_balance = 1280 + earned_points
        new_tier = "silver" if new_points_balance < 3000 else "gold"
        discount_percent = 5 if new_tier == "silver" else 10
        return cls(
            earned_points=earned_points,
            bonus_points=0,
            total_points_added=earned_points,
            new_points_balance=new_points_balance,
            new_tier=new_tier,
            discount_percent=discount_percent,
        )


class StaffRedeemIn(AppBaseModel):
    customer_id: UUID
    points_to_redeem: int
    comment: str | None = None


class StaffAdjustmentIn(AppBaseModel):
    customer_id: UUID
    points_delta: int
    comment: str


class StaffOperationOut(AppBaseModel):
    message: str
    points_balance: int
    tier: str
    discount_percent: float


class StaffCustomerDetailOut(AppBaseModel):
    customer_id: str
    member_id: str
    phone_number: str
    points_balance: int
    lifetime_points: int
    tier: str
    discount_percent: float
    qr_code_value: str
    barcode_value: str
    recent_transactions: list[LoyaltyTransactionOut]


class StaffScanIn(AppBaseModel):
    scan_value: str
