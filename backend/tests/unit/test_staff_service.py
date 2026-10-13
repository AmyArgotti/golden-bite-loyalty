from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.services.staff_service import StaffService


def test_search_customers_maps_repo_records() -> None:
    db = MagicMock()
    service = StaffService(db)
    actor = SimpleNamespace(id=uuid4(), role="staff")
    user = SimpleNamespace(id=uuid4(), phone_number="+79991234567")
    profile = SimpleNamespace(id=uuid4())
    account = SimpleNamespace(member_id="GB-100001", points_balance=1280, tier="silver")
    service.user_repo.search_customers = MagicMock(return_value=[(user, profile, account)])

    result = service.search_customers(actor, phone_number="+79991234567")

    assert len(result) == 1
    assert result[0].member_id == "GB-100001"
    assert result[0].phone_number == "+79991234567"
    assert result[0].points_balance == 1280


def test_get_customer_detail_raises_when_missing() -> None:
    db = MagicMock()
    service = StaffService(db)
    actor = SimpleNamespace(id=uuid4(), role="staff")
    service.user_repo.get_customer_bundle = MagicMock(return_value=None)

    with pytest.raises(ValueError, match="Customer not found"):
        service.get_customer_detail(actor, uuid4())


def test_get_customer_by_scan_builds_recent_activity() -> None:
    db = MagicMock()
    service = StaffService(db)
    actor = SimpleNamespace(id=uuid4(), role="staff")
    customer_id = uuid4()
    profile_id = uuid4()
    account_id = uuid4()
    account = SimpleNamespace(
        id=account_id,
        customer_profile_id=profile_id,
        member_id="GB-100001",
        points_balance=1415,
        lifetime_points=1540,
        tier="silver",
        discount_percent=Decimal("5.00"),
        qr_code_value="GB-100001",
        barcode_value="100001",
    )
    user = SimpleNamespace(id=customer_id, phone_number="+79991234567")
    profile = SimpleNamespace(id=profile_id)
    transaction = SimpleNamespace(
        transaction_type="earn",
        points_delta=135,
        rub_amount=Decimal("1350.00"),
        source="staff",
        comment="Order ORDER-1055",
        created_at=datetime(2026, 3, 25, 12, 0, 0),
    )

    service.loyalty_repo.get_account_by_scan_value = MagicMock(return_value=account)
    service.user_repo.get_customer_bundle_by_profile_id = MagicMock(return_value=(user, profile, account))
    service.loyalty_repo.list_recent_transactions = MagicMock(return_value=[transaction])

    result = service.get_customer_by_scan(actor, "GB-100001")

    assert result.customer_id == str(customer_id)
    assert result.member_id == "GB-100001"
    assert result.discount_percent == 5.0
    assert len(result.recent_transactions) == 1
    assert result.recent_transactions[0].points_delta == 135
