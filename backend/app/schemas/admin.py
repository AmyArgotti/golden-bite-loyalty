from datetime import datetime

from app.schemas.common import AppBaseModel


class AdminDashboardOut(AppBaseModel):
    active_customers: int
    total_points_issued: int
    transactions_today: int
    pending_fraud_flags: int

    @classmethod
    def example(cls) -> "AdminDashboardOut":
        return cls(
            active_customers=128,
            total_points_issued=22450,
            transactions_today=42,
            pending_fraud_flags=1,
        )


class TierRuleOut(AppBaseModel):
    name: str
    min_points: int
    discount_percent: float


class LoyaltyRulesOut(AppBaseModel):
    points_per_rub_ratio: float
    tiers: list[TierRuleOut]
    first_order_bonus: int
    birthday_bonus: int
    referral_referrer_bonus: int
    referral_referee_bonus: int

    @classmethod
    def example(cls) -> "LoyaltyRulesOut":
        return cls(
            points_per_rub_ratio=0.1,
            tiers=[
                TierRuleOut(name="bronze", min_points=0, discount_percent=0),
                TierRuleOut(name="silver", min_points=1000, discount_percent=5),
                TierRuleOut(name="gold", min_points=3000, discount_percent=10),
            ],
            first_order_bonus=100,
            birthday_bonus=200,
            referral_referrer_bonus=150,
            referral_referee_bonus=100,
        )


class StaffSeedOut(AppBaseModel):
    admin_phone_number: str
    staff_phone_number: str
    note: str


class TierRuleIn(AppBaseModel):
    name: str
    min_points: int
    discount_percent: float


class LoyaltyRulesUpdateIn(AppBaseModel):
    points_per_rub_ratio: float
    tiers: list[TierRuleIn]
    first_order_bonus: int
    birthday_bonus: int
    referral_referrer_bonus: int
    referral_referee_bonus: int


class AdminStaffOut(AppBaseModel):
    id: str
    phone_number: str
    role: str
    is_active: bool
    phone_verified_at: datetime | None


class AdminStaffCreateIn(AppBaseModel):
    phone_number: str
    role: str
    is_active: bool = True


class AdminStaffUpdateIn(AppBaseModel):
    role: str | None = None
    is_active: bool | None = None


class FraudFlagOut(AppBaseModel):
    flag_type: str
    severity: str
    description: str
    related_value: str | None
    created_at: datetime


class AuditLogOut(AppBaseModel):
    id: str
    actor_user_id: str | None
    actor_role: str
    action: str
    entity_type: str
    entity_id: str | None
    before_data: dict | None
    after_data: dict | None
    ip_address: str | None
    created_at: datetime
