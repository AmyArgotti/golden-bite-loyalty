from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.session import Session as UserSession


class SessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, session: UserSession) -> UserSession:
        self.db.add(session)
        self.db.flush()
        return session

    def list_active_by_user_id(self, user_id) -> list[UserSession]:
        stmt = select(UserSession).where(UserSession.user_id == user_id, UserSession.revoked_at.is_(None))
        return list(self.db.scalars(stmt).all())

    def list_active(self) -> list[UserSession]:
        stmt = select(UserSession).where(UserSession.revoked_at.is_(None))
        return list(self.db.scalars(stmt).all())
