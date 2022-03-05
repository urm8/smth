#!/usr/bin/env bash
set -e

echo 'Collecting static...'
mkdir -p tasks_api/static; python manage.py collectstatic --noinput || true

if [ -n "$REDIS_URI" ]; then
    read -r REDIS_HOST REDIS_PORT <<< $(python -c 'import os, furl; f = furl.furl(os.getenv("REDIS_URI")); print(f.host, f.port)')
    echo 'waiting redis...'
    while ! nc -z "$REDIS_HOST" "$REDIS_PORT"; do
        sleep 0.5
    done
else
    echo 'REDIS_URI not set skip waiting for redis...'
fi

if [ -n "$DB_URI" ]; then
    echo "waiting db..."
    read -r DB_HOST DB_PORT <<< $(python -c 'import os, furl; f = furl.furl(os.getenv("DB_URI")); print(f.host, f.port)')
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        sleep 0.5
    done
    echo 'running migrations...'
    python manage.py migrate --noinput
else
    echo 'DB_URI not set skip waiting for db...'
fi


echo "Starting app $VERSION"
exec "$@"
