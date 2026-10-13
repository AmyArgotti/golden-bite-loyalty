from app.core.constants import Roles
from app.core.config import settings
from app.core.security import utcnow
from app.db.session import SessionLocal
from app.models.user import User


def seed_users() -> dict[str, str]:
    db = SessionLocal()
    try:
        admin_phone_number = settings.seed_admin_phone_number
        staff_phone_number = settings.seed_staff_phone_number

        admin = db.query(User).filter(User.phone_number == admin_phone_number).first()
        if not admin:
            admin = User(
                phone_number=admin_phone_number,
                role=Roles.ADMIN,
                is_active=True,
                phone_verified_at=utcnow(),
            )
            db.add(admin)

        staff = db.query(User).filter(User.phone_number == staff_phone_number).first()
        if not staff:
            staff = User(
                phone_number=staff_phone_number,
                role=Roles.STAFF,
                is_active=True,
                phone_verified_at=utcnow(),
            )
            db.add(staff)

        db.commit()
        return {
            "admin_phone_number": admin_phone_number,
            "staff_phone_number": staff_phone_number,
            "note": "Use these seeded users for role-protected API testing.",
        }
    finally:
        db.close()


if __name__ == "__main__":
    print(seed_users())
