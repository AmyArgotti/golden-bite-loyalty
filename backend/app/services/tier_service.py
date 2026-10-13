from decimal import Decimal

from app.core.constants import Tiers


class TierService:
    @staticmethod
    def resolve(points_balance: int) -> tuple[str, Decimal]:
        if points_balance >= 3000:
            return (Tiers.GOLD, Decimal("10.00"))
        if points_balance >= 1000:
            return (Tiers.SILVER, Decimal("5.00"))
        return (Tiers.BRONZE, Decimal("0.00"))
