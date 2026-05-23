# Django Microservices: Bookshop + Warehouse

A two-service Django microservices architecture with a React frontend, Postgres, Redis, and Celery — orchestrated with Docker Compose and routed through NGINX.

## Architecture

```
                      ┌────────────────┐
                      │     NGINX      │
                      │   (port 80)    │
                      └──────┬─────────┘
              ┌──────────────┼──────────────────────┐
              ▼              ▼                      ▼
     ┌───────────────┐ ┌────────────────┐ ┌────────────────────┐
     │   ProjectA    │ │   ProjectB     │ │   React Frontend   │
     │   Bookshop    │ │   Warehouse    │ │   (Vite + TS)      │
     │  (port 8000)  │ │  (port 8001)   │ │                    │
     └───────┬───────┘ └────────┬───────┘ └────────────────────┘
             │                  │
   ┌─────────┴─────────┐  ┌─────┴────────┐
   │ Postgres A        │  │ Postgres B   │
   │ Redis A           │  │ Redis B      │
   │ Celery worker/beat│  │ Celery wk/bt │
   └───────────────────┘  └──────────────┘
```

* **ProjectA — Bookshop**: custom user model, books, orders, reviews, JWT auth, i18n (EN/UK), Redis cache, Swagger/Redoc, Sentry, WhiteNoise, Gunicorn.
* **ProjectB — Warehouse**: warehouses, stock items, stock movements, suppliers, low-stock Celery alerts, JWT auth, sync endpoint with ProjectA.
* **Frontend**: React + TS + Vite + Tailwind + Zustand + axios (with JWT refresh interceptor).

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Then open:
* **Frontend**: http://localhost/
* **ProjectA Swagger**: http://localhost/api/docs/
* **ProjectA admin**: http://localhost/admin/
* **ProjectA health**: http://localhost/health/
* **ProjectB Swagger**: http://localhost/warehouse/api/docs/
* **ProjectB admin**: http://localhost/warehouse-admin/
* **ProjectB health**: http://localhost/warehouse-health/

Create a superuser for ProjectA:
```bash
docker compose exec projecta python manage.py createsuperuser
```

## Tests

ProjectA:
```bash
cd projecta
pip install -r requirements.txt pytest-env
USE_SQLITE=1 pytest
```

ProjectB:
```bash
cd projectb
pip install -r requirements.txt pytest-env
USE_SQLITE=1 pytest
```

Both projects enforce `--cov-fail-under=70`.

Frontend:
```bash
cd frontend
npm install
npm run lint   # tsc --noEmit
npm run build
```

## Project layout

```
django-microservices/
├── docker-compose.yml
├── .env.example
├── nginx/nginx.conf
├── .github/workflows/ci.yml
├── projecta/                 # Bookshop service
│   ├── config/               # settings, urls, celery
│   ├── users/                # custom user model
│   ├── books/                # catalog
│   ├── orders/               # cart -> order flow
│   ├── core/                 # /health/
│   └── locale/{en,uk}/...
├── projectb/                 # Warehouse service
│   ├── config/
│   ├── warehouse/            # Warehouse / StockItem / StockMovement / Supplier
│   └── core/                 # /health/
└── frontend/                 # React + Vite + TS
    ├── src/
    │   ├── api/              # axios + JWT interceptor
    │   ├── store/            # zustand stores
    │   ├── components/
    │   └── pages/
    └── ...
```

## Cross-service sync

* `ProjectA → ProjectB`: when a book is created/updated, `books.tasks.notify_warehouse_of_book` posts to `POST /warehouse/api/sync/book/`.
* `ProjectB → ProjectA`: `warehouse.tasks.pull_books_from_projecta` (Celery beat, every 15 min) pulls the catalog and updates `StockItem` rows.
* `ProjectB` low-stock alerts: `warehouse.tasks.check_low_stock` runs hourly via Celery beat.

## Environment

See `.env.example` for the full list. Both services share a JWT signing key for cross-service token verification.
