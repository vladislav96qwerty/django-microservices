#!/usr/bin/env bash
# Build script executed by Render for ProjectB (Warehouse).
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

echo "==> ProjectB build complete"
