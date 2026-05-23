#!/usr/bin/env bash
set -e

echo "Waiting for postgres..."
until python -c "import socket,os,sys; s=socket.socket(); s.settimeout(2);
host=os.environ.get('PROJECTA_DB_HOST','postgres_a');
port=int(os.environ.get('PROJECTA_DB_PORT','5432'));
sys.exit(0 if s.connect_ex((host,port))==0 else 1)" 2>/dev/null; do
    sleep 1
done
echo "Postgres is up."

# Celery containers share this image but only the web container should run
# migrations / compilemessages / collectstatic. Detect by the launch command.
case "$1" in
    celery)
        echo "Celery container detected — skipping migrations & static collection."
        # Give the web container a head start so migrations finish first.
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
