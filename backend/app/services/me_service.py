from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.me import MeOut, ProfileOut, ProfileUpdateIn


class MeService:
    def __init__(self, db) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def get_me(self, current_user: User) -> MeOut:
        profile = self.user_repo.get_profile_by_user_id(current_user.id)
        return MeOut(
            user_id=str(current_user.id),
            phone_number=current_user.phone_number,
            role=current_user.role,
            profile=ProfileOut(
                full_name=profile.full_name if profile else None,
                birthday=profile.birthday if profile else None,
                marketing_sms_consent=profile.marketing_sms_consent if profile else False,
            ),
        )

    def update_profile(self, current_user: User, payload: ProfileUpdateIn) -> MeOut:
        profile = self.user_repo.get_profile_by_user_id(current_user.id)
        profile.full_name = payload.full_name
        profile.birthday = payload.birthday
        profile.marketing_sms_consent = payload.marketing_sms_consent
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return self.get_me(current_user)
