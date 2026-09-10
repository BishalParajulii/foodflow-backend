# FoodFlow — Project Scaffolding (Phase 0)

Production-oriented food delivery platform. **This phase is scaffolding only.**

> No business functionality has been implemented. No models, serializers,
> views/ViewSets, API endpoints (beyond a project-level `/api/v1/` placeholder),
> Celery tasks, WebSocket consumers, Redis caching logic, payments, delivery
> assignment, PostGIS queries, notifications, frontend, or Docker configuration
> exists yet.

## Tech stack (ready, not yet implemented)

- Python 3.12+
- Django 5.x
- Django REST Framework
- PostgreSQL-ready configuration (`DATABASE_URL`)
- Django Channels-ready ASGI configuration
- Redis-ready cache / channel-layer / Celery configuration
- Celery-ready project configuration (`config/celery.py`)
- `pyproject.toml`-based project configuration
- Ruff, type hints, pytest + pytest-django

## Directory layout

```text
foodflow/
├── manage.py
├── pyproject.toml
├── README.md
├── .gitignore
├── .env.example
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   ├── celery.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── local.py
│       ├── production.py
│       └── test.py
├── apps/
│   ├── __init__.py
│   ├── accounts/ restaurants/ menu/ carts/ orders/ payments/
│   ├── delivery/ locations/ notifications/ reviews/ promotions/
│   ├── analytics/ common/
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   └── architecture.md
└── scripts/
    └── __init__.py
```

### Top-level directories

| Path | Purpose |
| --- | --- |
| `config/` | Django project configuration package: settings split (`base`/`local`/`production`/`test`), root URLs, WSGI/ASGI entrypoints, Celery app bootstrap. No business logic. |
| `apps/` | All first-party Django applications under the `apps.*` Python namespace. Each app currently contains only Django scaffolding. |
| `tests/` | Out-of-app test suites: `unit/` for isolated tests, `integration/` for cross-app/request tests. App-local `tests.py` files remain as Django placeholders. |
| `docs/` | Architecture documentation. Currently only `architecture.md` describing *planned* responsibilities. |
| `scripts/` | Placeholder package for future operational scripts (seed, lint, CI helpers). No scripts yet. |

### Django apps (planned responsibilities, not implemented)

| App | Planned responsibility |
| --- | --- |
| `accounts` | Users and authentication (future custom User model lives here) |
| `restaurants` | Restaurants and branches |
| `menu` | Menus and food items |
| `carts` | Shopping carts |
| `orders` | Order lifecycle |
| `payments` | Payment processing |
| `delivery` | Delivery partners and deliveries |
| `locations` | Geographic / location functionality |
| `notifications` | Notifications |
| `reviews` | Reviews and ratings |
| `promotions` | Coupons and promotions |
| `analytics` | Reporting and metrics |
| `common` | Shared utilities and abstractions |

See `docs/architecture.md` for details.

## Dependencies

Defined in `pyproject.toml`:

- Runtime: `Django`, `djangorestframework`, `django-environ`, `psycopg[binary]`, `channels`, `channels-redis`, `celery`, `redis`, `drf-spectacular`, `django-filter`, `djangorestframework-simplejwt`
- Dev: `pytest`, `pytest-django`, `ruff`

## Setup

### 1. Create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 2. Install dependencies

```bash
# Runtime only
pip install .

# With dev tools (ruff, pytest, pytest-django)
pip install ".[dev]"
```

> Alternative (pip directly from pyproject is equivalent to installing the
> packages listed under `dependencies` / `optional-dependencies`).

### 3. Environment variables

```bash
cp .env.example .env
# Edit .env as needed. Never commit .env.
```

No real `.env` with secrets is shipped. `.env.example` documents all placeholders.

### 4. Run the initial Django checks

```bash
python manage.py check
python manage.py check --settings=config.settings.production
python manage.py showmigrations --settings=config.settings.local
```

### 5. Run the development server

```bash
python manage.py migrate
python manage.py runserver
```

Then visit:

- `http://127.0.0.1:8000/` — Django placeholder root
- `http://127.0.0.1:8000/api/v1/` — versioned API placeholder namespace
- `http://127.0.0.1:8000/admin/` — admin (no app models registered yet)

No Redis server, Celery worker, or PostgreSQL server is required to boot.

### 6. Tests / lint

```bash
pytest
ruff check .
ruff format --check .
```

## Docker

Full stack: `web` (Gunicorn + Uvicorn ASGI) + `db` (Postgres 16) +
`redis` (Redis 7) + `celery_worker` + `celery_beat`.

```bash
docker compose up --build
# or detached:
docker compose up --build -d
```

Then visit:

- `http://localhost:8000/` — Django placeholder root
- `http://localhost:8000/api/v1/` — versioned API placeholder namespace
- `http://localhost:8000/admin/` — admin
- `http://localhost:8000/api/docs/` — Swagger UI

Useful commands:

```bash
docker compose ps
docker compose logs -f web
docker compose logs -f celery_worker celery_beat
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec db psql -U foodflow -d foodflow
docker compose down        # stop
docker compose down -v     # stop + wipe DB/Redis volumes
```

Notes:

- No env file is required. `docker-compose.yml` ships working local
  defaults (production settings with `SECURE_SSL_REDIRECT=False`,
  Postgres/Redis on the compose network). The local `.env` file is for
  `manage.py`/pytest runs only and never affects containers. To override
  container env (`SECRET_KEY`, `GOOGLE_CLIENT_ID`, …), copy
  `.env.docker.example` to `.env.docker` (gitignored); infra addresses
  (`DATABASE_URL`, `REDIS_URL`, …) are set in `docker-compose.yml` itself.
- Only `web` runs `migrate` + `collectstatic` on startup (via
  `scripts/docker-entrypoint.sh`). Workers/beat skip them to avoid
  concurrent-migrate races. Override with `RUN_MIGRATIONS=1/0`.
- For real deployments, set `SECRET_KEY`, `ALLOWED_HOSTS`, and
  `SECURE_SSL_REDIRECT=True` (behind HTTPS), plus a managed Postgres/Redis.

## Settings

| Module | Purpose |
| --- | --- |
| `config.settings.base` | Shared configuration: installed apps, middleware, templates, DRF defaults, i18n, static/media, password validation, default PK. |
| `config.settings.local` | Development: `DEBUG=True`, console email, SQLite default, `InMemoryChannelLayer`, locmem cache unless `REDIS_URL` is set up for opt-in Redis. |
| `config.settings.production` | Production placeholders: `DEBUG=False`, `ALLOWED_HOSTS` from env, secure cookies, HTTPS/HSTS, `DATABASE_URL`-driven DB, production logging. No secrets hard-coded. |
| `config.settings.test` | Automated tests: in-memory SQLite, locmem cache/email, in-memory channel layer, fast password hashers. |

`AUTH_USER_MODEL = "accounts.User"` (email-login custom user in `apps.accounts`).

## Response format

Every API response uses the envelope (all ids are UUID strings):

```json
// Success (2xx)
{ "success": true, "message": "Item added to cart.", "data": { "id": "…" } }

// Error (4xx)
{ "success": false,
  "error": { "code": "validation_error", "message": "Invalid input.",
             "details": { "price": ["Ensure this value is …"] } } }
```

Error `code`s: `validation_error`, `authentication_error`,
`permission_denied`, `not_found`, `throttled`, `integrity_error`.

## Auth API (`/api/v1/auth/`)

Email + JWT (SimpleJWT, access 60 min / refresh 7 days by default,
rotation + blacklist enabled).

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/signup/` | No | Register. Body: `email`, `password`, `password_confirm`, optional `first_name`, `last_name`, `phone`, `role` (`customer`/`restaurant_owner`/`delivery_partner`, default `customer`). Returns `201` with `user` + `access` + `refresh`. |
| POST | `/api/v1/auth/login/` | No | Body: `email`, `password`. Returns `access` + `refresh` + `user`. |
| POST | `/api/v1/auth/token/refresh/` | No | Body: `refresh`. Returns new `access` (+ rotated `refresh`). |
| GET/PATCH/PUT | `/api/v1/auth/me/` | Yes (`Bearer <access>`) | Read / update own profile (`first_name`, `last_name`, `phone`). `email`/`role` are read-only here. |
| POST | `/api/v1/auth/change-password/` | Yes | Body: `old_password`, `new_password`, `new_password_confirm`. |
| POST | `/api/v1/auth/logout/` | Yes | Body: `refresh`. Blacklists the refresh token. |
| POST | `/api/v1/auth/google/` | No | Gmail login. Body: `id_token` (Google ID token from Google Identity Services), optional `role` for new accounts. New emails auto-register (`is_verified=True`, unusable password); existing emails link. Returns `200` with `user` + `access` + `refresh` + `created`. Requires `GOOGLE_CLIENT_ID` env. |

Example:

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"StrongPass123!","password_confirm":"StrongPass123!","first_name":"Test"}'

curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"StrongPass123!"}'

curl http://localhost:8000/api/v1/auth/me/ \
  -H 'Authorization: Bearer <access>'
```

## Restaurants API (`/api/v1/restaurants/`)

Restaurant = brand/chain (e.g. "Momo House"). Each restaurant has many
**branches** (physical outlets), managed nested under it — one place.
Restaurant browsing is public; writes need the owner (any authenticated user
can register one — a `customer` is upgraded to `restaurant_owner`) or staff.
**Branches are fully private: list, read, create, update and delete all
require the restaurant's owner or an admin** (`is_staff`/`is_superuser` or
`role=admin`).

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/api/v1/restaurants/` | No | List (search `?search=` name/description/address). |
| POST | `/api/v1/restaurants/` | Yes | Register. Body: `name`, optional `description`, `phone`, `address`, `logo_url`. Slug auto-generated. |
| GET/PATCH/PUT/DELETE | `/api/v1/restaurants/<id>/` | R/W | Detail nests `branches` + `branches_count`; edit owner/staff only. |
| GET/POST | `/api/v1/restaurants/<id>/branches/` | Owner/admin | List/add outlets. Body: `name`, optional `address`, `phone`, `latitude`/`longitude`, `opening_time`/`closing_time`, `is_active`. Slug auto-generated per restaurant. |
| GET/PATCH/PUT/DELETE | `/api/v1/restaurants/<id>/branches/<bid>/` | Owner/admin | Scoped to the parent — another restaurant's branch returns 404. |

## Menu API (`/api/v1/menu/`)

Public read (storefront browsing); writes need the restaurant's owner or
staff. Slugs auto-generate and stay unique per scope (`momos`, `momos-2`).

| Method | Endpoints | Description |
| --- | --- | --- |
| GET/POST | `/api/v1/menu/categories/` | List (`?restaurant=`, `?is_active=`, `?search=`) / create (`restaurant`, `name`, …). |
| GET/PATCH/PUT/DELETE | `/api/v1/menu/categories/<id>/` | Includes `items_count`. |
| GET/POST | `/api/v1/menu/items/` | List (`?restaurant=`, `?category=`, `?is_veg=`, `?is_available=`, `?min_price=`/`?max_price=`, `?search=`, `?ordering=price`) / create (`category`, `name`, `price`, optional `compare_at_price` ≥ price, `is_veg`, `is_available`, `preparation_time_minutes`, `modifier_groups: [ids]`). |
| GET/… | `/api/v1/menu/items/<id>/` | Detail nests `modifier_groups_detail` → options; exposes `category_name`, `restaurant_id`. |
| GET/POST | `/api/v1/menu/modifier-groups/` | Choice sets (`?restaurant=`), e.g. Size `min_select=1/max_select=1`, extras `min_select=0`. `min_select ≤ max_select` enforced (400 otherwise). |
| GET/POST | `/api/v1/menu/modifier-options/` | Options within a group (`group`, `name`, `price_delta` ≥ 0). |

 Queryset helpers: `Category.objects.active()`, `MenuItem.objects.available()`.

Example:

```bash
TOKEN=<access-token>
curl -X POST http://localhost:8000/api/v1/restaurants/ \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"Momo House"}'                                   # -> {"id": 1, ...}

curl -X POST http://localhost:8000/api/v1/menu/categories/ \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"restaurant":1,"name":"Momos"}'

curl 'http://localhost:8000/api/v1/menu/items/?restaurant=1&is_veg=true'
```

### Gmail login setup

1. Create a Web OAuth client in Google Cloud Console (APIs & Services >
   Credentials) and set `GOOGLE_CLIENT_ID` in `.env` for local runs and/or
   `.env.docker` for containers (see `.env.example` / `.env.docker.example`).
2. In the client app, sign in with Google Identity Services to get an ID token.
3. POST it to the backend:

```bash
curl -X POST http://localhost:8000/api/v1/auth/google/ \
  -H 'Content-Type: application/json' \
  -d '{"id_token":"<google-id-token>"}'
```

## Cart API (`/api/v1/cart/`)

One active cart per authenticated user (auto-created, empty `200` when new).
Single-restaurant rule: the cart locks to the first item's restaurant; adding
from another returns 400 until `DELETE clear/`. Lines are modifier-aware —
same item + same options merge quantities, different options stay separate
lines. Totals are live off the menu (orders will freeze prices at checkout).

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/v1/cart/` | My cart: nested `items` (unit/line totals, option detail), `item_count`, `subtotal`. |
| POST | `/api/v1/cart/items/` | Add: `menu_item`, `quantity` (1–99), `selected_options: [ids]`. Validates availability, option↔item compatibility and group min/max (required groups enforced). Returns the cart. |
| PATCH/DELETE | `/api/v1/cart/items/<id>/` | Change quantity/options, or remove the line (restaurant lock resets when emptied). Users can only touch their own lines (404 otherwise). |
| DELETE | `/api/v1/cart/clear/` | Empty the cart. |

Example:

```bash
curl -X POST http://localhost:8000/api/v1/cart/items/ \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"menu_item":1,"quantity":2,"selected_options":[3]}'
```

## Orders API (`/api/v1/orders/`)

Checkout freezes cart lines into an order (prices + modifier choices are
snapshotted; later menu edits never rewrite history) and clears the cart.
Lifecycle: `pending -> confirmed -> preparing -> ready -> out_for_delivery ->
delivered`, plus `cancelled` from `pending`/`confirmed`/`preparing`.

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/v1/orders/` | Checkout my cart. Optional `delivery_address`, `phone`, `notes`. Empty cart returns 400 `empty_cart`; stale/unavailable lines return 400. Returns `201` with nested `items` (frozen `unit_price`/`line_total`, option snapshot), `item_count`, `subtotal`/`total`. |
| GET | `/api/v1/orders/` | History (`?status=`, `?restaurant=`, `?ordering=-created_at`). Customers see own; restaurant owners also see their restaurant's; staff see all. |
| GET | `/api/v1/orders/<id>/` | Detail. Owner, restaurant owner, or admin (others 404). |
| PATCH | `/api/v1/orders/<id>/` | Update `status` only. Customers can only cancel `pending`/`confirmed`; forward moves need the restaurant owner/staff. Invalid jumps return 400. |
| POST | `/api/v1/orders/<id>/cancel/` | Cancel shortcut (same rules as `PATCH {"status":"cancelled"}`). |

Example:

```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"delivery_address":"Thamel","phone":"+9779800000001"}'

curl -X PATCH http://localhost:8000/api/v1/orders/<id>/ \
  -H "Authorization: Bearer $OWNER_TOKEN" -H 'Content-Type: application/json' \
  -d '{"status":"confirmed"}'
```

## API versioning

Namespace: `/api/v1/`. Implemented: `/api/v1/auth/`,
`/api/v1/restaurants/`, `/api/v1/menu/`, `/api/v1/cart/`, `/api/v1/orders/`.
Planned (not implemented):

```text
/api/v1/payments/ /api/v1/delivery/
```

`config/urls.py` exposes the project-level `/api/v1/` placeholder plus
`include()` hooks per app, and OpenAPI schema/docs via `drf-spectacular`.

## Status

- [x] Accounts: email-login User, JWT signup/login/refresh, Google login,
      profile, change-password, logout (blacklist)
- [x] Restaurants: brand + nested branches (owner/admin-only branch
      management), public browsing, owner-or-staff writes
- [x] Menu: categories, items, modifier groups/options; public read,
      owner-or-staff write; filters/search/ordering
- [x] Cart: per-user singleton, single-restaurant lock, modifier-aware lines,
      live totals; auth-only
- [x] Orders: checkout snapshot (frozen prices/options), history scoping,
      status state machine + cancel; auth-only
- [x] No Celery tasks
- [x] No Channels consumers / routing / WebSocket endpoints
- [x] No Redis caching logic
- [x] No payments / delivery / PostGIS / notifications logic
- [x] No frontend
- [x] Docker stack (`Dockerfile` + `docker-compose.yml` + Postgres/Redis/Celery)

Next: payments.
