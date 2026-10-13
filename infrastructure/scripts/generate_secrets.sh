#!/usr/bin/env bash
set -euo pipefail

openssl rand -hex 32 | awk '{print "SECRET_KEY="$0}'
openssl rand -hex 24 | awk '{print "POSTGRES_PASSWORD="$0}'
