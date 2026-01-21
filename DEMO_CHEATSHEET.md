# 🎯 Demo Cheat Sheet - Quick Reference

## 📝 What to Say (Key Phrases)

1. **"Unlimited concurrent sessions with independent workers"**
2. **"Real-time WebSocket streaming"**
3. **"Reuses original Computer Use Agent - no code duplication"**
4. **"Production-ready with Docker deployment"**
5. **"Database persistence for all sessions and messages"**

---

## 🎬 Actions in Order

### 1. Show Project (30 sec)
- Open IDE
- Show `computer_use_backend/` and `computer_use_demo/`
- Say: "New backend, reused agent"

### 2. Start Backend (30 sec)
```bash
python -m computer_use_backend.main
# OR
docker-compose up -d
```
- Open: http://localhost:8001/

### 3. First Session (1 min)
- Click "New Session"
- Type: "What is the weather in Dubai?"
- Send
- Point out real-time updates

### 4. Concurrent Sessions (1.5 min)
- Click "New Session" again
- Type: "What is 25 times 4?"
- Send
- Switch to Session 1
- Type: "List files in current directory"
- Send
- Switch between both - show both working

### 5. Show API (1 min)
- Open: http://localhost:8001/docs
- Scroll through endpoints
- Terminal:
```bash
curl http://localhost:8001/sessions/workers/health
```
- Point to worker count

### 6. Show Code (30 sec)
- Open `computer_use_backend/services/worker.py`
- Show imports from original agent

### 7. Wrap Up (30 sec)
- Delete a session
- Say summary
- Done!

---

## 🔗 URLs to Have Ready

- Web UI: http://localhost:8001/
- API Docs: http://localhost:8001/docs
- Health: http://localhost:8001/health/

---

## 💬 Test Messages

Use these for demo:
1. "What is the weather in Dubai?"
2. "What is 25 times 4?"
3. "List files in current directory"
4. "What is 2+2?"

---

## ⚡ Quick Commands

```bash
# Start backend
python -m computer_use_backend.main

# Check health
curl http://localhost:8001/health/

# Check workers
curl http://localhost:8001/sessions/workers/health

# Docker
docker-compose up -d
docker-compose ps
```

---

## ✅ Must Show

- [ ] Multiple sessions running at same time
- [ ] Real-time WebSocket updates
- [ ] Worker pool with multiple workers
- [ ] API documentation
- [ ] Code showing agent reuse
- [ ] Delete session functionality

---

## 🎯 Time Check

- 0:00 - Start intro
- 1:00 - Should be showing first session
- 2:30 - Should be showing concurrent sessions
- 4:00 - Should be wrapping up
- 5:00 - Done!

---

## 🆘 If Something Breaks

- **Pause recording** - It's okay!
- **Restart backend** if needed
- **Skip to next part** if one thing fails
- **Stay calm** - Explain what you're doing

---

**Print this and keep it next to you while recording!**
