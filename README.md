# Financial Ledger Backend

Django + DRF backend (cookiecutter-django / HackSoftware styleguide).

## Setup with Docker

```bash
cp .env.example .env
docker compose up -d --build
```

| Service | URL |
|---|---|
| API (uvicorn) | http://localhost:8000 |
| Swagger | http://localhost:8000/api/docs/ |
| Flower | http://localhost:5555 |
| RabbitMQ UI | http://localhost:15672 |

## Setup on host

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d db redis rabbitmq
python manage.py migrate
python -m uvicorn config.asgi:application --reload --host 0.0.0.0 --port 8000
```

Run Celery worker on the host:

```bash
./scripts/run_worker.sh
```

## Tests

```bash
pytest
```

## Project structure

```
financial_ledger/
  config/          # Django settings, ASGI, Celery
  ledger/
    core/          # BaseModel, shared serializers, API plumbing
      api/         # mixins, pagination, renderers, url aggregator
    <domain_app>/  # add new apps here
  docker/          # api + celery entrypoints
  scripts/         # host helper scripts
```
