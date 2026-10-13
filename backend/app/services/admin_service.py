import csv
from io import StringIO
from datetime import timedelta

from sqlalchemy import distinct, func, select

from app.models.loyalty_transaction import LoyaltyTransaction
from app.models.otp_request import OTPRequest
from app.models.user import User
from app.core.security import utcnow
from app.repositories.audit_repo import AuditRepository
from app.repositories.config_repo import LoyaltyConfigRepository
from app.repositories.user_repo import UserRepository
from app.schemas.admin import (
    AdminDashboardOut,
    AdminStaffCreateIn,
    AdminStaffOut,
    AdminStaffUpdateIn,
    AuditLogOut,
    FraudFlagOut,
    LoyaltyRulesOut,
    LoyaltyRulesUpdateIn,
    TierRuleOut,
)


class AdminService:
    def __init__(self, db) -> None:
        self.db = db
        self.config_repo = LoyaltyConfigRepository()
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    def get_dashboard(self) -> AdminDashboardOut:
        now = utcnow()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        active_customers = int(self.db.scalar(select(func.count()).select_from(User).where(User.role == "customer")) or 0)
        total_points_issued = int(
            self.db.scalar(
                select(func.coalesce(func.sum(LoyaltyTransaction.points_delta), 0)).where(LoyaltyTransaction.points_delta > 0)
            )
            or 0
        )
        transactions_today = int(
            self.db.scalar(
                select(func.count()).select_from(LoyaltyTransaction).where(LoyaltyTransaction.created_at >= day_start)
            )
            or 0
        )
        pending_fraud_flags = len(self.list_fraud_flags())
        return AdminDashboardOut(
            active_customers=active_customers,
            total_points_issued=total_points_issued,
            transactions_today=transactions_today,
            pending_fraud_flags=pending_fraud_flags,
        )

    def get_loyalty_rules(self) -> LoyaltyRulesOut:
        rules = self.config_repo.get_rules()
        return LoyaltyRulesOut(
            points_per_rub_ratio=rules["points_per_rub_ratio"],
            tiers=[TierRuleOut(**tier) for tier in rules["tiers"]],
            first_order_bonus=rules["first_order_bonus"],
            birthday_bonus=rules["birthday_bonus"],
            referral_referrer_bonus=rules["referral_referrer_bonus"],
            referral_referee_bonus=rules["referral_referee_bonus"],
        )

    def update_loyalty_rules(self, payload: LoyaltyRulesUpdateIn) -> LoyaltyRulesOut:
        saved = self.config_repo.save_rules(payload.model_dump())
        return LoyaltyRulesOut(
            points_per_rub_ratio=saved["points_per_rub_ratio"],
            tiers=[TierRuleOut(**tier) for tier in saved["tiers"]],
            first_order_bonus=saved["first_order_bonus"],
            birthday_bonus=saved["birthday_bonus"],
            referral_referrer_bonus=saved["referral_referrer_bonus"],
            referral_referee_bonus=saved["referral_referee_bonus"],
        )

    def list_staff(self) -> list[AdminStaffOut]:
        users = self.user_repo.list_staff_and_admin_users()
        return [
            AdminStaffOut(
                id=str(user.id),
                phone_number=user.phone_number,
                role=user.role,
                is_active=user.is_active,
                phone_verified_at=user.phone_verified_at,
            )
            for user in users
        ]

    def create_staff(self, payload: AdminStaffCreateIn) -> AdminStaffOut:
        user = User(
            phone_number=payload.phone_number,
            role=payload.role,
            is_active=payload.is_active,
            phone_verified_at=utcnow(),
        )
        self.user_repo.create_user(user)
        self.db.commit()
        self.db.refresh(user)
        return AdminStaffOut(
            id=str(user.id),
            phone_number=user.phone_number,
            role=user.role,
            is_active=user.is_active,
            phone_verified_at=user.phone_verified_at,
        )

    def update_staff(self, staff_id, payload: AdminStaffUpdateIn) -> AdminStaffOut:
        user = self.user_repo.get_by_id(staff_id)
        if not user:
            raise ValueError("Staff user not found")
        if payload.role is not None:
            user.role = payload.role
        if payload.is_active is not None:
            user.is_active = payload.is_active
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return AdminStaffOut(
            id=str(user.id),
            phone_number=user.phone_number,
            role=user.role,
            is_active=user.is_active,
            phone_verified_at=user.phone_verified_at,
        )

    def list_audit_logs(self) -> list[AuditLogOut]:
        logs = self.audit_repo.list_recent(limit=50)
        return [
            AuditLogOut(
                id=str(log.id),
                actor_user_id=str(log.actor_user_id) if log.actor_user_id else None,
                actor_role=log.actor_role,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=str(log.entity_id) if log.entity_id else None,
                before_data=log.before_data,
                after_data=log.after_data,
                ip_address=log.ip_address,
                created_at=log.created_at,
            )
            for log in logs
        ]

    def list_fraud_flags(self) -> list[FraudFlagOut]:
        flags: list[FraudFlagOut] = []
        now = utcnow()
        last_day = now - timedelta(hours=24)

        device_rows = self.db.execute(
            select(
                OTPRequest.device_fingerprint,
                func.count(distinct(OTPRequest.phone_number)).label("phone_count"),
                func.max(OTPRequest.created_at).label("last_seen"),
            )
            .where(OTPRequest.created_at >= last_day, OTPRequest.device_fingerprint.is_not(None))
            .group_by(OTPRequest.device_fingerprint)
            .having(func.count(distinct(OTPRequest.phone_number)) >= 3)
        ).all()
        for device_fingerprint, phone_count, last_seen in device_rows:
            flags.append(
                FraudFlagOut(
                    flag_type="otp_device_phone_churn",
                    severity="high",
                    description=f"One device requested OTPs for {phone_count} phone numbers in the last 24 hours.",
                    related_value=device_fingerprint,
                    created_at=last_seen,
                )
            )

        ip_rows = self.db.execute(
            select(
                OTPRequest.request_ip,
                func.count(OTPRequest.id).label("request_count"),
                func.max(OTPRequest.created_at).label("last_seen"),
            )
            .where(OTPRequest.created_at >= last_day, OTPRequest.request_ip.is_not(None))
            .group_by(OTPRequest.request_ip)
            .having(func.count(OTPRequest.id) >= 10)
        ).all()
        for request_ip, request_count, last_seen in ip_rows:
            flags.append(
                FraudFlagOut(
                    flag_type="otp_ip_volume_spike",
                    severity="medium",
                    description=f"IP address generated {request_count} OTP requests in the last 24 hours.",
                    related_value=request_ip,
                    created_at=last_seen,
                )
            )

        adjustment_rows = self.db.execute(
            select(
                LoyaltyTransaction.created_by_user_id,
                LoyaltyTransaction.points_delta,
                LoyaltyTransaction.comment,
                LoyaltyTransaction.created_at,
            )
            .where(
                LoyaltyTransaction.transaction_type == "manual_adjustment",
                func.abs(LoyaltyTransaction.points_delta) >= 500,
            )
            .order_by(LoyaltyTransaction.created_at.desc())
            .limit(25)
        ).all()
        for actor_user_id, points_delta, comment, created_at in adjustment_rows:
            flags.append(
                FraudFlagOut(
                    flag_type="large_manual_adjustment",
                    severity="medium" if abs(points_delta) < 1000 else "high",
                    description=f"Manual adjustment of {points_delta:+d} points requires review. Comment: {comment or 'none'}",
                    related_value=str(actor_user_id) if actor_user_id else None,
                    created_at=created_at,
                )
            )

        flags.sort(key=lambda item: item.created_at, reverse=True)
        return flags[:50]

    def export_customers_csv(self) -> str:
        rows = self.user_repo.list_customer_bundles()
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "user_id",
                "phone_number",
                "full_name",
                "birthday",
                "member_id",
                "points_balance",
                "lifetime_points",
                "tier",
                "discount_percent",
                "marketing_sms_consent",
                "created_at",
                "last_activity_at",
            ]
        )
        for user, profile, account in rows:
            writer.writerow(
                [
                    str(user.id),
                    user.phone_number,
                    profile.full_name or "",
                    profile.birthday.isoformat() if profile.birthday else "",
                    account.member_id,
                    account.points_balance,
                    account.lifetime_points,
                    account.tier,
                    float(account.discount_percent),
                    "true" if profile.marketing_sms_consent else "false",
                    profile.created_at.isoformat(),
                    account.last_activity_at.isoformat() if account.last_activity_at else "",
                ]
            )
        return output.getvalue()
