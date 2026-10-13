from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.auth import OTPRequestIn
from app.services.auth_service import AuthService, OTPRequestContext
from app.services.sms_service import SMSDeliveryError


def test_enforce_rate_limits_blocks_phone_limit() -> None:
    service = AuthService(MagicMock())
    context = OTPRequestContext(request_ip="127.0.0.1", device_fingerprint="device-1")

    with patch("app.services.auth_service.rate_limiter.allow") as allow_mock:
        allow_mock.return_value.allowed = False
        allow_mock.return_value.count = 4

        with pytest.raises(HTTPException) as exc:
            service._enforce_rate_limits("+79991234567", context)

    assert exc.value.status_code == 429
    assert "phone number" in exc.value.detail


def test_request_otp_persists_request_context() -> None:
    db = MagicMock()
    service = AuthService(db)
    service.otp_repo.count_recent_by_phone = MagicMock(return_value=0)
    service.otp_repo.create = MagicMock()
    service.sms_service.send_otp = MagicMock(return_value=MagicMock(provider="mock", status="sent", external_id="msg-1"))
    service._write_system_audit_event = MagicMock()

    payload = OTPRequestIn(phone_number="+79991234567", purpose="login")

    with patch("app.services.auth_service.rate_limiter.allow") as allow_mock:
        allow_mock.return_value.allowed = True
        allow_mock.return_value.count = 1

        result = service.request_otp(
            payload,
            request_ip="127.0.0.1",
            device_fingerprint="device-xyz",
        )

    created_request = service.otp_repo.create.call_args.args[0]
    assert created_request.request_ip == "127.0.0.1"
    assert created_request.device_fingerprint == "device-xyz"
    assert result.expires_in_seconds == 300
    assert db.commit.called
    service._write_system_audit_event.assert_called_once()


def test_request_otp_logs_failure_after_rollback() -> None:
    db = MagicMock()
    service = AuthService(db)
    service.otp_repo.count_recent_by_phone = MagicMock(return_value=0)
    service.otp_repo.create = MagicMock()
    service.sms_service.send_otp = MagicMock(side_effect=SMSDeliveryError("gateway down"))
    service._write_system_audit_event = MagicMock()

    payload = OTPRequestIn(phone_number="+79991234567", purpose="login")

    with patch("app.services.auth_service.rate_limiter.allow") as allow_mock:
        allow_mock.return_value.allowed = True
        allow_mock.return_value.count = 1

        with pytest.raises(HTTPException) as exc:
            service.request_otp(payload, request_ip="127.0.0.1", device_fingerprint="device-xyz")

    assert exc.value.status_code == 503
    assert db.rollback.called
    service._write_system_audit_event.assert_called_once()
    _, kwargs = service._write_system_audit_event.call_args
    assert kwargs["action"] == "auth.send_otp_failed"
    assert kwargs["entity_id"] is None
