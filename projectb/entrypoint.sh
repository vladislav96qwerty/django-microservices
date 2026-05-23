#!/usr/bin/env bash
set -e

if [ -z "$DATABASE_URL" ]; then
    echo "Waiting for postgres..."
    until python -c "import socket,os,sys; s=socket.socket(); s.settimeout(2);
host=os.environ.get('PROJECTB_DB_HOST','postgres_b');
port=int(os.environ.get('PROJECTB_DB_PORT','5432'));
sys.exit(0 if s.connect_ex((host,port))==0 else 1)" 2>/dev/null; do
        sleep 1
    done
    echo "Postgres is up."
fi

case "$1" in
    celery)
        echo "Celery container — skipping migrations & static collection."
        sleep 5
        ;;
    *)
        echo "Running migrations..."
        python manage.py migrate --noinput
        echo "Collecting static files..."
        python manage.py collectstatic --noinput || true

        if [ "$BOOTSTRAP" = "1" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
            echo "==> BOOTSTRAP=1: ensuring superuser '$DJANGO_SUPERUSER_USERNAME' exists..."
            python manage.py createsuperuser --noinput || echo "  (superuser already exists)"
        fi
        ;;
esac

exec "$@"
