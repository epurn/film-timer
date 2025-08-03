# Interval Timer API

A FastAPI-based interval timer application with PostgreSQL database and Docker deployment.

## Features

- **Fully Customizable Timers**: Create timers with custom steps, durations, repetitions, and notes
- **Import/Export**: Export timers to CSV format and import from CSV files
- **RESTful API**: Clean, versioned API endpoints with automatic documentation
- **Database Migrations**: Alembic-based database schema management
- **Comprehensive Testing**: Unit and integration tests with pytest
- **Docker Deployment**: Complete containerized setup with docker-compose

## Project Structure

```
Film Timer/
├── i_timer/                    # Python backend application
│   ├── app/
│   │   ├── core/              # Core configuration and database
│   │   ├── models/            # SQLAlchemy database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # FastAPI route handlers
│   │   ├── services/          # Business logic services
│   │   └── main.py           # FastAPI application
│   ├── tests/                 # Test suite
│   │   ├── unit/             # Unit tests
│   │   └── integration/      # Integration tests
│   ├── alembic/              # Database migrations
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Backend container
├── deployment/               # Docker deployment files
│   ├── docker-compose.yml   # Multi-container setup
│   └── postgres/            # Database initialization
└── .env.example             # Environment variables template
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd "Film Timer"
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Start the application:**
   ```bash
   cd deployment
   docker-compose up --build
   ```

4. **Access the application:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Development Setup

1. **Install Python dependencies:**
   ```bash
   cd i_timer
   pip install -r requirements.txt
   ```

2. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

3. **Run tests:**
   ```bash
   pytest
   ```

4. **Start development server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Timers
- `GET /api/v1/timers/` - List all timers
- `POST /api/v1/timers/` - Create a new timer
- `GET /api/v1/timers/{id}` - Get specific timer
- `PUT /api/v1/timers/{id}` - Update timer
- `DELETE /api/v1/timers/{id}` - Delete timer
- `POST /api/v1/timers/{id}/steps` - Add step to timer
- `DELETE /api/v1/timers/{id}/steps/{step_id}` - Delete timer step

### Import/Export
- `GET /api/v1/import-export/timers/{id}/export` - Export timer to CSV
- `POST /api/v1/import-export/timers/import` - Import timer from CSV

## Timer Structure

Each timer consists of:
- **Name**: Timer title
- **Description**: Optional description
- **Steps**: Ordered list of intervals with:
  - Title: Step name
  - Duration: Length in seconds
  - Repetitions: Number of times to repeat (default: 1)
  - Notes: Optional notes

## CSV Format

Export/import uses this CSV structure:
```csv
timer_name,timer_description,step_order,step_title,duration_seconds,repetitions,notes
Workout Timer,My workout routine,0,Warm up,300,1,Light cardio
Workout Timer,My workout routine,1,Work,1200,3,High intensity
```

## Environment Variables

Key configuration options in `.env`:

```bash
# Database
POSTGRES_DB=timer_db
POSTGRES_USER=timer_user
POSTGRES_PASSWORD=timer_pass

# Application
DEBUG=false
APP_NAME=Interval Timer API

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://frontend:3000
```

## Testing

Run the test suite:

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov=app
```

## Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Development

### Code Style
- Black for formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

### Architecture
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy 2.0**: Async ORM with declarative models
- **Pydantic**: Data validation and serialization
- **Alembic**: Database schema migrations
- **PostgreSQL**: Primary database
- **Docker**: Containerized deployment

## Future Enhancements

- Frontend web application (React/Vue.js)
- Real-time timer execution with WebSockets
- User authentication and multi-tenancy
- Timer sharing and community features
- Mobile application
- Audio cues and notifications