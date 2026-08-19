# Financial Ledger Backend

Multi-currency wallet and transaction API built with Django and DRF. Users register, manage wallets, deposit/withdraw funds, transfer between wallets, and receive real-time notifications over WebSockets.

**Stack:** Django 5 · DRF · PostgreSQL · Redis · RabbitMQ · Celery · Channels · uvicorn

## Architecture

```
Client → uvicorn (ASGI) → DRF APIs (/api/)
                              ↓
                    selectors (reads) / services (writes)
                              ↓
                         PostgreSQL

Celery worker ← RabbitMQ ← async tasks (e.g. high-value transfer alerts)
WebSocket     ← Redis    ← user notifications (/ws/notifications/)
```

| Layer | Role |
|---|---|
| `models/` | Fields, relations, constraints |
| `selectors/` | Read queries (`get_*`) |
| `services/` | Business writes (`create_*`, `transfer`, …) |
| `apis/` | HTTP validation → selector/service → response |
| `filters/` | Query-param filtering for list endpoints |

**Domain apps** under `ledger/`:

| App | Responsibility |
|---|---|
| `accounts` | Custom user model, validators |
| `authentication` | Register, login (JWT) |
| `wallets` | Wallet creation and listing |
| `transactions` | Deposits, withdrawals, transfers, immutable ledger |
| `notifications` | WebSocket consumer for user events |
| `core` | BaseModel, pagination, shared API plumbing |

HTTP routes are mounted at `/api/` (`config/urls.py` → `ledger/core/api/urls.py`).

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up -d --build
```

Migrations and initial data run automatically on API startup.

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/api/docs/ |
| Flower (Celery) | http://localhost:5555 |
| RabbitMQ UI | http://localhost:15672 |

Default superuser (created by `python manage.py initial`):

| Field | Value |
|---|---|
| username | `admin` |
| password | `admin123` |
| phone_number | `09000000000` |

## Local development (host)

**Requirements:** Python 3.12+, Docker (for infrastructure only)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pre-commit install          # optional — runs isort, black, ruff, flake8 on commit

cp .env.example .env
docker compose up -d db redis rabbitmq

python manage.py migrate
python manage.py initial
python -m uvicorn config.asgi:application --reload --host 0.0.0.0 --port 8000
```

Celery worker (separate terminal):

```bash
./scripts/run_worker.sh
```

## Tests

```bash
pytest
```

## Project layout

```
financial_ledger/
  config/              # settings, ASGI/WSGI, Celery, URL routing
  ledger/
    core/              # BaseModel, pagination, API mixins
    accounts/          # user model
    authentication/    # register / login
    wallets/           # wallet CRUD
    transactions/      # ledger entries, transfers, Celery tasks
    notifications/     # WebSocket consumers
  docker/              # container entrypoints
  scripts/             # host helper scripts (Celery worker)
  tests/               # pytest suite
```

## Migrations

Migration files are committed. After pulling:

```bash
python manage.py migrate
```

When you change models, generate and commit migrations in the same PR:

```bash
python manage.py makemigrations
python manage.py migrate
```
