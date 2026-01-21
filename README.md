# Computer Use Backend

FastAPI backend for Anthropic Computer Use Demo with concurrent sessions and real-time agent execution.

## Quick Start

### Option 1: Local Development (No API Key Required for Demo)

```bash
# 1. Setup virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Configure environment (optional - works without API key)
cp .env.example .env
# For demo: Leave ANTHROPIC_API_KEY as is (uses mock agent)
# For production: Set your real API key

# 4. Start backend
python -m computer_use_backend.main

# 5. Open browser
open http://localhost:8001/
```

**Access:**
- Backend API: http://localhost:8001
- Web UI: http://localhost:8001/
- API Docs: http://localhost:8001/docs

**Note:** Without an API key, the system uses a **Mock Agent** that simulates responses - perfect for demos and testing without costs!

### Option 2: Docker (Recommended for Production)

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 2. Start with Docker
./docker-start.sh
# OR
docker-compose up -d

# 3. Check status
docker-compose ps
```

**Access:**
- Backend API: http://localhost:8000
- Web UI: http://localhost:8000/
- API Docs: http://localhost:8000/docs

**See [DOCKER.md](DOCKER.md) for complete Docker guide.**

### Verify Installation

```bash
# Check backend health
curl http://localhost:8001/health/

# Expected response:
# {"status":"healthy","service":"computer-use-backend"}
```

## Features

- ✅ Concurrent sessions (unlimited)
- ✅ Computer Use Agent integration (reuses original tools)
- ✅ Database persistence (SQLite/PostgreSQL)
- ✅ REST API with auto-docs
- ✅ Worker pool management
- ✅ Web UI at http://localhost:8001/
- ✅ **WebSocket streaming** - Real-time agent updates
- ✅ **VNC Integration** - Remote desktop access (requires Xvfb & x11vnc)
- ✅ **Session deletion** - Clean up sessions with one click
- ✅ **Docker support** - Production-ready containerization

## API Endpoints

Visit http://localhost:8001/docs for interactive API documentation.

**Sessions:**
- `POST /sessions/` - Create session
- `GET /sessions/` - List sessions
- `GET /sessions/{id}` - Get session
- `DELETE /sessions/{id}` - Delete session

**Messages:**
- `POST /sessions/{id}/messages` - Send message (spawns worker)
- `GET /sessions/{id}/messages` - Get history

**Monitoring:**
- `GET /health/` - Health check
- `GET /sessions/workers/health` - Worker status

**WebSocket:**
- `WS /ws/{session_id}/stream` - Real-time agent updates

**VNC:**
- `GET /vnc/{session_id}/info` - Get VNC connection info
- `WS /vnc/{session_id}/stream` - VNC WebSocket proxy

## WebSocket Streaming

Connect to WebSocket for real-time agent execution updates:

```javascript
const ws = new WebSocket(`ws://localhost:8001/ws/${sessionId}/stream`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'agent_update') {
        console.log(`${data.update_type}: ${data.content}`);
    }
};
```

Update types:
- `thinking` - Agent reasoning
- `tool_use` - Tool execution started
- `tool_result` - Tool execution completed
- `error` - Error occurred
- `complete` - Processing finished

## VNC Remote Desktop

Each session has its own VNC server for desktop access:

```bash
# Get VNC info for a session
curl http://localhost:8001/vnc/{session_id}/info

# Connect with VNC client
vncviewer localhost:5901  # Port varies by session
```

**Requirements:**
- `Xvfb` - Virtual framebuffer
- `x11vnc` - VNC server

Install on Ubuntu/Debian:
```bash
sudo apt-get install xvfb x11vnc
```

Install on macOS:
```bash
brew install xquartz
# Note: VNC may have limited functionality on macOS
```

## Example Usage

```bash
# Create session
SESSION_ID=$(curl -s -X POST http://localhost:8001/sessions/ \
  -H "Content-Type: application/json" \
  -d '{}' | jq -r '.session_id')

# Send message
curl -X POST http://localhost:8001/sessions/$SESSION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What is 2+2?", "role": "user"}'

# Check worker status
curl http://localhost:8001/sessions/workers/health | jq

# Get messages
curl http://localhost:8001/sessions/$SESSION_ID/messages | jq
```

## Architecture

```
FastAPI Backend
├── API Layer (routers/)
├── Service Layer (services/)
│   ├── SessionManager
│   ├── WorkerPool
│   └── AgentService (wraps computer_use_demo)
├── Database Layer (SQLAlchemy)
└── Computer Use Agent (from computer_use_demo/)
```

## Configuration

Edit `.env` file:

```bash
# Required
ANTHROPIC_API_KEY=your_key_here

# Optional
PORT=8001
DATABASE_URL=sqlite+aiosqlite:///./computer_use_backend.db
MAX_CONCURRENT_SESSIONS=100
```

## Development

```bash
# Run tests
pytest

# Format code
black . && isort .

# Check types
mypy computer_use_backend/
```

## Project Structure

```
computer_use_backend/       # New FastAPI backend
├── main.py                 # Entry point
├── config.py               # Settings
├── models/                 # Database models
├── routers/                # API endpoints
├── services/               # Business logic
└── static/                 # Web UI

computer_use_demo/          # Original demo (reused)
├── loop.py                 # Agent logic (reused)
└── tools/                  # Tools (reused)
```

## Common Commands

### Start/Stop Backend

```bash
# Start backend (local)
python -m computer_use_backend.main

# Start backend (Docker)
docker-compose up -d backend

# Stop backend (Docker)
docker-compose down

# Restart backend (Docker)
docker-compose restart backend
```

### Check Status

```bash
# Check if backend is running
curl http://localhost:8001/health/

# Check worker status
curl http://localhost:8001/sessions/workers/health | jq

# View backend logs (Docker)
docker-compose logs -f backend

# Check running processes
ps aux | grep "computer_use_backend"
```

### Database

```bash
# Start PostgreSQL (Docker)
docker-compose up -d postgres

# Connect to database
docker-compose exec postgres psql -U postgres -d computer_use_backend

# Reset database (SQLite)
rm computer_use_backend.db
python -m computer_use_backend.main  # Will recreate
```

## Troubleshooting

**Port already in use:**
```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>
```

**Missing API key:**
```bash
# Add to .env file
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -e ".[dev]"
```

**Docker not running:**
```bash
# Start Docker Desktop (macOS/Windows)
# OR start Docker daemon (Linux)
sudo systemctl start docker
```

**Can't access web UI:**
- Check backend is running: `curl http://localhost:8001/health/`
- Check port in `.env` file (default: 8001)
- Try accessing: http://localhost:8001/

## License

See LICENSE file
