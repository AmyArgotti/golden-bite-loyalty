# Production Launch Checklist

Assumptions in this checklist:

- SMS provider: SMS.ru
- production domain: `https://loyalty.goldenbite.com`
- staff and admin are served at path-based routes:
  - `https://loyalty.goldenbite.com/staff`
  - `https://loyalty.goldenbite.com/admin`

## 1. Prepare Secrets

- copy [.env.production.example](/path/to/golden-bite-loyalty/.env.production.example) to `.env.production`
- generate a strong `SECRET_KEY`
  - you can use [generate_secrets.sh](/path/to/golden-bite-loyalty/infrastructure/scripts/generate_secrets.sh)
- set `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`
- make sure `DATABASE_URL` matches those same Postgres values exactly
- add real SMS provider values:
  - for `sms_ru`: `SMS_RU_API_ID`
  - for `twilio`: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`
- install Apple Wallet cert, key, and WWDR cert on the server
- validate the env file with [validate_env.sh](/path/to/golden-bite-loyalty/infrastructure/scripts/validate_env.sh)

## 2. Prepare Server

- provision Ubuntu LTS VPS with Docker and Docker Compose
- point DNS for `loyalty.goldenbite.com` to the server
- configure TLS for Nginx before live wallet tests
- ensure ports `80` and `443` are reachable
- use [loyalty.goldenbite.com.conf.example](/path/to/golden-bite-loyalty/infrastructure/nginx/loyalty.goldenbite.com.conf.example) as the HTTPS Nginx template

## 3. Prepare Runtime Storage

The production compose stack now mounts persistent app storage at `/var/lib/golden-bite` for:

- generated wallet packages
- loyalty rules configuration

PostgreSQL data is stored in the `postgres_data` Docker volume.

## 4. Deploy

```bash
cd /path/to/golden-bite-loyalty
cp .env.production.example .env
# edit .env with real values
infrastructure/scripts/deploy.sh
```

## 5. Verify Public Routes

- `https://loyalty.goldenbite.com/`
- `https://loyalty.goldenbite.com/staff`
- `https://loyalty.goldenbite.com/admin`
- `https://loyalty.goldenbite.com/api/v1/health`
- run [smoke_check.sh](/path/to/golden-bite-loyalty/infrastructure/scripts/smoke_check.sh)

## 6. Verify SMS End To End

1. request OTP from the customer app using a real phone
2. confirm the SMS arrives from the configured provider
3. verify OTP successfully
4. confirm the audit log contains `auth.send_otp`

If it fails:

1. confirm the audit log contains `auth.send_otp_failed`
2. verify provider credentials, sender name, and regional delivery restrictions

## 7. Verify Wallet End To End

1. sign in as a customer
2. generate the Apple Wallet pass
3. confirm the `.pkpass` installs successfully
4. register a purchase from the staff panel
5. confirm the pass package is regenerated with updated points and tier
6. verify wallet web-service registration and pass fetch routes work over HTTPS

## 8. Verify Operations

- create and update a staff user from the admin panel
- change loyalty rules
- review audit logs
- review fraud flags
- run a backup

## 9. Post-Launch Tasks

- configure uptime monitoring alerts
- schedule nightly `backup.sh` with [install_backup_cron.sh](/path/to/golden-bite-loyalty/infrastructure/scripts/install_backup_cron.sh)
- perform one restore drill against a disposable database
- rotate credentials out of any temporary shared notes

## Remaining Post-MVP Gaps

- APNs push notifications for Wallet updates
- Google Wallet support
- campaigns and referral automation
