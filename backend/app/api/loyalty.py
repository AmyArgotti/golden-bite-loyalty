from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.loyalty import LoyaltyCardOut, LoyaltyDashboardOut, LoyaltyTransactionOut
from app.services.loyalty_service import LoyaltyService


router = APIRouter()


@router.get("/me/loyalty", response_model=LoyaltyDashboardOut)
def get_loyalty_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LoyaltyDashboardOut:
    return LoyaltyService(db).get_dashboard(current_user)


@router.get("/me/transactions", response_model=list[LoyaltyTransactionOut])
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[LoyaltyTransactionOut]:
    return LoyaltyService(db).get_transactions(current_user)


@router.get("/me/card", response_model=LoyaltyCardOut)
def get_card(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> LoyaltyCardOut:
    return LoyaltyService(db).get_card(current_user)
