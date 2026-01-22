# 🎬 Simple Demo Script (5 Minutes)

## **What to Say and Do**

---

### **1. Introduction (30 sec)**

**Show:** IDE with project folders

**Say:**
> "This is my Computer Use Backend - a FastAPI rebuild that supports unlimited concurrent sessions with real-time streaming."

**Point to folders:**
- `computer_use_backend/` - "My new backend"
- `computer_use_demo/` - "Original agent I'm reusing"

---

### **2. Start System (30 sec)**

**Terminal:**
```bash
source venv/bin/activate
python -m computer_use_backend.main
```

**Say:**
> "Starting the backend. It runs on port 8001."

**Open browser:** http://localhost:8001/

---

### **3. First Session (1 min)**

**Say:**
> "Let me create a session and send a message."

**Do:**
1. Click **"New Session"**
2. Type: **"What is the weather in Dubai?"**
3. Click **Send**

**Say:**
> "See the real-time updates via WebSocket. The agent processes and responds."

**Wait for response:** "The weather in Dubai is currently sunny..."

---

### **4. Concurrent Sessions (1.5 min)**

**Say:**
> "Now the key feature - concurrent sessions. Let me create another one."

**Do:**
1. Click **"New Session"** (Session 2)
2. Type: **"What is 5 + 3?"**
3. Click **Send**
4. Switch to Session 1
5. Type: **"What is 10 times 5?"**
6. Click **Send**

**Say:**
> "Both sessions process simultaneously with independent workers."

**Switch between tabs** - show both have responses

---

### **5. Show API & Workers (1 min)**

**Say:**
> "Here's the API documentation."

**Open:** http://localhost:8001/docs

**Scroll through endpoints**

**Say:**
> "Complete REST API. Let me check the worker pool."

**Terminal:**
```bash
curl http://localhost:8001/sessions/workers/health
```

**Say:**
> "Two workers running concurrently."

---

### **6. Show Code (30 sec)**

**IDE - Open:** `computer_use_backend/services/worker.py`

**Say:**
> "Here's my worker pool managing concurrent sessions."

**IDE - Open:** `computer_use_backend/services/agent_service.py`

**Point to:**
```python
from computer_use_demo.loop import sampling_loop
```

**Say:**
> "I'm importing and reusing the original agent - no code duplication."

---

### **7. Wrap Up (30 sec)**

**Say:**
> "To summarize: FastAPI backend, unlimited concurrent sessions, real-time WebSocket streaming, reuses original agent, Docker ready."

**Browser - Delete a session**

**Say:**
> "Sessions clean up easily. Everything persists in the database. Thank you!"

---

## ✅ **Quick Reference**

**Questions:**
1. "What is the weather in Dubai?" (requirement)
2. "What is 5 + 3?"
3. "What is 10 times 5?"
4. "Hello!"

**Commands:**
```bash
source venv/bin/activate
python -m computer_use_backend.main
curl http://localhost:8001/sessions/workers/health
```

**URLs:**
- Web UI: http://localhost:8001/
- API Docs: http://localhost:8001/docs

---

**Keep it simple, show it works, emphasize concurrency!** 🚀
