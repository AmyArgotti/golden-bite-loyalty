# Launch Readiness Checklist

Use this as the final go/no-go list before the first real restaurant launch.

## Configuration

- [ ] production `.env` is filled with real values
- [ ] `DATABASE_URL` matches `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`
- [ ] Twilio credentials are real and validated
- [ ] Apple Wallet cert, key, and WWDR files are present on the server
- [ ] `WALLET_WEB_SERVICE_URL` points to the real HTTPS domain
- [ ] Sentry DSN is configured
- [ ] seed admin/staff phone numbers match the restaurant team

## Infrastructure

- [ ] real domain resolves to the server
- [ ] TLS certificate is installed and active
- [ ] Docker stack deploy succeeds
- [ ] `/api/v1/health` returns `200`
- [ ] `/`, `/staff`, and `/admin` return `200`
- [ ] nightly backup cron is installed
- [ ] one backup file has been created successfully

## Functional Verification

- [ ] customer OTP request works with a real phone
- [ ] customer OTP verify works with a real phone
- [ ] customer dashboard loads after login
- [ ] staff can search a customer by phone
- [ ] staff can register a purchase
- [ ] points/tier/discount update correctly
- [ ] admin can view audit logs
- [ ] admin can view fraud flags
- [ ] customer CSV export downloads

## Wallet Verification

- [ ] `.pkpass` downloads successfully
- [ ] `.pkpass` installs on a real iPhone
- [ ] pass shows points, member ID, tier, discount, and barcode
- [ ] pass refreshes after a purchase
- [ ] wallet registration/update endpoints respond correctly

## Operations

- [ ] uptime monitoring is active
- [ ] CPU/RAM/disk alerts are active
- [ ] SMS failure alerts are active
- [ ] Sentry error tracking is active
- [ ] one restore drill has succeeded
- [ ] cashier staff training is complete
- [ ] incident checklist has been reviewed with the team

## Launch Strategy

- [ ] launch with one branch first
- [ ] one admin owner is designated for support
- [ ] one cashier shift has been briefed
- [ ] rollback plan is defined if OTP or wallet issues appear
