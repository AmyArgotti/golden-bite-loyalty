from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, staff_or_admin_required
from app.models.user import User
from app.schemas.staff import (
    CustomerSearchOut,
    StaffCustomerDetailOut,
    StaffScanIn,
    PurchaseCreateIn,
    PurchaseCreateOut,
    StaffAdjustmentIn,
    StaffOperationOut,
    StaffRedeemIn,
)
from app.services.adjustment_service import AdjustmentService
from app.services.purchase_service import PurchaseService
from app.services.redemption_service import RedemptionService
from app.services.staff_service import StaffService


router = APIRouter()


@router.get("/customers/search", response_model=list[CustomerSearchOut])
def search_customers(
    phone_number: str | None = Query(default=None),
    member_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(staff_or_admin_required),
) -> list[CustomerSearchOut]:
    return StaffService(db).search_customers(current_user, phone_number=phone_number, member_id=member_id)


@router.post("/customers/scan", response_model=StaffCustomerDetailOut)
def scan_customer(
    payload: StaffScanIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff_or_admin_required),
) -> StaffCustomerDetailOut:
    try:
        return StaffService(db).get_customer_by_scan(current_user, payload.scan_value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/customers/{customer_id}", response_model=StaffCustomerDetailOut)
def get_customer_detail(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff_or_admin_required),
) -> StaffCustomerDetailOut:
    try:
        return StaffService(db).get_customer_detail(current_user, customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/purchases", response_model=PurchaseCreateOut)
def register_purchase(
    payload: PurchaseCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff_or_admin_required),
) -> PurchaseCreateOut:
    return PurchaseService(db).register_purchase(current_user, payload)


@router.post("/redeem", response_model=StaffOperationOut)
def redeem_reward(
    payload: StaffRedeemIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff_or_admin_required),
) -> StaffOperationOut:
    return RedemptionService(db).redeem(current_user, payload)


@router.post("/adjust", response_model=StaffOperationOut)
def adjust_points(
    payload: StaffAdjustmentIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff_or_admin_required),
) -> StaffOperationOut:
    return AdjustmentService(db).adjust(current_user, payload)
