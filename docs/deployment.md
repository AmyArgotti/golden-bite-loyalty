# Deployment And 24/7 Operations

## Minimum Launch Topology

For one restaurant, start with one production VPS:

- 2 to 4 vCPU
- 4 to 8 GB RAM
- 80 to 160 GB SSD
- Ubuntu LTS

Run these services:

- `nginx`
- `backend-api`
- `customer-web`
- `staff-panel`
- `admin-panel`
- `worker`
- `postgres`
- `redis`

Customer, staff, and admin frontends are now wired as Next.js apps behind Nginx in the production compose stack.

## Keep It Running 24/7

### Service management

- Use Docker Compose with `restart: unless-stopped`
- Health checks on API, Redis, PostgreSQL, and web apps
- Separate worker process for scheduled jobs
- Log rotation enabled on server

### Monitoring

- Uptime monitor on `/api/v1/health`
- Sentry for backend and frontend errors
- Basic server monitoring for CPU, RAM, disk, and restart count
- Alert on SMS failures, wallet sync failures, and job failures

### Backups

- Nightly PostgreSQL dump
- Keep `14` daily backups
- Weekly offsite copy to S3-compatible storage
- Monthly restore test

### Security

- HTTPS only with Let's Encrypt
- Strong app secret rotation policy
- Separate admin/staff permissions
- IP logging on sensitive actions
- Audit logs retained for all point changes

## Recommended Environments

- `dev`: local Docker Compose
- `staging`: production-like server for testing changes
- `prod`: live restaurant system

## Operational Checklist

- SSL active
- Backups verified
- Monitoring alerts configured
- Admin seed user created
- SMS provider credentials configured
- Apple Wallet certificate installed
- Environment variables stored securely

## Recommended Production Assumption

For the current repository shape, the cleanest production layout is:

- customer app: `https://loyalty.goldenbite.com/`
- staff panel: `https://loyalty.goldenbite.com/staff`
- admin panel: `https://loyalty.goldenbite.com/admin`
- API: `https://loyalty.goldenbite.com/api/v1`

Recommended SMS provider for MVP launch:

- Twilio

See:

- [.env.production.example](/path/to/golden-bite-loyalty/.env.production.example)
- [loyalty.goldenbite.com.conf.example](/path/to/golden-bite-loyalty/infrastructure/nginx/loyalty.goldenbite.com.conf.example)
- [production-launch-checklist.md](/path/to/golden-bite-loyalty/docs/production-launch-checklist.md)
