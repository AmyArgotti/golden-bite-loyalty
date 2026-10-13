from decimal import Decimal

from app.services.tier_service import TierService


def test_tier_service_resolves_bronze() -> None:
    assert TierService.resolve(999) == ("bronze", Decimal("0.00"))


def test_tier_service_resolves_silver() -> None:
    assert TierService.resolve(1000) == ("silver", Decimal("5.00"))


def test_tier_service_resolves_gold() -> None:
    assert TierService.resolve(3000) == ("gold", Decimal("10.00"))
