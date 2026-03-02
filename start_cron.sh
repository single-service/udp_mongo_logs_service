#!/bin/bash
# /app/export_env.sh
env | grep -E "DB_URL|LOG_RETENTION_DAYS|IS_ASYNC" > /app/.env
/usr/sbin/cron -f