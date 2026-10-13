from fastapi import HTTPException, status

from app.core.security import utcnow
from app.models.audit_log import AuditLog
from app.models.loyalty_transaction import LoyaltyTransaction
from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.loyalty_repo import LoyaltyRepository
from app.repositories.user_repo import UserRepository
from app.schemas.staff import StaffAdjustmentIn, StaffOperationOut
from app.services.tier_service import TierService
from app.services.wallet_service import WalletService


class AdjustmentService:
    def __init__(self, db) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.loyalty_repo = LoyaltyRepository(db)
        self.audit_repo = AuditRepository(db)
        self.wallet_service = WalletService(db)

    def adjust(self, actor: User, payload: StaffAdjustmentIn) -> StaffOperationOut:
        if actor.role == "staff" and not payload.comment.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment is required")

        profile = self.user_repo.get_profile_by_user_id(payload.customer_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")

        account = self.loyalty_repo.get_account_by_profile_id(profile.id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loyalty account not found")

        if account.points_balance + payload.points_delta < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Adjustment would make balance negative")

        before_state = {
            "points_balance": account.points_balance,
            "tier": account.tier,
            "discount_percent": str(account.discount_percent),
        }
        account.points_balance += payload.points_delta
        if payload.points_delta > 0:
            account.lifetime_points += payload.points_delta
        account.last_activity_at = utcnow()
        account.tier, account.discount_percent = TierService.resolve(account.points_balance)
        self.db.add(account)
        self.loyalty_repo.create_transaction(
            LoyaltyTransaction(
                loyalty_account_id=account.id,
                transaction_type="manual_adjustment",
                points_delta=payload.points_delta,
                source="staff",
                comment=payload.comment,
                created_by_user_id=actor.id,
            )
        )
        self.audit_repo.create(
            AuditLog(
                actor_user_id=actor.id,
                actor_role=actor.role,
                action="staff.adjust",
                entity_type="loyalty_account",
                entity_id=account.id,
                before_data=before_state,
                after_data={
                    "points_balance": account.points_balance,
                    "tier": account.tier,
                    "discount_percent": str(account.discount_percent),
                },
            )
        )
        self.wallet_service.sync_account_pass(account)
        self.db.commit()
        self.db.refresh(account)
        return StaffOperationOut(
            message="Adjustment recorded",
            points_balance=account.points_balance,
            tier=account.tier,
            discount_percent=float(account.discount_percent),
        )
