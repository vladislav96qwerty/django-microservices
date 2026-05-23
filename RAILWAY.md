# Deploying to Railway

Railway is the simplest free host for this project because it auto-injects
`DATABASE_URL`, `REDIS_URL`, and `PORT` and supports monorepos out of the box.

## What you'll create on Railway

```
┌──────────────────────────────────────────────────────────────┐
│  Project: django-microservices                                │
│                                                                │
│   Service: projecta-postgres     (Plugin: PostgreSQL)          │
│   Service: projectb-postgres     (Plugin: PostgreSQL)          │
│   Service: projecta-redis        (Plugin: Redis)               │
│   Service: projectb-redis        (Plugin: Redis)               │
│                                                                │
│   Service: projecta              (root: projecta)              │
│   Service: projecta-celery       (root: projecta) — worker     │
│   Service: projectb              (root: projectb)              │
│   Service: projectb-celery       (root: projectb) — worker     │
│   Service: frontend              (root: frontend)              │
└──────────────────────────────────────────────────────────────┘
```

## Step-by-step

### 1. Create the project and add databases / Redis

1. Push the repo to GitHub.
2. railway.app → **New Project** → **Deploy from GitHub repo** → pick this repo.
3. Inside the project, click **+ New → Database → Add PostgreSQL** twice (rename: `projecta-postgres`, `projectb-postgres`).
4. **+ New → Database → Add Redis** twice (rename: `projecta-redis`, `projectb-redis`).

### 2. Deploy ProjectA (web)

1. **+ New → GitHub Repo** → same repo.
2. Settings → **Root Directory**: `projecta`.
3. Settings → **Watch Paths**: `projecta/**`.
4. Variables tab — add (use the "Reference" button to pull values from the plugins):

   | Variable | Value |
   |---|---|
   | `DJANGO_SETTINGS_MODULE` | `config.settings_prod` |
   | `PROJECTA_SECRET_KEY` | (click "Generate" or paste a strong value) |
   | `JWT_SIGNING_KEY` | (paste a strong value — must match across all services) |
   | `DATABASE_URL` | `${{projecta-postgres.DATABASE_URL}}` |
   | `REDIS_URL` | `${{projecta-redis.REDIS_URL}}` |
   | `PROJECTB_HOST` | `${{projectb.RAILWAY_PRIVATE_DOMAIN}}` |
   | `CORS_ALLOWED_ORIGINS` | `https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}` |
   | `PROJECTA_SENTRY_DSN` | *(optional)* |

5. Settings → **Generate Domain** to get a public URL.

### 3. Deploy ProjectA Celery worker

1. **+ New → Empty Service** (or duplicate the projecta service).
2. Connect the same GitHub repo, Root Directory `projecta`.
3. Settings → **Custom Start Command**:
   ```
   celery -A config worker -l info --concurrency=2
   ```
4. Copy all environment variables from `projecta` (DATABASE_URL, REDIS_URL, JWT_SIGNING_KEY, PROJECTA_SECRET_KEY).
5. **Do not** generate a public domain — workers don't accept HTTP.

(Optionally repeat for celery beat with start command `celery -A config beat -l info`.)

### 4. Deploy ProjectB (web + worker)

Repeat steps 2–3 for `projectb`, referencing `projectb-postgres` / `projectb-redis` and setting:

   | Variable | Value |
   |---|---|
   | `PROJECTA_HOST` | `${{projecta.RAILWAY_PRIVATE_DOMAIN}}` |
   | `LOW_STOCK_THRESHOLD` | `10` |

### 5. Deploy the frontend

1. **+ New → GitHub Repo** → same repo, Root Directory `frontend`.
2. Variables:

   | Variable | Value |
   |---|---|
   | `VITE_API_BASE_URL` | `https://${{projecta.RAILWAY_PUBLIC_DOMAIN}}/api` |

3. Settings → **Generate Domain**.
4. After it's up, add the resulting URL to `projecta`'s `CORS_ALLOWED_ORIGINS` (if you didn't reference it dynamically) and redeploy projecta.

## Cross-service URLs explained

Railway gives each service two hostnames:

* `RAILWAY_PRIVATE_DOMAIN` — internal-only, e.g. `projectb.railway.internal:8080`. Free, low-latency.
* `RAILWAY_PUBLIC_DOMAIN` — public HTTPS, e.g. `projectb-production.up.railway.app`. Bills egress.

Our `settings_prod.py` detects `.railway.internal` and uses `http://` automatically (no TLS on the private mesh). For everything else it uses `https://`.

## Pricing

Free trial gives **$5 credit / month** which covers a small Postgres + Redis + a few hobby services with low traffic. To stay free:

* Use a single shared Postgres database for both services (set `DATABASE_URL` to the same value, use different `DATABASE_NAME`s).
* Skip celery beat (run cron via Railway Cron Jobs instead).
* Set service memory limits in Settings.

## Sanity-check after deploy

```
curl https://projecta-production.up.railway.app/health/
curl https://projectb-production.up.railway.app/health/
```

Both should return JSON with `"status": "ok"`.
