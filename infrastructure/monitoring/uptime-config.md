# Uptime Monitoring

Monitor these endpoints and signals:

- `GET /api/v1/health`
- web app root `/`
- staff panel root `/staff/`
- admin panel root `/admin/`
- Apple Wallet download endpoint `/api/v1/wallet/status` for authenticated smoke checks

Alert when:

- health endpoint fails 2 checks in a row
- wallet pass generation returns `5xx`
- fraud flag volume spikes unusually in a short period
- OTP request returns elevated `503`
- disk usage exceeds `80%`
- backup job does not run in the last `24` hours

Recommended cadence:

- uptime checks every `1` minute
- server resource checks every `5` minutes
- backup verification daily
