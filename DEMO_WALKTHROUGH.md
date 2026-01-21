# 🎬 Demo Walkthrough Script (5 Minutes)

## 📝 What to Say & Do

---

## **[0:00-0:45] Introduction & Project Overview**

### **Say:**
> "Hi, this is my Computer Use Backend project - a FastAPI rebuild of Anthropic's Computer Use Demo. The key requirement was unlimited concurrent sessions with real-time streaming. Let me show you the architecture."

### **Do:**
1. Open your IDE showing the project
2. Show folder structure:
   ```
   computer_use_backend/    ← New FastAPI backend
   computer_use_demo/       ← Original agent (reused)
   ```

### **Say:**
> "I built a new FastAPI backend here, and I'm reusing the original Computer Use Agent from here - no code duplication."

### **Show in IDE:**
- `computer_use_backend/routers/` - "API endpoints"
- `computer_use_backend/services/worker.py` - "Worker pool for concurrency"
- `computer_use_demo/loop.py` - "Original agent, imported and reused"

---

## **[0:45-1:15] Start the System**

### **Say:**
> "Let me start the backend. I can use Docker or run it locally."

### **Do - Option 1 (Docker):**
```bash
docker-compose up -d
docker-compose ps
```

### **Do - Option 2 (Local):**
```bash
python -m computer_use_backend.main
```

### **Say:**
> "The system is now running on port 8001. Let me open the web interface."

### **Do:**
- Open browser to `http://localhost:8001/`

---

## **[1:15-2:15] Use Case 1: Single Session**

### **Say:**
> "First, let me create a session and send a message."

### **Do:**
1. Click **"New Session"** button
2. Type: **"What is the weather in Dubai?"**
3. Click **Send**

### **Say:**
> "Notice the real-time updates via WebSocket. The agent is thinking, using tools, and responding - all streamed live."

### **Point out on screen:**
- "Starting to process..." (thinking)
- "Using web search tool" (tool use)
- "Retrieved weather data" (tool result)
- Final response appears

### **Say:**
> "The response is saved to the database, and the worker stays alive for this session."

---

## **[2:15-3:30] Use Case 2: Concurrent Sessions**

### **Say:**
> "Now the key requirement - unlimited concurrent sessions. Let me create a second session while the first one is still active."

### **Do:**
1. Click **"New Session"** again (creates Session 2)
2. In Session 2, type: **"What is 25 times 4?"**
3. Click **Send**
4. Quickly switch back to Session 1
5. Type: **"List files in current directory"**
6. Click **Send**

### **Say:**
> "Both sessions are processing simultaneously with independent workers. No blocking, no waiting."

### **Do:**
- Switch between Session 1 and Session 2 tabs
- Show both have responses

### **Say:**
> "Each session has its own worker and Computer Use Agent instance."

---

## **[3:30-4:15] Show Technical Details**

### **Say:**
> "Let me show you the API and worker pool."

### **Do:**
1. Open new tab: `http://localhost:8001/docs`
2. Scroll through endpoints

### **Say:**
> "Complete REST API with all CRUD operations. Workers spawn automatically when messages are sent."

### **Do:**
3. Open terminal and run:
```bash
curl http://localhost:8001/sessions/workers/health
```

### **Say:**
> "Here you can see the worker pool - multiple workers running concurrently."

### **Show output:**
- Point to `"total_workers": 2`
- Point to each worker's status

---

## **[4:15-4:45] Show Code Integration**

### **Say:**
> "Let me quickly show how I integrated the original agent."

### **Do:**
1. Open `computer_use_backend/services/worker.py` in IDE
2. Scroll to the import section

### **Say:**
> "Here I import the original agent service. No reimplementation - just wrapping and reusing."

### **Show:**
```python
from .agent_service import AgentService
from .mock_agent_service import MockAgentService
```

### **Say:**
> "I also created a mock agent for demos without API costs."

---

## **[4:45-5:00] Wrap Up**

### **Say:**
> "To summarize: I've built a production-ready FastAPI backend with unlimited concurrent sessions, real-time WebSocket streaming, full Computer Use Agent integration, and Docker deployment."

### **Do:**
1. Go back to web UI
2. Click delete button on one session
3. Show it disappears

### **Say:**
> "Sessions can be cleaned up easily, terminating workers and freeing resources. Everything is persistent in the database, and the system is ready for production deployment. Thank you!"

---

## 🎯 Key Points to Hit

Make sure you mention these:

1. ✅ **"Unlimited concurrent sessions"** - Say this explicitly
2. ✅ **"Real-time WebSocket streaming"** - Point it out
3. ✅ **"Reuses original Computer Use Agent"** - Show the import
4. ✅ **"Independent workers per session"** - Show worker health
5. ✅ **"No blocking between sessions"** - Demonstrate with 2 sessions
6. ✅ **"Database persistence"** - Mention it
7. ✅ **"Docker ready"** - Show docker-compose.yml or use it

---

## 📋 Pre-Recording Checklist

Before you start recording:

- [ ] Backend is running (local or Docker)
- [ ] Browser open to http://localhost:8001/
- [ ] API docs tab ready at http://localhost:8001/docs
- [ ] Terminal ready with curl command
- [ ] IDE open showing project structure
- [ ] Close unnecessary apps/tabs
- [ ] Test your microphone
- [ ] Practice once without recording

---

## 💡 Tips

### If Something Goes Wrong:
- **Pause and restart** - It's okay to edit the video
- **Have backup plan** - If one session fails, continue with others
- **Stay calm** - Explain what you're doing

### Speaking:
- **Speak clearly** - Not too fast
- **Be confident** - You built this!
- **Show enthusiasm** - You're proud of your work

### Timing:
- **Don't rush** - 5 minutes is plenty
- **Pause between sections** - Let things load
- **Skip if needed** - If running long, skip the code walkthrough

---

## 🎥 Recording Setup

### Screen:
- Close extra windows
- Increase font size (terminal & IDE)
- Use clean browser profile
- Full screen or large window

### Audio:
- Test microphone first
- Quiet environment
- Speak at normal volume
- Close to microphone

### Recording Software:
- **macOS:** QuickTime, OBS, or Loom
- **Windows:** OBS, Xbox Game Bar, or Loom
- **Linux:** OBS or SimpleScreenRecorder

---

## 📊 Timing Breakdown

| Time | Section | What to Show |
|------|---------|--------------|
| 0:00-0:45 | Intro | Project structure, architecture |
| 0:45-1:15 | Startup | Start backend, open UI |
| 1:15-2:15 | Use Case 1 | Single session, send message |
| 2:15-3:30 | Use Case 2 | Concurrent sessions |
| 3:30-4:15 | Technical | API docs, worker health |
| 4:15-4:45 | Code | Show agent integration |
| 4:45-5:00 | Wrap up | Delete session, summary |

---

## 🎬 Alternative: Shorter Version (3-4 min)

If you want to keep it shorter:

1. **Skip:** Code walkthrough (save 30 sec)
2. **Combine:** Use cases 1 & 2 (save 30 sec)
3. **Faster:** Startup and intro (save 30 sec)

---

## ✅ After Recording

1. **Watch it once** - Check audio and video quality
2. **Trim if needed** - Remove dead air at start/end
3. **Add title slide** (optional) - Project name at start
4. **Export** - MP4 format, 1080p if possible
5. **Upload** - YouTube (unlisted) or file sharing

---

**You're ready! Good luck with your demo! 🚀**
