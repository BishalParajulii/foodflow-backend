# FoodFlow Architecture (Phase 0 — Scaffolding Only)

> All app responsibilities below are **planned**, not implemented.
> No models, serializers, views, endpoints, tasks, consumers, or business
> logic exist yet.

## Overview

- `config/` — Django project configuration (settings split, URLs, WSGI/ASGI, Celery bootstrap).
- `apps/` — First-party Django apps under the `apps.*` namespace.
- `tests/` — `unit/` (isolated) and `integration/` (cross-app / request-level) suites.
- `docs/` — Architecture notes (this file).
- `scripts/` — Future operational scripts (empty placeholder).
- API namespace — `/api/v1/` (project-level placeholder only).

## Planned app responsibilities

| App | Planned responsibility | Notes for later phases |
| --- | --- | --- |
| `accounts` | users and authentication | Future home of custom `User` model (`AUTH_USER_MODEL`). No User model yet. |
| `restaurants` | restaurants and branches | Menus link here later; no models yet. |
| `menu` | menus and food items | Categories, items, modifiers later; no models yet. |
| `carts` | shopping carts | Session/user cart lifecycle later; no logic yet. |
| `orders` | order lifecycle | State machine, totals, history later; no logic yet. |
| `payments` | payment processing | Provider integration, webhooks later; no logic yet. |
| `delivery` | delivery partners and deliveries | Assignment, tracking later; no logic yet. |
| `locations` | geographic / location functionality | Addresses, zones, (PostGIS later if needed); no queries yet. |
| `notifications` | notifications | Email/SMS/push fan-out later (Celery + Channels); no logic yet. |
| `reviews` | reviews and ratings | Restaurant/item ratings later; no logic yet. |
| `promotions` | coupons and promotions | Codes, discounts, campaigns later; no logic yet. |
| `analytics` | reporting and metrics | Aggregates, dashboards later; no logic yet. |
| `common` | shared utilities | Future base models, mixins, permissions, pagination, exceptions. No utilities yet. |

## Cross-cutting readiness (no functionality)

- **PostgreSQL-ready**: `DATABASE_URL` via `django-environ`; SQLite fallback so the project boots without a DB server.
- **Redis-ready**: `REDIS_URL` / `CELERY_*` env vars; `locmem` cache + `InMemoryChannelLayer` by default so no Redis server is required to boot.
- **Celery-ready**: `config/celery.py` + `CELERY_*` settings + `autodiscover_tasks()`; zero tasks defined.
- **Channels-ready**: `config/asgi.py` uses `ProtocolTypeRouter` with `http` wired and `websocket` left as a commented hook; no consumers/routing/groups.
- **DRF foundation**: global auth/permission/pagination/renderers/parsers/throttling placeholders + `drf-spectacular` OpenAPI settings; no serializers/views/endpoints beyond the project-level `/api/v1/` placeholder.
- **Auth preparation**: `AUTH_USER_MODEL` intentionally unset (commented placeholder in `base.py`) until the custom User model is added.

## Settings

- `base.py` — shared config.
- `local.py` — `DEBUG=True`, console email, dev defaults.
- `production.py` — `DEBUG=False`, `ALLOWED_HOSTS` from env, secure cookies, HTTPS/HSTS, production logging; no secrets hard-coded.
- `test.py` — in-memory SQLite, locmem cache/email, in-memory channels, fast hashers, eager Celery.

## What is explicitly out of scope for this phase

Models, serializers, views/ViewSets, routers, app URLs, Celery tasks,
consumers, Redis caching logic, payments, delivery assignment, PostGIS queries,
notifications, business logic, frontend, Docker.
