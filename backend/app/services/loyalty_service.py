from app.models.user import User
from app.repositories.loyalty_repo import LoyaltyRepository
from app.repositories.user_repo import UserRepository
from app.schemas.loyalty import LoyaltyCardOut, LoyaltyDashboardOut, LoyaltyTransactionOut


class LoyaltyService:
    def __init__(self, db) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.loyalty_repo = LoyaltyRepository(db)

    def get_dashboard(self, current_user: User) -> LoyaltyDashboardOut:
        profile = self.user_repo.get_profile_by_user_id(current_user.id)
        account = self.loyalty_repo.get_account_by_profile_id(profile.id)
        return LoyaltyDashboardOut(
            member_id=account.member_id,
            points_balance=account.points_balance,
            lifetime_points=account.lifetime_points,
            tier=account.tier,
            discount_percent=float(account.discount_percent),
            qr_code_value=account.qr_code_value,
            barcode_value=account.barcode_value,
            wallet_status=account.wallet_status,
        )

    def get_transactions(self, current_user: User) -> list[LoyaltyTransactionOut]:
        profile = self.user_repo.get_profile_by_user_id(current_user.id)
        account = self.loyalty_repo.get_account_by_profile_id(profile.id)
        transactions = self.loyalty_repo.list_transactions(account.id)
        return [
            LoyaltyTransactionOut(
                transaction_type=item.transaction_type,
                points_delta=item.points_delta,
                rub_amount=float(item.rub_amount) if item.rub_amount is not None else None,
                source=item.source,
                comment=item.comment,
                created_at=item.created_at,
            )
            for item in transactions
        ]

    def get_card(self, current_user: User) -> LoyaltyCardOut:
        profile = self.user_repo.get_profile_by_user_id(current_user.id)
        account = self.loyalty_repo.get_account_by_profile_id(profile.id)
        return LoyaltyCardOut(
            member_id=account.member_id,
            qr_code_value=account.qr_code_value,
            barcode_value=account.barcode_value,
            tier=account.tier,
            points_balance=account.points_balance,
        )
