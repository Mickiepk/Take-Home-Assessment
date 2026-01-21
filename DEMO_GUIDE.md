# How to See the Results

## 🌐 Option 1: Web UI (Easiest)

**Open in your browser:**
```
http://localhost:8001/
```

**What you'll see:**
- Session sidebar (create/select sessions)
- Chat interface (send messages)
- Real-time updates (WebSocket streaming)
- Worker status indicator

**Try it:**
1. Click "New Session"
2. Type a message: "What is 2+2?"
3. Watch real-time updates appear
4. See the agent's response

---

## 📚 Option 2: API Documentation (Interactive)

**Swagger UI:**
```
http://localhost:8001/docs
```

**What you can do:**
- See all API endpoints
- Try them out interactively
- View request/response schemas
- Test with real data

**Try it:**
1. Open `/docs`
2. Expand "POST /sessions/"
3. Click "Try it out"
4. Click "Execute"
5. See the response

---

## 🖥️ Option 3: Command Line (Quick Tests)

### Create a session:
```bash
curl -X POST http://localhost:8001/sessions/ \
  -H "Content-Type: application/json" \
  -d '{}' | python -m json.tool
```

### Send a message:
```bash
SESSION_ID="your-session-id-here"
curl -X POST http://localhost:8001/sessions/$SESSION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello!", "role": "user"}' | python -m json.tool
```

### Check worker status:
```bash
curl http://localhost:8001/sessions/workers/health | python -m json.tool
```

### Get message history:
```bash
curl http://localhost:8001/sessions/$SESSION_ID/messages | python -m json.tool
```

---

## 🎬 Option 4: Demo Script (Automated)

**Run the demo:**
```bash
python demo.py
```

**What it shows:**
- Health check
- Session creation
- Message sending
- Worker spawning
- Message history
- VNC info
- All endpoints

---

## 🧪 Option 5: WebSocket Test (Real-time)

**Run WebSocket test:**
```bash
python test_websocket.py
```

**What you'll see:**
- WebSocket connection
- Real-time agent updates
- Tool execution
- Completion status

---

## 🖼️ Option 6: VNC Desktop (If Installed)

**Check VNC info:**
```bash
SESSION_ID="your-session-id-here"
curl http://localhost:8001/vnc/$SESSION_ID/info | python -m json.tool
```

**Connect with VNC client:**
```bash
# Get the VNC port from the info above
vncviewer localhost:5901
```

**Requirements:**
- Xvfb (virtual display)
- x11vnc (VNC server)

Install on Ubuntu/Debian:
```bash
sudo apt-get install xvfb x11vnc
```

---

## 📊 Current Status Check

**Quick status:**
```bash
# Health
curl http://localhost:8001/health/

# Sessions
curl http://localhost:8001/sessions/ | python -m json.tool

# Workers
curl http://localhost:8001/sessions/workers/health | python -m json.tool
```

---

## 🎯 What's Working Right Now

✅ **Session Management**
- Create, list, get, delete sessions
- Persistent storage

✅ **Message Processing**
- Send messages
- Auto-spawn workers
- Computer Use Agent integration

✅ **Real-time Streaming**
- WebSocket connections
- Live agent updates
- Tool execution streaming

✅ **Worker Pool**
- Concurrent workers
- Auto-initialization
- Health monitoring

✅ **VNC Integration**
- VNC server per session
- Remote desktop access
- (Requires Xvfb & x11vnc)

✅ **Web UI**
- Session management
- Chat interface
- Real-time updates

---

## 🚀 Quick Start

**1. Start backend:**
```bash
python -m computer_use_backend.main
```

**2. Open browser:**
```
http://localhost:8001/
```

**3. Create session and chat!**

---

## 📈 Progress: 90% Complete!

**Completed:**
- ✅ Session management
- ✅ Message processing
- ✅ Worker pool
- ✅ Computer Use Agent
- ✅ WebSocket streaming
- ✅ VNC integration
- ✅ Web UI
- ✅ Database persistence

**Remaining:**
- ⏳ Complete Docker setup
- ⏳ Property-based tests
- ⏳ Integration tests
- ⏳ VM isolation (optional)

---

## 🆘 Troubleshooting

**Backend not responding?**
```bash
# Check if running
curl http://localhost:8001/health/

# Check port
lsof -i :8001

# Restart
python -m computer_use_backend.main
```

**No workers spawning?**
- Check ANTHROPIC_API_KEY in .env
- Check logs for errors
- Verify dependencies installed

**VNC not working?**
- Install Xvfb: `sudo apt-get install xvfb x11vnc`
- Check VNC info endpoint
- VNC may not work on macOS

---

## 📞 Need Help?

Check the logs:
```bash
# Backend logs show everything
# Look for errors or warnings
```

Check the docs:
```
http://localhost:8001/docs
```

Read the README:
```bash
cat README.md
```
