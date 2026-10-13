from decimal import Decimal
from math import floor

from fastapi import HTTPException, status

from app.core.security import utcnow
from app.models.audit_log import AuditLog
from app.models.loyalty_transaction import LoyaltyTransaction
from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.loyalty_repo import LoyaltyRepository
from app.repositories.user_repo import UserRepository
from app.schemas.staff import PurchaseCreateIn, PurchaseCreateOut
from app.services.tier_service import TierService
from app.services.wallet_service import WalletService


class PurchaseService:
    FIRST_ORDER_BONUS = 100

    def __init__(self, db) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.loyalty_repo = LoyaltyRepository(db)
        self.audit_repo = AuditRepository(db)
        self.wallet_service = WalletService(db)

    def register_purchase(self, actor: User, payload: PurchaseCreateIn) -> PurchaseCreateOut:
        if payload.purchase_amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Purchase amount must be positive")

        profile = self.user_repo.get_profile_by_user_id(payload.customer_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")

        account = self.loyalty_repo.get_account_by_profile_id(profile.id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loyalty account not found")

        before_state = {
            "points_balance": account.points_balance,
            "lifetime_points": account.lifetime_points,
            "tier": account.tier,
            "discount_percent": str(account.discount_percent),
        }

        earned_points = floor(payload.purchase_amount / 10)
        is_first_paid_order = self.loyalty_repo.count_transactions_by_type(account.id, "earn") == 0
        bonus_points = self.FIRST_ORDER_BONUS if is_first_paid_order and payload.purchase_amount > 0 else 0
        total_points_added = earned_points + bonus_points

        account.points_balance += total_points_added
        account.lifetime_points += total_points_added
        account.last_activity_at = utcnow()
        account.tier, account.discount_percent = TierService.resolve(account.points_balance)
        self.db.add(account)

        self.loyalty_repo.create_transaction(
            LoyaltyTransaction(
                loyalty_account_id=account.id,
                transaction_type="earn",
                points_delta=earned_points,
                rub_amount=Decimal(str(payload.purchase_amount)),
                order_reference=payload.order_reference,
                source="staff",
                comment=f"Purchase registered by staff for {payload.purchase_amount:.2f} RUB",
                created_by_user_id=actor.id,
                branch_id=payload.branch_id,
            )
        )

        if bonus_points:
            self.loyalty_repo.create_transaction(
                LoyaltyTransaction(
                    loyalty_account_id=account.id,
                    transaction_type="first_order_bonus",
                    points_delta=bonus_points,
                    rub_amount=None,
                    order_reference=payload.order_reference,
                    source="system",
                    comment="First paid order bonus",
                    created_by_user_id=actor.id,
                    branch_id=payload.branch_id,
                )
            )

        after_state = {
            "points_balance": account.points_balance,
            "lifetime_points": account.lifetime_points,
            "tier": account.tier,
            "discount_percent": str(account.discount_percent),
        }
        self.audit_repo.create(
            AuditLog(
                actor_user_id=actor.id,
                actor_role=actor.role,
                action="staff.register_purchase",
                entity_type="loyalty_account",
                entity_id=account.id,
                before_data=before_state,
                after_data=after_state,
            )
        )
        self.wallet_service.sync_account_pass(account)
        self.db.commit()
        self.db.refresh(account)

        return PurchaseCreateOut(
            earned_points=earned_points,
            bonus_points=bonus_points,
            total_points_added=total_points_added,
            new_points_balance=account.points_balance,
            new_tier=account.tier,
            discount_percent=float(account.discount_percent),
        )
