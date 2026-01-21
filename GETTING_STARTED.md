# 🚀 Getting Started

Complete guide to get Computer Use Backend up and running in 5 minutes.

---

## ⚡ Quick Start (Choose One)

### Option A: Local Development (Fastest)

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# 2. Configure
cp .env.example .env
# Edit .env: Set ANTHROPIC_API_KEY=your_key_here

# 3. Run
python -m computer_use_backend.main

# 4. Open browser
open http://localhost:8001/
```

### Option B: Docker (Production-like)

```bash
# 1. Configure
cp .env.example .env
# Edit .env: Set ANTHROPIC_API_KEY=your_key_here

# 2. Run
./docker-start.sh

# 3. Open browser
open http://localhost:8000/
```

---

## 📋 Prerequisites

### For Local Development:
- Python 3.11+
- pip
- Anthropic API key

### For Docker:
- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- Docker Compose v2.0+
- Anthropic API key

### For VNC (Optional):
- Xvfb: `sudo apt-get install xvfb` (Linux)
- x11vnc: `sudo apt-get install x11vnc` (Linux)

---

## 🔑 Get API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy the key (starts with `sk-ant-`)

---

## 📝 Configuration

### 1. Create .env file

```bash
cp .env.example .env
```

### 2. Edit .env

**Required:**
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

**Optional (defaults are fine):**
```bash
PORT=8001
DATABASE_URL=sqlite+aiosqlite:///./computer_use_backend.db
MAX_CONCURRENT_SESSIONS=100
LOG_LEVEL=INFO
```

---

## 🎯 First Steps

### 1. Start the Backend

**Local:**
```bash
python -m computer_use_backend.main
```

**Docker:**
```bash
docker-compose up -d
```

### 2. Verify It's Running

```bash
curl http://localhost:8001/health/
# Should return: {"status":"healthy","service":"computer-use-backend"}
```

### 3. Open Web UI

```
http://localhost:8001/
```

### 4. Create Your First Session

1. Click "New Session" button
2. Type a message: "What is 2+2?"
3. Watch the agent respond in real-time!

---

## 🧪 Test Everything

### Run Demo Script

```bash
python demo.py
```

This will:
- Create a session
- Send a message
- Show worker status
- Display message history
- Show all endpoints

### Test WebSocket

```bash
python test_websocket.py
```

### Test API

```bash
# Create session
curl -X POST http://localhost:8001/sessions/ \
  -H "Content-Type: application/json" \
  -d '{}'

# List sessions
curl http://localhost:8001/sessions/

# Check health
curl http://localhost:8001/health/
```

---

## 📚 Explore Features

### Web UI
- **URL:** http://localhost:8001/
- Create/delete sessions
- Send messages
- View real-time updates
- Monitor worker status

### API Documentation
- **Swagger:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc
- Interactive testing
- Complete endpoint docs

### WebSocket Streaming
- Real-time agent updates
- Tool execution streaming
- Multiple clients support

### VNC Desktop (if installed)
- Remote desktop per session
- View agent's screen
- Debug visually

---

## 🛠️ Common Tasks

### View Logs

**Local:**
```bash
# Logs are printed to console
```

**Docker:**
```bash
docker-compose logs -f backend
```

### Stop Services

**Local:**
```bash
# Press Ctrl+C
```

**Docker:**
```bash
docker-compose down
```

### Restart

**Local:**
```bash
# Stop (Ctrl+C) and run again
python -m computer_use_backend.main
```

**Docker:**
```bash
docker-compose restart backend
```

### Check Status

```bash
# Health check
curl http://localhost:8001/health/

# Worker status
curl http://localhost:8001/sessions/workers/health

# Docker status
docker-compose ps
```

---

## 🐛 Troubleshooting

### "Port already in use"

**Solution:**
```bash
# Find process using port
lsof -i :8001

# Kill it
kill -9 <PID>

# Or change port in .env
PORT=8002
```

### "Invalid API key"

**Solution:**
1. Check .env file has correct key
2. Key should start with `sk-ant-`
3. No quotes around the key
4. No extra spaces

### "Module not found"

**Solution:**
```bash
# Reinstall dependencies
pip install -e ".[dev]"
```

### "Database error"

**Solution:**
```bash
# Delete and recreate database
rm computer_use_backend.db
python -m computer_use_backend.main
```

### "Docker build failed"

**Solution:**
```bash
# Clean build
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## 📖 Next Steps

### Learn More
- Read [README.md](README.md) for overview
- Check [FEATURES.md](FEATURES.md) for features
- See [DOCKER.md](DOCKER.md) for Docker details
- Review [DEMO_GUIDE.md](DEMO_GUIDE.md) for testing

### Try Features
1. Create multiple sessions (test concurrency)
2. Send complex messages to agent
3. Watch real-time WebSocket updates
4. Delete old sessions
5. Check worker health
6. Explore API docs

### Customize
- Adjust worker limits in .env
- Change port numbers
- Configure CORS origins
- Set up PostgreSQL
- Enable VNC

### Deploy
- Use docker-compose.prod.yml
- Set up SSL/TLS
- Configure monitoring
- Set up backups
- Scale horizontally

---

## 💡 Tips

1. **Start Simple**
   - Use local development first
   - Test with simple messages
   - Explore the Web UI

2. **Use API Docs**
   - Interactive testing at /docs
   - Try all endpoints
   - See request/response formats

3. **Monitor Logs**
   - Watch for errors
   - Check worker status
   - Verify API calls

4. **Test Concurrency**
   - Create multiple sessions
   - Send messages simultaneously
   - Verify independence

5. **Clean Up**
   - Delete old sessions
   - Monitor resource usage
   - Restart if needed

---

## 🎓 Learning Path

### Day 1: Basics
- [ ] Install and configure
- [ ] Start backend
- [ ] Create first session
- [ ] Send first message
- [ ] Explore Web UI

### Day 2: Features
- [ ] Test WebSocket streaming
- [ ] Try multiple sessions
- [ ] Use API documentation
- [ ] Check worker health
- [ ] Delete sessions

### Day 3: Advanced
- [ ] Set up Docker
- [ ] Configure PostgreSQL
- [ ] Enable VNC
- [ ] Test concurrency
- [ ] Monitor performance

### Day 4: Production
- [ ] Use production config
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test scaling
- [ ] Deploy

---

## 🆘 Get Help

### Documentation
- README.md - Main guide
- DOCKER.md - Docker guide
- FEATURES.md - Feature list
- DEMO_GUIDE.md - Testing guide

### Testing
- `python demo.py` - Full demo
- `python test_websocket.py` - WebSocket test
- `python test_delete.py` - Delete test

### Debugging
- Check logs for errors
- Verify .env configuration
- Test with curl commands
- Use API docs for testing

---

## ✅ Checklist

Before you start:
- [ ] Python 3.11+ installed (for local)
- [ ] Docker installed (for Docker)
- [ ] Anthropic API key obtained
- [ ] .env file configured
- [ ] Port 8001 (or 8000) available

After starting:
- [ ] Health check passes
- [ ] Web UI loads
- [ ] Can create session
- [ ] Can send message
- [ ] Agent responds

---

**Ready to start? Pick an option above and follow the steps!**

**Need help? Check the troubleshooting section or documentation.**

**Happy coding! 🚀**
