from datetime import datetime

from app.schemas.common import AppBaseModel


class WalletAddOut(AppBaseModel):
    download_url: str


class WalletStatusOut(AppBaseModel):
    status: str
    last_synced_at: datetime | None


class WalletRegistrationOut(AppBaseModel):
    serial_numbers: list[str]
    last_updated: str | None = None


class WalletLogIn(AppBaseModel):
    logs: list[str]
