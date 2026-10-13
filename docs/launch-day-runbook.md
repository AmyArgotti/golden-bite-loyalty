# Launch Day Runbook

## Goal

Launch Golden Bite Loyalty with one branch, one manager owner, and one trained cashier shift.

## Roles

- Launch owner:
  the person responsible for the final go/no-go decision
- Technical operator:
  the person running deploy, smoke checks, and server verification
- Restaurant manager:
  the person approving staff readiness and customer-facing launch
- Cashier champion:
  the first cashier using the staff panel during live service

## Before Opening

1. confirm the production server is reachable
2. confirm `.env` is complete and validated
3. confirm deploy succeeds
4. confirm smoke checks pass
5. confirm Twilio OTP works with one real phone
6. confirm Apple Wallet pass installs on one real iPhone
7. confirm seeded or created admin/staff accounts are correct
8. confirm backup job is installed

## Exact Launch Sequence

### 1. Validate config

```bash
cd /path/to/golden-bite-loyalty
ENV_FILE=/path/to/golden-bite-loyalty/.env APP_ENV_EXPECTED=production infrastructure/scripts/validate_env.sh
```

### 2. Deploy

```bash
cd /path/to/golden-bite-loyalty
infrastructure/scripts/deploy.sh
```

### 3. Smoke check

```bash
BASE_URL=https://your-real-domain.com infrastructure/scripts/smoke_check.sh
```

### 4. Seed or confirm staff/admin users

```bash
cd /path/to/golden-bite-loyalty
set -a
source .env
set +a
PYTHONPATH=backend python3 backend/app/db/seed.py
```

### 5. OTP test

- request OTP with one real customer phone
- verify login succeeds
- confirm customer dashboard loads

### 6. Wallet test

- generate `.pkpass`
- install on one real iPhone
- confirm member ID, points, tier, discount, and barcode are visible

### 7. Staff flow test

- log into `/staff`
- search the test customer
- register a purchase
- confirm points update
- confirm the wallet pass refresh path works

### 8. Admin flow test

- log into `/admin`
- confirm dashboard loads
- confirm fraud flags page loads
- confirm audit logs record the test actions

## Go / No-Go Rule

Go only if all are true:

- deploy succeeded
- smoke checks passed
- OTP works on a real phone
- staff purchase flow works end-to-end
- admin audit trail reflects the actions
- one backup can be created successfully

No-Go if any are false:

- OTP delivery fails
- staff cannot register purchases
- wallet pass cannot be installed
- audit logs are missing
- backups do not run

## During First Service Window

- keep one admin logged into the owner panel
- keep one trained cashier on the staff panel
- use one test customer account once more after the first real transaction
- watch for:
  - OTP send failures
  - incorrect point calculation
  - wallet pass not refreshing
  - staff selecting the wrong customer

## After First Successful Transactions

- run one manual backup
- review audit logs
- review fraud flags
- collect cashier feedback
- collect manager feedback

## If Something Fails

- OTP issue:
  check SMS provider status and audit logs
- points issue:
  review audit log and reverse with a documented manual adjustment
- wallet issue:
  confirm pass signing and wallet web-service URL
- full outage:
  pause loyalty actions and record purchases for later reconciliation
