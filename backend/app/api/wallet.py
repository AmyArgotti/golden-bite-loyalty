from fastapi import APIRouter, Depends, Header, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.wallet import WalletAddOut, WalletLogIn, WalletRegistrationOut, WalletStatusOut
from app.services.wallet_service import WalletService


router = APIRouter()


@router.post("/apple/add", response_model=WalletAddOut)
def add_apple_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WalletAddOut:
    return WalletService(db).create_apple_pass(current_user)


@router.get("/status", response_model=WalletStatusOut)
def wallet_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WalletStatusOut:
    return WalletService(db).get_status(current_user)


@router.post("/refresh", response_model=WalletStatusOut)
def refresh_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WalletStatusOut:
    return WalletService(db).refresh_pass(current_user)


@router.get("/passes/{pass_id}")
def download_pass(pass_id: str, db: Session = Depends(get_db)) -> FileResponse:
    pkpass_path = WalletService(db).get_pass_path(pass_id)
    return FileResponse(pkpass_path, media_type="application/vnd.apple.pkpass", filename=pkpass_path.name)


def _extract_wallet_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("ApplePass "):
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing ApplePass token")
    return authorization.removeprefix("ApplePass ").strip()


@router.post("/apple/devices/{device_library_identifier}/registrations/{pass_type_identifier}/{serial_number}", status_code=201)
def register_wallet_device(
    device_library_identifier: str,
    pass_type_identifier: str,
    serial_number: str,
    payload: dict,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    WalletService(db).register_device(
        device_library_identifier=device_library_identifier,
        pass_type_identifier=pass_type_identifier,
        serial_number=serial_number,
        push_token=payload.get("pushToken", ""),
        auth_token=_extract_wallet_token(authorization),
    )
    return {"status": "registered"}


@router.delete("/apple/devices/{device_library_identifier}/registrations/{pass_type_identifier}/{serial_number}", status_code=200)
def unregister_wallet_device(
    device_library_identifier: str,
    pass_type_identifier: str,
    serial_number: str,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    WalletService(db).unregister_device(
        device_library_identifier=device_library_identifier,
        pass_type_identifier=pass_type_identifier,
        serial_number=serial_number,
        auth_token=_extract_wallet_token(authorization),
    )
    return {"status": "unregistered"}


@router.get("/apple/devices/{device_library_identifier}/registrations/{pass_type_identifier}", response_model=WalletRegistrationOut)
def list_updated_wallet_passes(
    device_library_identifier: str,
    pass_type_identifier: str,
    passes_updated_since: str | None = Query(default=None, alias="passesUpdatedSince"),
    db: Session = Depends(get_db),
) -> WalletRegistrationOut:
    return WalletService(db).get_updated_serials(
        device_library_identifier=device_library_identifier,
        pass_type_identifier=pass_type_identifier,
        passes_updated_since=passes_updated_since,
    )


@router.get("/apple/passes/{pass_type_identifier}/{serial_number}")
def download_registered_wallet_pass(
    pass_type_identifier: str,
    serial_number: str,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> FileResponse:
    pkpass_path = WalletService(db).get_registered_pass_path(
        pass_type_identifier=pass_type_identifier,
        serial_number=serial_number,
        auth_token=_extract_wallet_token(authorization),
    )
    return FileResponse(pkpass_path, media_type="application/vnd.apple.pkpass", filename=pkpass_path.name)


@router.post("/apple/log", status_code=200)
def wallet_log(payload: WalletLogIn) -> dict[str, int]:
    return {"accepted_logs": len(payload.logs)}
