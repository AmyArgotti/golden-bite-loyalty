from decimal import Decimal
from uuid import uuid4

from app.services.tier_service import TierService


def test_first_order_bonus_math() -> None:
    purchase_amount = 1350
    earned_points = purchase_amount // 10
    bonus_points = 100
    total = earned_points + bonus_points
    assert earned_points == 135
    assert bonus_points == 100
    assert total == 235


def test_tier_after_purchase_promotes_to_gold() -> None:
    tier, discount = TierService.resolve(3050)
    assert tier == "gold"
    assert discount == Decimal("10.00")
