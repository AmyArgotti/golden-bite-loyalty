from app.db.base import Base
from app.db.session import engine
from app.models import AuditLog, CustomerProfile, LoyaltyAccount, LoyaltyTransaction, OTPRequest, Session, User


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
