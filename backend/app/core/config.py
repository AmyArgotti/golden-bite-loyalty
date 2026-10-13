from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002"]
    app_name: str = "Golden Bite Loyalty API"
    app_env: str = "development"
    secret_key: str = "change-me"
    database_url: str = "postgresql+psycopg://golden_bite:golden_bite@localhost:5432/golden_bite"
    redis_url: str = "redis://localhost:6379/0"
    access_token_ttl_min: int = 15
    refresh_token_ttl_days: int = 30
    otp_ttl_seconds: int = 300
    otp_max_attempts: int = 5
    rate_limit_otp_per_phone: int = 3
    rate_limit_otp_per_ip: int = 10
    rate_limit_otp_per_device: int = 10
    rate_limit_otp_phone_window_minutes: int = 15
    rate_limit_otp_ip_window_minutes: int = 60
    sms_provider: str = "mock"
    sms_api_url: str | None = None
    sms_api_key: str | None = None
    sms_sender_name: str = "Golden Bite"
    sms_timeout_seconds: int = 10
    sms_ru_api_id: str | None = None
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_from_number: str | None = None
    wallet_passes_dir: str = "/tmp/golden-bite-wallet-passes"
    wallet_pass_type_identifier: str | None = None
    wallet_team_identifier: str | None = None
    wallet_organization_name: str = "Golden Bite"
    wallet_web_service_url: str | None = None
    wallet_signing_cert_path: str | None = None
    wallet_signing_key_path: str | None = None
    wallet_wwdr_cert_path: str | None = None
    loyalty_rules_path: str = "/tmp/golden-bite-loyalty-rules.json"
    sentry_dsn: str | None = None
    sentry_environment: str | None = None
    sentry_traces_sample_rate: float = 0.0
    seed_admin_phone_number: str = "+79990000001"
    seed_staff_phone_number: str = "+79990000002"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
