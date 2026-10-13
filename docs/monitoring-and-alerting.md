# Monitoring And Alerting

## Minimum Monitoring Stack

- uptime monitor for `/api/v1/health`
- uptime monitor for `/`, `/staff`, and `/admin`
- Sentry for backend errors
- server metrics for CPU, RAM, and disk
- cron backup log monitoring

## Alerts To Configure

- API health fails twice in a row
- staff or admin panel becomes unavailable
- disk usage exceeds `80%`
- memory pressure remains high
- backup job has not produced a file in `24` hours
- elevated OTP `503` responses
- repeated `auth.send_otp_failed` audit events
- wallet pass generation returns `5xx`

## Sentry

Set these env vars:

- `SENTRY_DSN`
- `SENTRY_ENVIRONMENT`
- `SENTRY_TRACES_SAMPLE_RATE`

Backend Sentry is initialized automatically when `SENTRY_DSN` is set.

## Daily Review

- check uptime dashboard
- check recent Sentry issues
- check recent fraud flags
- confirm latest backup exists
- confirm no unusual OTP delivery failures
