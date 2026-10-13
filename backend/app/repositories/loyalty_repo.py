from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.loyalty_account import LoyaltyAccount
from app.models.loyalty_transaction import LoyaltyTransaction


class LoyaltyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_account_by_profile_id(self, profile_id) -> LoyaltyAccount | None:
        stmt = select(LoyaltyAccount).where(LoyaltyAccount.customer_profile_id == profile_id)
        return self.db.scalars(stmt).first()

    def create_account(self, account: LoyaltyAccount) -> LoyaltyAccount:
        self.db.add(account)
        self.db.flush()
        return account

    def create_transaction(self, transaction: LoyaltyTransaction) -> LoyaltyTransaction:
        self.db.add(transaction)
        self.db.flush()
        return transaction

    def count_transactions_by_type(self, loyalty_account_id, transaction_type: str) -> int:
        stmt = select(func.count()).select_from(LoyaltyTransaction).where(
            LoyaltyTransaction.loyalty_account_id == loyalty_account_id,
            LoyaltyTransaction.transaction_type == transaction_type,
        )
        return int(self.db.scalar(stmt) or 0)

    def list_transactions(self, loyalty_account_id) -> list[LoyaltyTransaction]:
        stmt = (
            select(LoyaltyTransaction)
            .where(LoyaltyTransaction.loyalty_account_id == loyalty_account_id)
            .order_by(LoyaltyTransaction.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_recent_transactions(self, loyalty_account_id, limit: int = 10) -> list[LoyaltyTransaction]:
        stmt = (
            select(LoyaltyTransaction)
            .where(LoyaltyTransaction.loyalty_account_id == loyalty_account_id)
            .order_by(LoyaltyTransaction.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_account_by_scan_value(self, scan_value: str) -> LoyaltyAccount | None:
        stmt = select(LoyaltyAccount).where(
            or_(
                LoyaltyAccount.member_id == scan_value,
                LoyaltyAccount.qr_code_value == scan_value,
                LoyaltyAccount.barcode_value == scan_value,
            )
        )
        return self.db.scalars(stmt).first()
