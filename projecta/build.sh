#!/usr/bin/env bash
# Build script executed by Render for ProjectA (Bookshop).
set -o errexit
set -o nounset
set -o pipefail

echo "==> Installing Python dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files"
python manage.py collectstatic --noinput --clear

echo "==> Applying database migrations"
python manage.py migrate --noinput

echo "==> Loading initial fixtures (idempotent)"
python manage.py loaddata initial_data || echo "    (no fixtures or already loaded)"

echo "==> ProjectA build complete"
