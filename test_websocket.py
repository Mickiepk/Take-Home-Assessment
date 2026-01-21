#!/usr/bin/env python3
"""
Simple WebSocket test client to verify real-time streaming.
"""

import asyncio
import json
import sys
import httpx
import websockets


async def test_websocket_streaming():
    """Test WebSocket streaming with a real session."""
    base_url = "http://localhost:8001"
    
    print("🚀 Testing WebSocket Streaming\n")
    
    # Step 1: Create a session
    print("1. Creating session...")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{base_url}/sessions/", json={})
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"   ✅ Session created: {session_id}\n")
    
    # Step 2: Connect to WebSocket
    print("2. Connecting to WebSocket...")
    ws_url = f"ws://localhost:8001/ws/{session_id}/stream"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"   ✅ Connected to {ws_url}\n")
            
            # Step 3: Send a message via REST API
            print("3. Sending message via REST API...")
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{base_url}/sessions/{session_id}/messages",
                    json={"content": "What is 2+2?", "role": "user"}
                )
                print("   ✅ Message sent\n")
            
            # Step 4: Receive real-time updates via WebSocket
            print("4. Receiving real-time updates:\n")
            print("-" * 60)
            
            update_count = 0
            timeout = 30  # 30 seconds timeout
            
            try:
                async with asyncio.timeout(timeout):
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        update_count += 1
                        
                        if data.get("type") == "connected":
                            print(f"   🔗 {data.get('message')}")
                            continue
                        
                        if data.get("type") == "agent_update":
                            update_type = data.get("update_type", "unknown")
                            content = data.get("content", "")
                            
                            # Format output based on update type
                            if update_type == "thinking":
                                print(f"   💭 {content}")
                            elif update_type == "tool_use":
                                tool_name = data.get("metadata", {}).get("tool_name", "unknown")
                                print(f"   🔧 Using tool: {tool_name}")
                            elif update_type == "tool_result":
                                print(f"   ✅ {content}")
                            elif update_type == "error":
                                print(f"   ❌ {content}")
                            elif update_type == "complete":
                                print(f"   ✨ {content}")
                                print("-" * 60)
                                print(f"\n✅ Test completed! Received {update_count} updates")
                                break
                        
            except asyncio.TimeoutError:
                print(f"\n⏱️  Timeout after {timeout} seconds")
                print(f"   Received {update_count} updates before timeout")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_websocket_streaming())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
