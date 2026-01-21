# Computer Use Backend

A scalable FastAPI backend for the Anthropic Computer Use Demo with concurrent session support, real-time streaming, and database persistence.

## Features

- **Scalable Architecture**: FastAPI-based backend with unlimited concurrent sessions
- **Real-time Streaming**: WebSocket support for live agent execution updates
- **Session Management**: Persistent sessions with message history
- **VNC Integration**: Remote desktop access for each session
- **Database Persistence**: PostgreSQL storage for sessions and messages
- **Docker Deployment**: Complete containerized setup
- **Monitoring**: Comprehensive logging and health checks

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Anthropic API key

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd computer-use-backend
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Edit `.env` and add your Anthropic API key:
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

4. Start the services:
```bash
docker compose up -d
```

5. Check the health:
```bash
curl http://localhost:8000/health/
```

### Local Development

1. Install dependencies:
```bash
pip install -e ".[dev]"
```

2. Start PostgreSQL (using Docker):
```bash
docker compose up postgres -d
```

3. Run the application:
```bash
python -m computer_use_backend.main
```

## API Documentation

Once running, visit:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health/

### Key Endpoints

- `POST /sessions` - Create a new session
- `GET /sessions` - List all sessions
- `GET /sessions/{id}/messages` - Get message history
- `POST /sessions/{id}/messages` - Send a message
- `WS /ws/sessions/{id}/stream` - Real-time streaming

## Architecture

The system follows a layered architecture:

1. **API Layer**: FastAPI routers for HTTP and WebSocket endpoints
2. **Service Layer**: Business logic for session and worker management
3. **Database Layer**: PostgreSQL with SQLAlchemy for persistence
4. **Worker Layer**: Isolated processes for agent execution
5. **Infrastructure**: VNC servers and VM instances per session

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black computer_use_backend/
isort computer_use_backend/
```

### Type Checking

```bash
mypy computer_use_backend/
```

## Configuration

See `.env.example` for all available configuration options.

## Status

This is the initial project structure. Core functionality will be implemented in subsequent tasks:

- ✅ Task 1: Project structure and dependencies
- ⏳ Task 2: Database layer and models
- ⏳ Task 3: FastAPI application and endpoints
- ⏳ Task 4: Worker pool and session management
- ⏳ Task 5: WebSocket streaming
- ⏳ Task 6: VNC integration
- ⏳ Task 7: Web frontend
- ⏳ Task 8: Monitoring and logging

## License

[Add your license here]