import json
from pathlib import Path

from app.core.config import settings


class LoyaltyConfigRepository:
    DEFAULT_RULES = {
        "points_per_rub_ratio": 0.1,
        "tiers": [
            {"name": "bronze", "min_points": 0, "discount_percent": 0},
            {"name": "silver", "min_points": 1000, "discount_percent": 5},
            {"name": "gold", "min_points": 3000, "discount_percent": 10},
        ],
        "first_order_bonus": 100,
        "birthday_bonus": 200,
        "referral_referrer_bonus": 150,
        "referral_referee_bonus": 100,
    }

    def get_rules(self) -> dict:
        path = Path(settings.loyalty_rules_path)
        if not path.exists():
            return self.DEFAULT_RULES.copy()
        return json.loads(path.read_text(encoding="utf-8"))

    def save_rules(self, rules: dict) -> dict:
        path = Path(settings.loyalty_rules_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rules, indent=2), encoding="utf-8")
        return rules
