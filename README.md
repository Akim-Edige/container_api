# Container Storage API

REST API for managing shipping containers and storage zones, built with FastAPI and PostgreSQL. Includes optional WebSocket events and Docker tooling for local development.

## Features
- CRUD-style endpoints for containers and zones
- Capacity tracking with automatic load adjustments on arrival/departure
- WebSocket broadcasts for container updates
- Docker Compose stack with PostgreSQL

## Requirements
- Python 3.11+
- PostgreSQL 13+ (if running without Docker)

## Quick Start (Docker)
```bash
cp env.example .env
docker-compose up --build
```
On first boot the `api` service waits for PostgreSQL, runs `python -m scripts.seed`,
and leaves you with demo zones/containers (including an overflow scenario). To
reset the data, run `docker-compose down -v` and start again. API docs live at
`http://localhost:8000/docs`.

## Local Development
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/container_db
python -m scripts.seed  # optional but gives you demo data
uvicorn app.main:app --reload
```

Create the database manually (or via Docker) before starting the API. Tables are created automatically on startup, and the seed script skips reruns once data exists.

## API Overview
| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET    | /containers | List all containers |
| POST   | /containers | Create container (increments zone load) |
| PATCH  | /containers/{id} | Update status (departures decrement load) |
| GET    | /zones | List zones |
| POST   | /zones/{id}/assign | Assign container to zone with capacity check |

`HTTP 400 Zone Overloaded` is returned on capacity breaches. Container status values: `arrived`, `stored`, `departed`.

## WebSocket
Connect to `ws://localhost:8000/ws/containers` to receive `container.created`, `container.updated`, and `container.assigned` events.

## Environment Variables
- `DATABASE_URL` – SQLAlchemy async URL to PostgreSQL (see `env.example`).

## Testing (manual)
Use `curl`/Postman:
```bash
curl -X POST http://localhost:8000/containers \
  -H "Content-Type: application/json" \
  -d '{"number":"CONT-001","type":"40ft","status":"arrived","zone_id":1}'
```

## License
MIT

