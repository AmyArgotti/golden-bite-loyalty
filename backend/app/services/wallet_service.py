from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import HTTPException, status

from app.core.config import settings
from app.models.loyalty_account import LoyaltyAccount
from app.models.user import User
from app.repositories.loyalty_repo import LoyaltyRepository
from app.repositories.user_repo import UserRepository
from app.schemas.wallet import WalletAddOut, WalletRegistrationOut, WalletStatusOut


class WalletService:
    def __init__(self, db) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.loyalty_repo = LoyaltyRepository(db)
        self.base_dir = Path(settings.wallet_passes_dir)

    def create_apple_pass(self, current_user: User) -> WalletAddOut:
        account = self._get_account(current_user)
        serial_number = self._build_serial_number(account)
        self._generate_and_store_pass(account, serial_number=serial_number, allow_create=True)
        self.db.commit()
        self.db.refresh(account)
        return WalletAddOut(download_url=f"/api/v1/wallet/passes/{serial_number}")

    def get_status(self, current_user: User) -> WalletStatusOut:
        account = self._get_account(current_user)
        return WalletStatusOut(status=account.wallet_status, last_synced_at=account.updated_at)

    def refresh_pass(self, current_user: User) -> WalletStatusOut:
        account = self._get_account(current_user)
        serial_number = self._build_serial_number(account)
        self._generate_and_store_pass(account, serial_number=serial_number, allow_create=True)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return WalletStatusOut(status=account.wallet_status, last_synced_at=account.updated_at)

    def sync_account_pass(self, account: LoyaltyAccount) -> None:
        serial_number = self._build_serial_number(account)
        metadata = self._load_registry()
        if serial_number not in metadata:
            return
        try:
            self._generate_and_store_pass(account, serial_number=serial_number, allow_create=False)
        except Exception:
            account.wallet_status = "sync_failed"
            self.db.add(account)

    def get_pass_path(self, pass_id: str) -> Path:
        pkpass_path = self._pkpass_path(pass_id)
        if not pkpass_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pass not found")
        return pkpass_path

    def register_device(
        self,
        device_library_identifier: str,
        pass_type_identifier: str,
        serial_number: str,
        push_token: str,
        auth_token: str,
    ) -> None:
        metadata = self._load_registry()
        entry = self._get_registry_entry(metadata, serial_number, pass_type_identifier, auth_token)
        devices = entry["registered_devices"]
        if not any(device["device_library_identifier"] == device_library_identifier for device in devices):
            devices.append(
                {
                    "device_library_identifier": device_library_identifier,
                    "push_token": push_token,
                    "registered_at": self._timestamp(),
                }
            )
        entry["updated_at"] = self._timestamp()
        self._save_registry(metadata)

    def unregister_device(
        self,
        device_library_identifier: str,
        pass_type_identifier: str,
        serial_number: str,
        auth_token: str,
    ) -> None:
        metadata = self._load_registry()
        entry = self._get_registry_entry(metadata, serial_number, pass_type_identifier, auth_token)
        entry["registered_devices"] = [
            device
            for device in entry["registered_devices"]
            if device["device_library_identifier"] != device_library_identifier
        ]
        entry["updated_at"] = self._timestamp()
        self._save_registry(metadata)

    def get_updated_serials(
        self,
        device_library_identifier: str,
        pass_type_identifier: str,
        passes_updated_since: str | None = None,
    ) -> WalletRegistrationOut:
        metadata = self._load_registry()
        serials: list[str] = []
        latest: str | None = None
        for serial_number, entry in metadata.items():
            if entry["pass_type_identifier"] != pass_type_identifier:
                continue
            if not any(device["device_library_identifier"] == device_library_identifier for device in entry["registered_devices"]):
                continue
            if passes_updated_since and entry["updated_at"] <= passes_updated_since:
                continue
            serials.append(serial_number)
            latest = max(latest, entry["updated_at"]) if latest else entry["updated_at"]
        return WalletRegistrationOut(serial_numbers=serials, last_updated=latest)

    def get_registered_pass_path(self, pass_type_identifier: str, serial_number: str, auth_token: str) -> Path:
        metadata = self._load_registry()
        self._get_registry_entry(metadata, serial_number, pass_type_identifier, auth_token)
        return self.get_pass_path(serial_number)

    def _get_account(self, current_user: User) -> LoyaltyAccount:
        profile = self.user_repo.get_profile_by_user_id(current_user.id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
        account = self.loyalty_repo.get_account_by_profile_id(profile.id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loyalty account not found")
        return account

    def _generate_and_store_pass(self, account: LoyaltyAccount, serial_number: str, allow_create: bool) -> None:
        self._ensure_base_dir()
        metadata = self._load_registry()
        existing = metadata.get(serial_number)
        if not allow_create and not existing:
            return

        auth_token = existing["auth_token"] if existing else hashlib.sha256(serial_number.encode("utf-8")).hexdigest()[:32]
        pass_type_identifier = settings.wallet_pass_type_identifier or "pass.com.goldenbite.loyalty.dev"
        pass_dir = self.base_dir / serial_number
        pass_dir.mkdir(parents=True, exist_ok=True)

        pass_payload = self._build_pass_payload(account, serial_number=serial_number, auth_token=auth_token)
        (pass_dir / "pass.json").write_text(json.dumps(pass_payload, indent=2), encoding="utf-8")
        (pass_dir / "README.txt").write_text(
            "Golden Bite wallet pass package. Replace bundled placeholder assets and provide Apple signing certificates before production launch.",
            encoding="utf-8",
        )
        self._write_assets(pass_dir)
        self._write_manifest(pass_dir)

        status_value = "generated_unsigned"
        if self._is_signing_configured():
            self._write_signature(pass_dir)
            status_value = "active"

        pkpass_path = self._pkpass_path(serial_number)
        with ZipFile(pkpass_path, "w", compression=ZIP_DEFLATED) as zf:
            for asset_name in ["pass.json", "manifest.json", "README.txt", "icon.png", "icon@2x.png", "logo.png", "logo@2x.png"]:
                asset_path = pass_dir / asset_name
                if asset_path.exists():
                    zf.write(asset_path, arcname=asset_name)
            if (pass_dir / "signature").exists():
                zf.write(pass_dir / "signature", arcname="signature")

        metadata[serial_number] = {
            "serial_number": serial_number,
            "account_member_id": account.member_id,
            "auth_token": auth_token,
            "pass_type_identifier": pass_type_identifier,
            "updated_at": self._timestamp(),
            "registered_devices": existing["registered_devices"] if existing else [],
        }
        self._save_registry(metadata)

        account.wallet_status = status_value
        self.db.add(account)

    def _build_pass_payload(self, account: LoyaltyAccount, serial_number: str, auth_token: str) -> dict:
        description = f"{settings.wallet_organization_name} loyalty card"
        barcode_message = account.barcode_value
        return {
            "description": description,
            "formatVersion": 1,
            "organizationName": settings.wallet_organization_name,
            "passTypeIdentifier": settings.wallet_pass_type_identifier or "pass.com.goldenbite.loyalty.dev",
            "serialNumber": serial_number,
            "teamIdentifier": settings.wallet_team_identifier or "DEVTEAM",
            "foregroundColor": "rgb(255,255,255)",
            "backgroundColor": "rgb(179,90,43)",
            "labelColor": "rgb(255,245,240)",
            "barcode": {
                "format": "PKBarcodeFormatCode128",
                "message": barcode_message,
                "messageEncoding": "iso-8859-1",
                "altText": account.member_id,
            },
            "generic": {
                "primaryFields": [
                    {"key": "points", "label": "Points", "value": str(account.points_balance)},
                ],
                "secondaryFields": [
                    {"key": "tier", "label": "Tier", "value": account.tier.title()},
                    {"key": "discount", "label": "Discount", "value": f"{float(account.discount_percent):.0f}%"},
                ],
                "auxiliaryFields": [
                    {"key": "member", "label": "Member ID", "value": account.member_id},
                ],
                "backFields": [
                    {"key": "lifetime", "label": "Lifetime Points", "value": str(account.lifetime_points)},
                    {"key": "barcode", "label": "Barcode", "value": account.barcode_value},
                    {
                        "key": "generated",
                        "label": "Generated At",
                        "value": self._timestamp(),
                    },
                ],
            },
            "webServiceURL": settings.wallet_web_service_url or "",
            "authenticationToken": auth_token,
        }

    def _write_manifest(self, pass_dir: Path) -> None:
        manifest = {}
        for child in pass_dir.iterdir():
            if child.name == "signature" or not child.is_file():
                continue
            manifest[child.name] = hashlib.sha1(child.read_bytes()).hexdigest()
        (pass_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def _is_signing_configured(self) -> bool:
        return bool(
            settings.wallet_signing_cert_path
            and settings.wallet_signing_key_path
            and settings.wallet_wwdr_cert_path
        )

    def _write_signature(self, pass_dir: Path) -> None:
        signature_path = pass_dir / "signature"
        command = [
            "openssl",
            "smime",
            "-binary",
            "-sign",
            "-signer",
            str(settings.wallet_signing_cert_path),
            "-inkey",
            str(settings.wallet_signing_key_path),
            "-certfile",
            str(settings.wallet_wwdr_cert_path),
            "-in",
            str(pass_dir / "manifest.json"),
            "-out",
            str(signature_path),
            "-outform",
            "DER",
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Wallet pass signing failed: {completed.stderr.strip() or 'openssl error'}",
            )

    def _write_assets(self, pass_dir: Path) -> None:
        png_bytes = bytes.fromhex(
            "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C489"
            "0000000D49444154789C6360F8CF0002000100B5D67F990000000049454E44AE426082"
        )
        for asset_name in ["icon.png", "icon@2x.png", "logo.png", "logo@2x.png"]:
            (pass_dir / asset_name).write_bytes(png_bytes)

    def _registry_path(self) -> Path:
        return self.base_dir / "registrations.json"

    def _ensure_base_dir(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _load_registry(self) -> dict:
        path = self._registry_path()
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _save_registry(self, metadata: dict) -> None:
        self._ensure_base_dir()
        self._registry_path().write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    def _get_registry_entry(self, metadata: dict, serial_number: str, pass_type_identifier: str, auth_token: str) -> dict:
        entry = metadata.get(serial_number)
        if not entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pass registration not found")
        if entry["pass_type_identifier"] != pass_type_identifier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pass type mismatch")
        if entry["auth_token"] != auth_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid wallet auth token")
        return entry

    def _build_serial_number(self, account: LoyaltyAccount) -> str:
        return account.member_id

    def _pkpass_path(self, serial_number: str) -> Path:
        return self.base_dir / f"{serial_number}.pkpass"

    def _timestamp(self) -> str:
        return datetime.now(UTC).isoformat()
