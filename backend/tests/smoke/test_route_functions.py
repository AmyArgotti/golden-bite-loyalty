import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.api import admin as admin_api
from app.api import auth as auth_api
from app.api import health as health_api
from app.api import staff as staff_api
from app.schemas.admin import AdminDashboardOut, AdminStaffOut, AuditLogOut, FraudFlagOut, LoyaltyRulesOut, TierRuleOut
from app.schemas.auth import AuthUserOut, OTPRequestIn, OTPRequestOut, OTPVerifyIn, OTPVerifyOut
from app.schemas.staff import CustomerSearchOut, PurchaseCreateIn, PurchaseCreateOut, StaffCustomerDetailOut


class RouteFunctionSmokeTests(unittest.TestCase):
    def test_healthcheck_returns_ok(self) -> None:
        self.assertEqual(health_api.healthcheck(), {"status": "ok"})

    def test_request_otp_route_passes_context(self) -> None:
        payload = OTPRequestIn(phone_number="+79991234567", purpose="login")
        request = SimpleNamespace(client=SimpleNamespace(host="127.0.0.1"))
        db = MagicMock()

        with patch("app.api.auth.AuthService.request_otp", return_value=OTPRequestOut(message="OTP sent", expires_in_seconds=300)) as request_mock:
            response = auth_api.request_otp(payload, request, "device-123", db)

        self.assertEqual(response.expires_in_seconds, 300)
        request_mock.assert_called_once()
        _, kwargs = request_mock.call_args
        self.assertEqual(kwargs["request_ip"], "127.0.0.1")
        self.assertEqual(kwargs["device_fingerprint"], "device-123")

    def test_verify_otp_route_returns_tokens(self) -> None:
        payload = OTPVerifyIn(phone_number="+79991234567", otp_code="123456")
        db = MagicMock()
        expected = OTPVerifyOut(
            access_token="a",
            refresh_token="r",
            user=AuthUserOut(id="user-1", role="customer"),
            is_new_user=True,
        )
        with patch("app.api.auth.AuthService.verify_otp", return_value=expected):
            response = auth_api.verify_otp(payload, db)
        self.assertEqual(response.user.role, "customer")

    def test_staff_search_route_returns_customer_rows(self) -> None:
        db = MagicMock()
        current_user = SimpleNamespace(id=uuid4(), role="staff")
        expected = [
            CustomerSearchOut(
                customer_id="customer-1",
                member_id="GB-100001",
                phone_number="+79991234567",
                points_balance=1280,
                tier="silver",
            )
        ]
        with patch("app.api.staff.StaffService.search_customers", return_value=expected):
            response = staff_api.search_customers("+79991234567", None, db, current_user)
        self.assertEqual(response[0].member_id, "GB-100001")

    def test_staff_purchase_route_returns_summary(self) -> None:
        db = MagicMock()
        current_user = SimpleNamespace(id=uuid4(), role="staff")
        payload = PurchaseCreateIn(
            customer_id=uuid4(),
            purchase_amount=1350,
            order_reference="ORDER-1055",
        )
        expected = PurchaseCreateOut(
            earned_points=135,
            bonus_points=100,
            total_points_added=235,
            new_points_balance=1415,
            new_tier="silver",
            discount_percent=5.0,
        )
        with patch("app.api.staff.PurchaseService.register_purchase", return_value=expected):
            response = staff_api.register_purchase(payload, db, current_user)
        self.assertEqual(response.total_points_added, 235)

    def test_admin_routes_return_dashboard_staff_audit_and_fraud(self) -> None:
        db = MagicMock()
        current_user = SimpleNamespace(id=uuid4(), role="admin")
        with patch(
            "app.api.admin.AdminService.get_dashboard",
            return_value=AdminDashboardOut(
                active_customers=12,
                total_points_issued=4500,
                transactions_today=9,
                pending_fraud_flags=0,
            ),
        ), patch(
            "app.api.admin.AdminService.get_loyalty_rules",
            return_value=LoyaltyRulesOut(
                points_per_rub_ratio=0.1,
                tiers=[TierRuleOut(name="silver", min_points=1000, discount_percent=5)],
                first_order_bonus=100,
                birthday_bonus=200,
                referral_referrer_bonus=150,
                referral_referee_bonus=100,
            ),
        ), patch(
            "app.api.admin.AdminService.list_staff",
            return_value=[
                AdminStaffOut(
                    id="admin-1",
                    phone_number="+79990000001",
                    role="admin",
                    is_active=True,
                    phone_verified_at=None,
                )
            ],
        ), patch(
            "app.api.admin.AdminService.list_audit_logs",
            return_value=[
                AuditLogOut(
                    id="log-1",
                    actor_user_id="admin-1",
                    actor_role="admin",
                    action="staff.adjust",
                    entity_type="loyalty_account",
                    entity_id="entity-1",
                    before_data={"points_balance": 10},
                    after_data={"points_balance": 60},
                    ip_address=None,
                    created_at=__import__("datetime").datetime(2026, 3, 25, 12, 0, 0),
                )
            ],
        ), patch(
            "app.api.admin.AdminService.list_fraud_flags",
            return_value=[
                FraudFlagOut(
                    flag_type="otp_device_phone_churn",
                    severity="high",
                    description="One device requested OTPs for 4 phone numbers in the last 24 hours.",
                    related_value="device-1",
                    created_at=__import__("datetime").datetime(2026, 3, 25, 12, 5, 0),
                )
            ],
        ):
            dashboard = admin_api.get_dashboard(db, current_user)
            rules = admin_api.get_loyalty_rules(db, current_user)
            staff = admin_api.list_staff(db, current_user)
            audit_logs = admin_api.list_audit_logs(db, current_user)
            fraud_flags = admin_api.list_fraud_flags(db, current_user)

        self.assertEqual(dashboard.active_customers, 12)
        self.assertEqual(rules.first_order_bonus, 100)
        self.assertEqual(staff[0].role, "admin")
        self.assertEqual(audit_logs[0].action, "staff.adjust")
        self.assertEqual(fraud_flags[0].severity, "high")


if __name__ == "__main__":
    unittest.main()
