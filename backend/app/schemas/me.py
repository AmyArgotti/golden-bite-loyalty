from datetime import date

from app.schemas.common import AppBaseModel


class ProfileOut(AppBaseModel):
    full_name: str | None = None
    birthday: date | None = None
    marketing_sms_consent: bool = False


class MeOut(AppBaseModel):
    user_id: str
    phone_number: str
    role: str
    profile: ProfileOut

    @classmethod
    def example(cls) -> "MeOut":
        return cls(
            user_id="00000000-0000-0000-0000-000000000001",
            phone_number="+79991234567",
            role="customer",
            profile=ProfileOut(full_name="Golden Bite Member", birthday=None, marketing_sms_consent=False),
        )

    @classmethod
    def from_profile_update(cls, payload: "ProfileUpdateIn") -> "MeOut":
        return cls(
            user_id="00000000-0000-0000-0000-000000000001",
            phone_number="+79991234567",
            role="customer",
            profile=ProfileOut(**payload.model_dump()),
        )


class ProfileUpdateIn(AppBaseModel):
    full_name: str | None = None
    birthday: date | None = None
    marketing_sms_consent: bool = False
