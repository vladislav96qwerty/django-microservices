#!/usr/bin/env bash
set -e

# Local docker-compose case: ping the postgres container before migrating.
# On Render/Railway the DB lives outside the container and DATABASE_URL is set,
# so we skip the socket ping (the platform guarantees the DB is up).
if [ -z "$DATABASE_URL" ]; then
    echo "Waiting for postgres..."
    until python -c "import socket,os,sys; s=socket.socket(); s.settimeout(2);
host=os.environ.get('PROJECTA_DB_HOST','postgres_a');
port=int(os.environ.get('PROJECTA_DB_PORT','5432'));
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

        echo "Compiling messages..."
        python manage.py compilemessages || true

        echo "Collecting static files..."
        python manage.py collectstatic --noinput || true
        ;;
esac

exec "$@"
