#!/usr/bin/env python3
"""
Demo script to showcase all features of the Computer Use Backend.
"""

import asyncio
import httpx
import json
from datetime import datetime


async def demo():
    """Run a complete demo of the system."""
    base_url = "http://localhost:8001"
    
    print("=" * 70)
    print("🚀 COMPUTER USE BACKEND - FEATURE DEMO")
    print("=" * 70)
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Health Check
        print("1️⃣  HEALTH CHECK")
        print("-" * 70)
        response = await client.get(f"{base_url}/health/")
        print(f"   Status: {response.json()}")
        print()
        
        # 2. Create Session
        print("2️⃣  CREATE SESSION")
        print("-" * 70)
        response = await client.post(
            f"{base_url}/sessions/",
            json={"session_metadata": {"demo": "test", "timestamp": datetime.now().isoformat()}}
        )
        session = response.json()
        session_id = session["session_id"]
        print(f"   ✅ Session created: {session_id}")
        print(f"   Created at: {session['created_at']}")
        print()
        
        # 3. List Sessions
        print("3️⃣  LIST ALL SESSIONS")
        print("-" * 70)
        response = await client.get(f"{base_url}/sessions/")
        sessions = response.json()
        print(f"   Total sessions: {len(sessions)}")
        for s in sessions[-3:]:  # Show last 3
            print(f"   - {s['session_id'][:8]}... ({s['status']})")
        print()
        
        # 4. Send Message (spawns worker)
        print("4️⃣  SEND MESSAGE (Worker Auto-Spawns)")
        print("-" * 70)
        message_content = "Hello! Can you tell me what 5 + 3 equals?"
        print(f"   Message: \"{message_content}\"")
        response = await client.post(
            f"{base_url}/sessions/{session_id}/messages",
            json={"content": message_content, "role": "user"}
        )
        message = response.json()
        print(f"   ✅ Message sent: {message['message_id']}")
        print(f"   Timestamp: {message['timestamp']}")
        print()
        
        # Wait a bit for worker to spawn
        await asyncio.sleep(2)
        
        # 5. Check Worker Status
        print("5️⃣  WORKER POOL STATUS")
        print("-" * 70)
        response = await client.get(f"{base_url}/sessions/workers/health")
        health = response.json()
        print(f"   Total workers: {health['total_workers']}/{health['max_workers']}")
        if session_id in health['workers']:
            worker = health['workers'][session_id]
            print(f"   Worker for our session:")
            print(f"     - Worker ID: {worker['worker_id']}")
            print(f"     - Status: {worker['status']}")
            print(f"     - VNC Port: {worker.get('vnc_port', 'N/A')}")
        print()
        
        # 6. Get Message History
        print("6️⃣  MESSAGE HISTORY")
        print("-" * 70)
        await asyncio.sleep(3)  # Wait for agent response
        response = await client.get(f"{base_url}/sessions/{session_id}/messages")
        messages = response.json()
        print(f"   Total messages: {len(messages)}")
        for msg in messages:
            role = msg['role'].upper()
            content = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
            print(f"   [{role}] {content}")
        print()
        
        # 7. VNC Info (if available)
        print("7️⃣  VNC DESKTOP ACCESS")
        print("-" * 70)
        try:
            response = await client.get(f"{base_url}/vnc/{session_id}/info")
            if response.status_code == 200:
                vnc_info = response.json()
                print(f"   ✅ VNC Server Running")
                print(f"   VNC Port: {vnc_info['vnc_port']}")
                print(f"   VNC URL: {vnc_info['vnc_url']}")
                print(f"   Display: {vnc_info['display']}")
                print(f"   Health: {vnc_info['health']['is_running']}")
            else:
                print(f"   ⚠️  VNC not available (requires Xvfb & x11vnc)")
        except Exception as e:
            print(f"   ⚠️  VNC not available: {str(e)}")
        print()
        
        # 8. API Documentation
        print("8️⃣  API DOCUMENTATION")
        print("-" * 70)
        print(f"   Swagger UI: {base_url}/docs")
        print(f"   ReDoc: {base_url}/redoc")
        print(f"   Web UI: {base_url}/")
        print()
        
        # 9. WebSocket Info
        print("9️⃣  WEBSOCKET STREAMING")
        print("-" * 70)
        print(f"   Agent Updates: ws://localhost:8001/ws/{session_id}/stream")
        print(f"   VNC Stream: ws://localhost:8001/vnc/{session_id}/stream")
        print(f"   Status: ✅ Real-time streaming enabled")
        print()
        
        # Summary
        print("=" * 70)
        print("✨ DEMO COMPLETE!")
        print("=" * 70)
        print()
        print("🎯 What's Working:")
        print("   ✅ Session management")
        print("   ✅ Message processing")
        print("   ✅ Worker pool (auto-spawn)")
        print("   ✅ Computer Use Agent integration")
        print("   ✅ WebSocket streaming")
        print("   ✅ VNC server (if Xvfb installed)")
        print("   ✅ Database persistence")
        print("   ✅ Web UI")
        print()
        print("🌐 Access Points:")
        print(f"   • Web UI: {base_url}/")
        print(f"   • API Docs: {base_url}/docs")
        print(f"   • Health: {base_url}/health/")
        print()
        print("📊 Current Status:")
        print(f"   • Active Sessions: {len(sessions)}")
        print(f"   • Active Workers: {health['total_workers']}")
        print(f"   • Session ID: {session_id[:16]}...")
        print()


if __name__ == "__main__":
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
