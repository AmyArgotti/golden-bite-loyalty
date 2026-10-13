# Operations Runbook

## Daily Checks

- confirm API health endpoint is green
- confirm customer web, staff panel, and admin panel are reachable through Nginx
- confirm latest backup file exists
- review recent audit logs for unusual point adjustments
- review fraud flags for OTP churn or large manual adjustments
- review OTP send failure rate
- confirm wallet pass refreshes are being generated after point-changing actions

## Deploy

```bash
infrastructure/scripts/deploy.sh
```

## Backup

```bash
DATABASE_URL=postgresql://... infrastructure/scripts/backup.sh
```

Default behavior:

- compress backup output as `.sql.gz`
- keep last `14` days unless `RETENTION_DAYS` is overridden

## Restore

```bash
DATABASE_URL=postgresql://... infrastructure/scripts/restore.sh backups/file.sql.gz
```

## Wallet Notes

- unsigned passes are acceptable only for local development
- production Apple Wallet requires pass signing certificate, key, and WWDR certificate
- wallet pass serial numbers stay stable per member so Apple registration/update polling can find the refreshed pass
- after loyalty balance changes, the backend regenerates any existing registered pass package automatically
- APNs push notifications are still not implemented, so Apple devices will rely on Wallet web-service polling until that is added

## SMS Notes

- `mock` provider is development-only
- `twilio` and `generic_http` are production-capable adapters
- verify live delivery in staging before launch and confirm `auth.send_otp` audit entries appear
