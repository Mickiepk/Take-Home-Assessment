# 🚀 How to Start for Demo

## Quick Start Commands:

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Start backend (includes frontend)
python -m computer_use_backend.main

# 3. Open browser
open http://localhost:8001/
```

## What This Does:
- ✅ Starts FastAPI backend on port 8001
- ✅ Serves web UI at http://localhost:8001/
- ✅ Enables API at http://localhost:8001/docs
- ✅ Mock agent ready (no API key needed)

## For Demo Video:

**Show in terminal:**
```bash
source venv/bin/activate
python -m computer_use_backend.main
```

**Then open browser to:**
```
http://localhost:8001/
```

That's it! Everything runs from one command.

## Alternative - Docker:

```bash
docker-compose up -d
open http://localhost:8000/
```

(Note: Docker uses port 8000, local uses 8001)
