from datetime import datetime

from app.schemas.admin import AdminDashboardOut, AdminStaffOut, AuditLogOut, LoyaltyRulesOut, TierRuleOut
from app.schemas.auth import OTPRequestOut, OTPVerifyOut, AuthUserOut
from app.schemas.staff import CustomerSearchOut, PurchaseCreateOut, StaffCustomerDetailOut
from app.api.deps import get_current_user
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.services.purchase_service import PurchaseService
from app.services.staff_service import StaffService


def override_current_user(app, user) -> None:
    app.dependency_overrides[get_current_user] = lambda: user


def test_health_route_returns_ok(client) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_request_otp_route_uses_request_context(client, monkeypatch) -> None:
    called = {}

    def fake_request_otp(self, payload, request_ip=None, device_fingerprint=None):
        called["phone"] = payload.phone_number
        called["ip"] = request_ip
        called["device"] = device_fingerprint
        return OTPRequestOut(message="OTP sent", expires_in_seconds=300)

    monkeypatch.setattr(AuthService, "request_otp", fake_request_otp)

    response = client.post(
        "/api/v1/auth/request-otp",
        json={"phone_number": "+79991234567", "purpose": "login"},
        headers={"X-Device-Fingerprint": "device-123"},
    )

    assert response.status_code == 200
    assert response.json()["expires_in_seconds"] == 300
    assert called == {"phone": "+79991234567", "ip": "testclient", "device": "device-123"}


def test_verify_otp_route_returns_tokens(client, monkeypatch) -> None:
    def fake_verify(self, payload):
        return OTPVerifyOut(
            access_token="token-a",
            refresh_token="token-r",
            user=AuthUserOut(id="user-1", role="customer"),
            is_new_user=True,
        )

    monkeypatch.setattr(AuthService, "verify_otp", fake_verify)

    response = client.post(
        "/api/v1/auth/verify-otp",
        json={"phone_number": "+79991234567", "otp_code": "123456"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "customer"
    assert response.json()["is_new_user"] is True


def test_staff_search_route_returns_customers(client, app, staff_user, monkeypatch) -> None:
    override_current_user(app, staff_user)

    monkeypatch.setattr(
        StaffService,
        "search_customers",
        lambda self, actor, phone_number=None, member_id=None: [
            CustomerSearchOut(
                customer_id="customer-1",
                member_id="GB-100001",
                phone_number="+79991234567",
                points_balance=1280,
                tier="silver",
            )
        ],
    )

    response = client.get("/api/v1/staff/customers/search?phone_number=+79991234567")

    assert response.status_code == 200
    assert response.json()[0]["member_id"] == "GB-100001"


def test_staff_purchase_route_returns_purchase_summary(client, app, staff_user, monkeypatch) -> None:
    override_current_user(app, staff_user)

    monkeypatch.setattr(
        PurchaseService,
        "register_purchase",
        lambda self, actor, payload: PurchaseCreateOut(
            earned_points=135,
            bonus_points=100,
            total_points_added=235,
            new_points_balance=1415,
            new_tier="silver",
            discount_percent=5.0,
        ),
    )

    response = client.post(
        "/api/v1/staff/purchases",
        json={
            "customer_id": "00000000-0000-0000-0000-000000000101",
            "purchase_amount": 1350,
            "order_reference": "ORDER-1055",
        },
    )

    assert response.status_code == 200
    assert response.json()["total_points_added"] == 235


def test_staff_scan_route_returns_customer_detail(client, app, staff_user, monkeypatch) -> None:
    override_current_user(app, staff_user)

    monkeypatch.setattr(
        StaffService,
        "get_customer_by_scan",
        lambda self, actor, scan_value: StaffCustomerDetailOut(
            customer_id="customer-1",
            member_id="GB-100001",
            phone_number="+79991234567",
            points_balance=1280,
            lifetime_points=1540,
            tier="silver",
            discount_percent=5.0,
            qr_code_value=scan_value,
            barcode_value="100001",
            recent_transactions=[],
        ),
    )

    response = client.post("/api/v1/staff/customers/scan", json={"scan_value": "GB-100001"})

    assert response.status_code == 200
    assert response.json()["qr_code_value"] == "GB-100001"


def test_admin_routes_return_dashboard_staff_and_audit(client, app, admin_user, monkeypatch) -> None:
    override_current_user(app, admin_user)

    monkeypatch.setattr(
        AdminService,
        "get_dashboard",
        lambda self: AdminDashboardOut(
            active_customers=12,
            total_points_issued=4500,
            transactions_today=9,
            pending_fraud_flags=0,
        ),
    )
    monkeypatch.setattr(
        AdminService,
        "get_loyalty_rules",
        lambda self: LoyaltyRulesOut(
            points_per_rub_ratio=0.1,
            tiers=[TierRuleOut(name="silver", min_points=1000, discount_percent=5)],
            first_order_bonus=100,
            birthday_bonus=200,
            referral_referrer_bonus=150,
            referral_referee_bonus=100,
        ),
    )
    monkeypatch.setattr(
        AdminService,
        "list_staff",
        lambda self: [
            AdminStaffOut(
                id="admin-1",
                phone_number="+79990000001",
                role="admin",
                is_active=True,
                phone_verified_at=None,
            )
        ],
    )
    monkeypatch.setattr(
        AdminService,
        "list_audit_logs",
        lambda self: [
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
                created_at=datetime(2026, 3, 25, 12, 0, 0),
            )
        ],
    )

    dashboard_response = client.get("/api/v1/admin/dashboard")
    rules_response = client.get("/api/v1/admin/config/loyalty-rules")
    staff_response = client.get("/api/v1/admin/staff")
    audit_response = client.get("/api/v1/admin/audit-logs")

    assert dashboard_response.status_code == 200
    assert rules_response.status_code == 200
    assert staff_response.status_code == 200
    assert audit_response.status_code == 200
    assert staff_response.json()[0]["role"] == "admin"
    assert audit_response.json()[0]["action"] == "staff.adjust"
