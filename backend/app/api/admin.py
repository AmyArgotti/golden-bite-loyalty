from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.core.constants import Roles
from app.schemas.admin import (
    AdminDashboardOut,
    AdminStaffCreateIn,
    AdminStaffOut,
    AdminStaffUpdateIn,
    AuditLogOut,
    FraudFlagOut,
    LoyaltyRulesOut,
    LoyaltyRulesUpdateIn,
)
from app.services.admin_service import AdminService


router = APIRouter()
admin_required = require_roles(Roles.ADMIN, Roles.SUPER_ADMIN)


@router.get("/dashboard", response_model=AdminDashboardOut)
def get_dashboard(
    db: Session = Depends(get_db),
    _current_user=Depends(admin_required),
) -> AdminDashboardOut:
    return AdminService(db).get_dashboard()


@router.get("/config/loyalty-rules", response_model=LoyaltyRulesOut)
def get_loyalty_rules(
    db: Session = Depends(get_db),
    _current_user=Depends(admin_required),
) -> LoyaltyRulesOut:
    return AdminService(db).get_loyalty_rules()


@router.patch("/config/loyalty-rules", response_model=LoyaltyRulesOut)
def update_loyalty_rules(
    payload: LoyaltyRulesUpdateIn,
    db: Session = Depends(get_db),
    _current_user=Depends(admin_required),
) -> LoyaltyRulesOut:
    return AdminService(db).update_loyalty_rules(payload)


@router.get("/staff", response_model=list[AdminStaffOut])
def list_staff(
    db: Session = Depends(get_db),
    _current_user=Depends(admin_required),
) -> list[AdminStaffOut]:
    return AdminService(db).list_staff()


@router.post("/staff", response_model=AdminStaffOut)
def create_staff(
    payload: AdminStaffCreateIn,
    db: Session = Depends(get_db),
    _current_user=Depends(admin_required),
) -> AdminStaffOut:
    return AdminService(db).create_staff(payload)


@router.patch("/staff/{staff_id}", response_model=AdminStaffOut)
def update_staff(
    staff_id: UUID,
    payload: AdminStaffUpdateIn,
    db: Session = Depends(get_db),
    _current_user=Depends(admin_required),
) -> AdminStaffOut:
    try:
        return AdminService(db).update_staff(staff_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(
    db: Session = Depends(get_db),
    _current_user=Depends(admin_required),
) -> list[AuditLogOut]:
    return AdminService(db).list_audit_logs()


@router.get("/fraud-flags", response_model=list[FraudFlagOut])
def list_fraud_flags(
    db: Session = Depends(get_db),
    _current_user=Depends(admin_required),
) -> list[FraudFlagOut]:
    return AdminService(db).list_fraud_flags()


@router.get("/customers/export")
def export_customers(
    db: Session = Depends(get_db),
    _current_user=Depends(admin_required),
) -> PlainTextResponse:
    csv_data = AdminService(db).export_customers_csv()
    headers = {"Content-Disposition": 'attachment; filename="golden-bite-customers.csv"'}
    return PlainTextResponse(content=csv_data, media_type="text/csv", headers=headers)
