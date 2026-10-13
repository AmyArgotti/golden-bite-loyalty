from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer_profile import CustomerProfile
from app.models.loyalty_account import LoyaltyAccount
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_phone(self, phone_number: str) -> User | None:
        stmt = select(User).where(User.phone_number == phone_number)
        return self.db.scalars(stmt).first()

    def get_profile_by_user_id(self, user_id) -> CustomerProfile | None:
        stmt = select(CustomerProfile).where(CustomerProfile.user_id == user_id)
        return self.db.scalars(stmt).first()

    def list_customer_profiles(self) -> list[CustomerProfile]:
        stmt = select(CustomerProfile).order_by(CustomerProfile.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def list_customer_bundles(self) -> list[tuple[User, CustomerProfile, LoyaltyAccount]]:
        stmt = (
            select(User, CustomerProfile, LoyaltyAccount)
            .join(CustomerProfile, CustomerProfile.user_id == User.id)
            .join(LoyaltyAccount, LoyaltyAccount.customer_profile_id == CustomerProfile.id)
            .where(User.role == "customer")
            .order_by(User.created_at.desc())
        )
        return list(self.db.execute(stmt).all())

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def create_profile(self, profile: CustomerProfile) -> CustomerProfile:
        self.db.add(profile)
        self.db.flush()
        return profile

    def search_customers(self, phone_number: str | None = None, member_id: str | None = None) -> list[tuple[User, CustomerProfile, LoyaltyAccount]]:
        stmt = (
            select(User, CustomerProfile, LoyaltyAccount)
            .join(CustomerProfile, CustomerProfile.user_id == User.id)
            .join(LoyaltyAccount, LoyaltyAccount.customer_profile_id == CustomerProfile.id)
            .where(User.role == "customer")
        )
        if phone_number:
            stmt = stmt.where(User.phone_number == phone_number)
        if member_id:
            stmt = stmt.where(LoyaltyAccount.member_id == member_id)
        if not phone_number and not member_id:
            stmt = stmt.limit(20)
        return list(self.db.execute(stmt).all())

    def get_customer_bundle(self, customer_user_id) -> tuple[User, CustomerProfile, LoyaltyAccount] | None:
        stmt = (
            select(User, CustomerProfile, LoyaltyAccount)
            .join(CustomerProfile, CustomerProfile.user_id == User.id)
            .join(LoyaltyAccount, LoyaltyAccount.customer_profile_id == CustomerProfile.id)
            .where(User.id == customer_user_id, User.role == "customer")
        )
        return self.db.execute(stmt).first()

    def get_customer_bundle_by_profile_id(self, profile_id) -> tuple[User, CustomerProfile, LoyaltyAccount] | None:
        stmt = (
            select(User, CustomerProfile, LoyaltyAccount)
            .join(CustomerProfile, CustomerProfile.user_id == User.id)
            .join(LoyaltyAccount, LoyaltyAccount.customer_profile_id == CustomerProfile.id)
            .where(CustomerProfile.id == profile_id, User.role == "customer")
        )
        return self.db.execute(stmt).first()

    def list_staff_and_admin_users(self) -> list[User]:
        stmt = (
            select(User)
            .where(User.role.in_(["staff", "admin", "super_admin"]))
            .order_by(User.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, user_id) -> User | None:
        return self.db.get(User, user_id)
