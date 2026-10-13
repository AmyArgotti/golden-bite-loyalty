from app.models.user import User
from app.repositories.loyalty_repo import LoyaltyRepository
from app.repositories.user_repo import UserRepository
from app.schemas.loyalty import LoyaltyTransactionOut
from app.schemas.staff import CustomerSearchOut, StaffCustomerDetailOut


class StaffService:
    def __init__(self, db) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.loyalty_repo = LoyaltyRepository(db)

    def search_customers(
        self,
        actor: User,
        phone_number: str | None = None,
        member_id: str | None = None,
    ) -> list[CustomerSearchOut]:
        _ = actor
        results: list[CustomerSearchOut] = []
        for user, _profile, account in self.user_repo.search_customers(phone_number=phone_number, member_id=member_id):
            results.append(
                CustomerSearchOut(
                    customer_id=str(user.id),
                    member_id=account.member_id,
                    phone_number=user.phone_number,
                    points_balance=account.points_balance,
                    tier=account.tier,
                )
            )
        return results

    def get_customer_detail(self, actor: User, customer_user_id) -> StaffCustomerDetailOut:
        _ = actor
        bundle = self.user_repo.get_customer_bundle(customer_user_id)
        if not bundle:
            raise ValueError("Customer not found")
        return self._build_customer_detail(bundle)

    def get_customer_by_scan(self, actor: User, scan_value: str) -> StaffCustomerDetailOut:
        _ = actor
        account = self.loyalty_repo.get_account_by_scan_value(scan_value)
        if not account:
            raise ValueError("Customer not found")
        bundle = self.user_repo.get_customer_bundle_by_profile_id(account.customer_profile_id)
        if not bundle:
            raise ValueError("Customer not found")
        return self._build_customer_detail(bundle)

    def _build_customer_detail(self, bundle) -> StaffCustomerDetailOut:
        user, _profile, account = bundle
        transactions = self.loyalty_repo.list_recent_transactions(account.id, limit=8)
        return StaffCustomerDetailOut(
            customer_id=str(user.id),
            member_id=account.member_id,
            phone_number=user.phone_number,
            points_balance=account.points_balance,
            lifetime_points=account.lifetime_points,
            tier=account.tier,
            discount_percent=float(account.discount_percent),
            qr_code_value=account.qr_code_value,
            barcode_value=account.barcode_value,
            recent_transactions=[
                LoyaltyTransactionOut(
                    transaction_type=item.transaction_type,
                    points_delta=item.points_delta,
                    rub_amount=float(item.rub_amount) if item.rub_amount is not None else None,
                    source=item.source,
                    comment=item.comment,
                    created_at=item.created_at,
                )
                for item in transactions
            ],
        )
