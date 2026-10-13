# Milestone Status

## Milestone 1

Included:

- FastAPI backend scaffold
- OTP request and verify
- customer/session creation
- loyalty account bootstrap
- customer profile and loyalty endpoints
- staff search, purchase, redeem, and manual adjustment logic
- admin dashboard and loyalty rule read/write endpoints
- seed script for admin/staff users
- Alembic initial migration
- OTP throttling by phone, IP, and device
- SMS provider abstraction and live-provider config seam
- unit, smoke, integration-style, and real pytest execution

Remaining polish:

- live SMS provider verification in staging
- stronger cookie/session hardening
- broader database-backed end-to-end tests

## Milestone 2

Included:

- Next.js customer app scaffold
- phone + OTP UI flow
- dashboard with loyalty card preview
- transaction history display
- profile editing flow
- wallet action buttons
- PWA manifest scaffold
- API client wiring to backend endpoints
- production build verification

Remaining polish:

- Google Wallet integration
- offline/PWA install polish
- richer customer profile/settings sections

## Milestone 3

Included:

- Next.js staff panel scaffold
- staff OTP login flow
- customer search by phone or member ID
- scan-based customer lookup
- customer selection for cashier actions
- customer quick-view and recent activity panel
- purchase registration UI
- points redemption UI
- manual adjustment UI
- production build verification

Remaining polish:

- QR/barcode scanning camera flow
- branch selector
- stronger cashier permissions UX

## Milestone 4

Included:

- Apple Wallet pass generation
- optional pass signing support
- stable pass serial per member
- wallet package asset pipeline
- wallet registration and update polling endpoints
- automatic pass regeneration after purchases, redemptions, and adjustments

Remaining polish:

- APNs push notifications
- Google Wallet implementation
- richer production pass image set and branding assets

## Milestone 5

Included:

- Next.js admin panel scaffold
- admin OTP login flow
- KPI dashboard view
- loyalty rules view
- staff roster view
- audit log view
- staff management actions
- loyalty rule editing
- fraud flag API and UI
- production build verification

Remaining polish:

- campaign flows
- richer reporting dashboards

## Phase 6 Hardening

Included:

- production compose stack for backend plus customer, staff, and admin apps
- Nginx routing for `/`, `/staff`, `/admin`, and `/api`
- deploy, backup, and restore scripts
- monitoring and runbook documentation
- real backend pytest verification

Remaining polish:

- full staging pass with real SMS credentials and Apple certs
- production TLS and DNS verification on the target server
- restore drill against a staging database
