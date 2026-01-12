# Task Management API

A RESTful API for managing tasks built with FastAPI, SQLModel, and Neon PostgreSQL.

## Features

- Full CRUD operations for tasks
- Task filtering by status and priority
- Pagination support
- Input validation with Pydantic
- PostgreSQL database with Neon (serverless)
- Comprehensive test suite with pytest

## Tech Stack

- **Framework:** FastAPI
- **ORM:** SQLModel (SQLAlchemy + Pydantic)
- **Database:** Neon PostgreSQL
- **Testing:** pytest
- **Package Manager:** uv

## Project Structure

```
taskmanagement-api/
├── main.py           # FastAPI application and routes
├── models.py         # SQLModel table and schema definitions
├── database.py       # Database engine and session management
├── conftest.py       # Pytest fixtures
├── test_main.py      # Test cases
├── .env              # Environment variables (not in repo)
├── .env.example      # Environment template
├── pyproject.toml    # Project dependencies
└── uv.lock           # Lock file
```

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- Neon database account

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Ad1nn/Task_Management_api.git
cd Task_Management_api
```

2. Install dependencies:
```bash
uv sync
```

3. Configure environment variables:
```bash
cp .env.example .env
```

4. Update `.env` with your Neon database connection string:
```env
DATABASE_URL=postgresql://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

## Usage

### Start the server

```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### API Documentation

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tasks` | Create a new task |
| `GET` | `/tasks` | Get all tasks |
| `GET` | `/tasks/{id}` | Get a task by ID |
| `PUT` | `/tasks/{id}` | Update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |

### Query Parameters (GET /tasks)

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status: `pending`, `in_progress`, `completed` |
| `priority` | string | Filter by priority: `low`, `medium`, `high` |
| `skip` | integer | Number of records to skip (default: 0) |
| `limit` | integer | Number of records to return (default: 10, max: 100) |

### Task Schema

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": "Complete the FastAPI tutorial",
  "status": "pending",
  "priority": "high",
  "created_at": "2024-01-12T10:00:00",
  "updated_at": "2024-01-12T10:00:00"
}
```

### Example Requests

**Create a task:**
```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Complete tutorial", "priority": "high"}'
```

**Get all tasks:**
```bash
curl http://127.0.0.1:8000/tasks
```

**Filter tasks by status:**
```bash
curl "http://127.0.0.1:8000/tasks?status=pending"
```

**Update a task:**
```bash
curl -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

**Delete a task:**
```bash
curl -X DELETE http://127.0.0.1:8000/tasks/1
```

## Testing

Run all tests:
```bash
uv run pytest -v
```

Run with coverage:
```bash
uv run pytest --cov=. --cov-report=term-missing
```

### Test Categories

| Category | Tests | Description |
|----------|-------|-------------|
| Health | 2 | Root and health endpoints |
| Create | 7 | Task creation and validation |
| Read | 9 | Get tasks, filtering, pagination |
| Update | 7 | Update fields, validation |
| Delete | 3 | Delete and verify removal |

**Total: 28 tests**

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Neon PostgreSQL connection string | Yes |

## License

MIT
