# Staging Checklist

## Before Deploy

- copy [.env.staging.example](/path/to/golden-bite-loyalty/.env.staging.example) to `.env`
- set a real `SECRET_KEY`
- set `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`
- make sure `DATABASE_URL` matches those same Postgres values exactly
- configure a live SMS provider
- place Apple Wallet signing cert, key, and WWDR cert on the server
- set `WALLET_WEB_SERVICE_URL` to the public HTTPS wallet endpoint
- point DNS to the staging server
- confirm TLS is working before wallet tests

## Deploy

```bash
cd /path/to/golden-bite-loyalty
infrastructure/scripts/deploy.sh
```

## Backend Verification

- open `GET /api/v1/health`
- log in with seeded admin and confirm admin dashboard loads
- confirm audit logs page renders
- confirm fraud flags page renders

## SMS Verification

1. request OTP using a real phone number
2. confirm the SMS is received within a reasonable time
3. verify the OTP using `/api/v1/auth/verify-otp`
4. confirm an `auth.send_otp` audit entry exists
5. if delivery fails, confirm an `auth.send_otp_failed` audit entry exists

## Wallet Verification

1. log into the customer app with a real phone
2. generate the Apple Wallet pass
3. confirm the downloaded `.pkpass` installs successfully
4. confirm the pass shows member ID, points, tier, discount, and barcode
5. register a purchase from the staff panel
6. confirm the pass package is regenerated
7. verify the wallet web-service registration and pass polling endpoints respond correctly

## Staff Verification

1. log into `/staff`
2. search a customer by phone
3. scan or paste a barcode/member ID
4. register a purchase
5. redeem points
6. apply a manual adjustment
7. confirm customer quick-view updates after each action

## Admin Verification

1. log into `/admin`
2. review KPI dashboard
3. create a new staff user
4. disable and re-enable a staff user
5. update loyalty rules
6. confirm audit entries reflect the changes
7. review fraud flags for suspicious OTP or adjustment activity

## Backup And Restore Verification

1. run `infrastructure/scripts/backup.sh`
2. confirm a compressed backup file appears in `backups/`
3. test `infrastructure/scripts/restore.sh` on a disposable database

## Known Remaining Gaps

- APNs push notifications for Apple Wallet are not implemented yet
- Google Wallet is not implemented yet
- campaign automation and referrals remain beyond MVP
