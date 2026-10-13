# Server Setup

## Recommended Host

- Ubuntu 24.04 LTS
- 2 to 4 vCPU
- 4 to 8 GB RAM
- 80 to 160 GB SSD

## Install Base Packages

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg nginx cron
```

## Install Docker

Follow Docker's Ubuntu instructions or use Docker Engine packages for:

- `docker`
- `docker compose`

Confirm:

```bash
docker --version
docker compose version
```

## Prepare App Directories

```bash
sudo mkdir -p /opt/golden-bite-loyalty
sudo mkdir -p /var/lib/golden-bite
sudo chown -R $USER:$USER /opt/golden-bite-loyalty
```

## Copy Project Files

Deploy the repository into:

```bash
/opt/golden-bite-loyalty
```

## Prepare Environment File

```bash
cd /opt/golden-bite-loyalty
cp .env.production.example .env
```

Edit `.env` with:

- real Postgres password
- real Twilio credentials
- real Apple Wallet values
- real production secrets

You can generate strong local placeholders with:

```bash
infrastructure/scripts/generate_secrets.sh
```

Validate it:

```bash
ENV_FILE=/opt/golden-bite-loyalty/.env infrastructure/scripts/validate_env.sh
```

## Prepare TLS

Use [loyalty.goldenbite.com.conf.example](/path/to/golden-bite-loyalty/infrastructure/nginx/loyalty.goldenbite.com.conf.example) as the production Nginx template and install a valid certificate for your real domain.

## Deploy

```bash
cd /opt/golden-bite-loyalty
infrastructure/scripts/deploy.sh
```

## Schedule Backups

```bash
cd /opt/golden-bite-loyalty
ENV_FILE=/opt/golden-bite-loyalty/.env infrastructure/scripts/install_backup_cron.sh
```

## Verify

- open `/api/v1/health`
- load `/`, `/staff`, and `/admin`
- request a real OTP
- generate a wallet pass
- run one backup

Quick smoke check:

```bash
BASE_URL=https://loyalty.goldenbite.com infrastructure/scripts/smoke_check.sh
```
