from __future__ import annotations

import json
from base64 import b64encode
from dataclasses import dataclass
from urllib.parse import quote_plus
from urllib import error, request

from app.core.config import settings


class SMSDeliveryError(Exception):
    pass


@dataclass
class SMSMessage:
    phone_number: str
    text: str


@dataclass
class SMSDeliveryResult:
    provider: str
    status: str
    external_id: str | None = None


class BaseSMSProvider:
    def send(self, message: SMSMessage) -> SMSDeliveryResult:
        raise NotImplementedError


class MockSMSProvider(BaseSMSProvider):
    def send(self, message: SMSMessage) -> SMSDeliveryResult:
        print(f"[mock-sms] to={message.phone_number} text={message.text}")
        return SMSDeliveryResult(provider="mock", status="sent", external_id="mock-message")


class GenericHTTPSMSProvider(BaseSMSProvider):
    def send(self, message: SMSMessage) -> SMSDeliveryResult:
        if not settings.sms_api_url:
            raise SMSDeliveryError("SMS_API_URL is not configured")

        payload = json.dumps(
            {
                "to": message.phone_number,
                "message": message.text,
                "sender": settings.sms_sender_name,
            }
        ).encode("utf-8")
        req = request.Request(
            settings.sms_api_url,
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.sms_api_key or ''}",
            },
        )

        try:
            with request.urlopen(req, timeout=settings.sms_timeout_seconds) as response:
                if response.status >= 400:
                    raise SMSDeliveryError(f"SMS provider returned {response.status}")
                response_body = response.read().decode("utf-8") if hasattr(response, "read") else ""
                return SMSDeliveryResult(provider="generic_http", status="sent", external_id=response_body or None)
        except error.URLError as exc:
            raise SMSDeliveryError(f"SMS delivery failed: {exc.reason}") from exc


class TwilioSMSProvider(BaseSMSProvider):
    def send(self, message: SMSMessage) -> SMSDeliveryResult:
        if not settings.twilio_account_sid or not settings.twilio_auth_token or not settings.twilio_from_number:
            raise SMSDeliveryError("Twilio credentials are not fully configured")

        api_url = (
            f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
        )
        body = (
            f"To={quote_plus(message.phone_number)}"
            f"&From={quote_plus(settings.twilio_from_number)}"
            f"&Body={quote_plus(message.text)}"
        ).encode("utf-8")
        basic_auth = b64encode(
            f"{settings.twilio_account_sid}:{settings.twilio_auth_token}".encode("utf-8")
        ).decode("utf-8")
        req = request.Request(
            api_url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {basic_auth}",
            },
        )

        try:
            with request.urlopen(req, timeout=settings.sms_timeout_seconds) as response:
                response_text = response.read().decode("utf-8")
                if response.status >= 400:
                    raise SMSDeliveryError(f"Twilio returned {response.status}")
                external_id = None
                try:
                    external_id = json.loads(response_text).get("sid")
                except json.JSONDecodeError:
                    external_id = None
                return SMSDeliveryResult(provider="twilio", status="sent", external_id=external_id)
        except error.URLError as exc:
            raise SMSDeliveryError(f"Twilio delivery failed: {exc.reason}") from exc


class SMSRuProvider(BaseSMSProvider):
    def send(self, message: SMSMessage) -> SMSDeliveryResult:
        if not settings.sms_ru_api_id:
            raise SMSDeliveryError("SMS_RU_API_ID is not configured")

        body = (
            f"api_id={quote_plus(settings.sms_ru_api_id)}"
            f"&to={quote_plus(message.phone_number)}"
            f"&msg={quote_plus(message.text)}"
            f"&json=1"
        )
        if settings.sms_sender_name:
            body += f"&from={quote_plus(settings.sms_sender_name)}"

        req = request.Request(
            "https://sms.ru/sms/send",
            data=body.encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        try:
            with request.urlopen(req, timeout=settings.sms_timeout_seconds) as response:
                response_text = response.read().decode("utf-8")
                payload = json.loads(response_text)
                if response.status >= 400:
                    raise SMSDeliveryError(f"SMS.ru returned {response.status}")
                if payload.get("status") != "OK":
                    raise SMSDeliveryError(
                        f"SMS.ru delivery failed: {payload.get('status_text') or payload.get('status_code') or 'unknown error'}"
                    )

                message_payload = payload.get("sms", {}).get(message.phone_number)
                if not message_payload or message_payload.get("status") != "OK":
                    error_text = None
                    if message_payload:
                        error_text = message_payload.get("status_text") or message_payload.get("status_code")
                    raise SMSDeliveryError(f"SMS.ru delivery failed: {error_text or 'unknown error'}")

                return SMSDeliveryResult(
                    provider="sms_ru",
                    status="sent",
                    external_id=message_payload.get("sms_id"),
                )
        except error.URLError as exc:
            raise SMSDeliveryError(f"SMS.ru delivery failed: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise SMSDeliveryError("SMS.ru returned invalid JSON") from exc


class SMSService:
    def __init__(self) -> None:
        self.provider = self._build_provider()

    def send_otp(self, phone_number: str, otp_code: str) -> SMSDeliveryResult:
        message = SMSMessage(
            phone_number=phone_number,
            text=f"Your Golden Bite verification code is {otp_code}. It expires in {settings.otp_ttl_seconds // 60} minutes.",
        )
        return self.provider.send(message)

    def _build_provider(self) -> BaseSMSProvider:
        provider_name = settings.sms_provider.lower().strip()
        if provider_name in {"mock", "console"}:
            return MockSMSProvider()
        if provider_name in {"sms_ru", "smsru"}:
            return SMSRuProvider()
        if provider_name in {"generic_http", "http"}:
            return GenericHTTPSMSProvider()
        if provider_name in {"twilio"}:
            return TwilioSMSProvider()
        raise SMSDeliveryError(f"Unsupported SMS provider: {settings.sms_provider}")
