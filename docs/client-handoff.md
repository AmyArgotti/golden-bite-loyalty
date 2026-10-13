# Golden Bite Loyalty Client Handoff

## Project Summary

Golden Bite Loyalty is a production-oriented loyalty platform for a restaurant with three main surfaces:

- customer app
- staff panel
- admin panel

It supports:

- phone number login with OTP
- loyalty account creation
- points, tiers, discounts, and transaction history
- staff purchase registration and point redemption
- admin oversight, audit logs, fraud review, and customer export
- Apple Wallet pass generation and refresh support

## Delivered Scope

### Customer Experience

- phone registration/login with OTP
- customer profile
- loyalty dashboard
- points balance and tier view
- barcode and QR values
- transaction history
- Apple Wallet generation flow

### Staff Experience

- staff OTP login
- customer lookup by phone or member ID
- scan-based lookup
- purchase registration
- points redemption
- manual adjustment with comments
- quick customer activity view

### Admin Experience

- admin OTP login
- KPI dashboard
- loyalty rule editing
- staff user management
- audit logs
- fraud review queue
- customer CSV export

### Operations

- Docker-based deployment
- production compose stack
- database migration flow
- backup and restore scripts
- smoke-check and env validation scripts
- launch-day and incident runbooks

## What The Client Still Needs To Provide

- real SMS provider credentials
- real Apple Wallet certificate files
- live domain and SSL certificate
- manager/admin/staff phone numbers for production
- branded wallet assets if a polished pass design is required

## Launch Recommendation

Launch with:

- one branch
- one manager owner
- one trained cashier shift
- one day of close observation after go-live

## Success Criteria

The project should be considered successfully launched when:

- customers can log in with OTP
- staff can register purchases and see points update
- admins can review activity and exports
- backups are running
- the first real iPhone wallet pass installs successfully
