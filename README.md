# FoodFlow — Monorepo

Production-oriented food delivery platform: Django + DRF API with a Next.js frontend.

```text
foodflow/
├── docker-compose.yml      # full stack: db + redis + web + workers + frontend
├── backend/                # Django + DRF API (see backend/README.md)
│   ├── manage.py
│   ├── pyproject.toml
│   ├── config/             # settings (base/local/production/test), urls, asgi/wsgi, celery
│   ├── apps/               # accounts, restaurants, menu, carts, orders, payments, …
│   ├── tests/              # unit + integration
│   ├── scripts/            # docker-entrypoint.sh
│   └── docs/               # architecture.md
└── frontend/               # Next.js restaurant app (see frontend/README.md)
    ├── package.json
    ├── next.config.js
    ├── pages/
    ├── public/
    └── src/
```

## Quick start

### Backend (Django API)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

API: `http://127.0.0.1:8000/api/v1/` · Docs: `http://127.0.0.1:8000/api/docs/`
Full backend guide: [`backend/README.md`](backend/README.md).

### Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.example .env.local   # sets NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Site: `http://localhost:3000` · Admin: `http://localhost:3000/admin/login`
Full frontend guide: [`frontend/README.md`](frontend/README.md).

### Full stack (Docker)

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- API: `http://localhost:8000/api/v1/` · Swagger: `http://localhost:8000/api/docs/`
- Container env overrides: copy `backend/.env.docker.example` to
  `backend/.env.docker` (gitignored). Infra addresses (`DATABASE_URL`,
  `REDIS_URL`, …) live in `docker-compose.yml`.

## Tests / lint

```bash
cd backend
pytest
ruff check .
ruff format --check .
```
