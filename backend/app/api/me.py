from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.me import MeOut, ProfileUpdateIn
from app.services.me_service import MeService


router = APIRouter()


@router.get("/me", response_model=MeOut)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MeOut:
    return MeService(db).get_me(current_user)


@router.patch("/me/profile", response_model=MeOut)
def update_profile(
    payload: ProfileUpdateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeOut:
    return MeService(db).update_profile(current_user, payload)
