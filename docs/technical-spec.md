# Golden Bite Loyalty Technical Plan

## Architecture

### Frontend

- `apps/web`: Next.js customer cabinet and PWA fallback
- `apps/staff-panel`: Next.js staff workflow for search, scan, purchases, redemption
- `apps/admin-panel`: Next.js admin tools for staff management, audit, rules, and reporting

### Backend

- `backend/app/api`: FastAPI routers
- `backend/app/services`: business rules and domain logic
- `backend/app/repositories`: database access layer
- `backend/app/models`: SQLAlchemy models
- `backend/app/schemas`: request and response contracts
- `backend/app/tasks`: scheduled and async jobs

### Infrastructure

- PostgreSQL: source of truth
- Redis: OTP throttling, short-lived state, job broker
- Worker: scheduled jobs and background updates
- Nginx: HTTPS, proxy, caching headers
- Docker Compose: service orchestration

## Real-World MVP Scope

### Include in v1

- Customer OTP auth
- Consent capture
- Loyalty account creation
- Points, tier, and discount calculations
- QR/barcode generation
- Purchase registration by staff
- Manual adjustment with audit logs
- Customer transaction history
- Wallet pass generation and refresh

### Delay to v2

- Referral automation
- Birthday bonus automation
- Campaign engine
- Fraud dashboard UI
- POS integrations

## Suggested Backend Modules

- `auth`: OTP request, verify, sessions, logout
- `me`: current user profile and preferences
- `loyalty`: loyalty dashboard and transactions
- `wallet`: pass generation, status, refresh
- `staff`: customer lookup, purchase registration, redemption, adjustments
- `admin`: staff management, rules, reports, audit, fraud flags

## Core Business Rules

- Earn rate: `floor(purchase_amount / 10)`
- Bronze: `0-999`
- Silver: `1000-2999`
- Gold: `3000+`
- Bronze discount: `0%`
- Silver discount: `5%`
- Gold discount: `10%`

## Security Baseline

- HTTPS only
- OTP TTL: `300` seconds
- OTP max attempts: `5`
- Phone send limit: `3 / 15 min`
- IP/device send limit: `10 / hour`
- HttpOnly secure cookies for refresh sessions
- RBAC for customer, staff, admin, super admin
- Audit record for every point-changing action
- Hashed OTP and hashed refresh tokens

## Recommended Milestones

1. Auth, users, sessions, loyalty tables, migrations
2. Customer dashboard and transaction history
3. Staff panel and purchase registration
4. Wallet support
5. Admin tools and production hardening
