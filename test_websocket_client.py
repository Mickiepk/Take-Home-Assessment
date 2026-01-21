#!/usr/bin/env python3
"""
Simple WebSocket client to test real-time streaming.
"""

import asyncio
import json
import sys
from datetime import datetime

try:
    import websockets
    import httpx
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets", "httpx"])
    import websockets
    import httpx


BASE_URL = "http://localhost:8001"
WS_URL = "ws://localhost:8001"


async def test_websocket_streaming():
    """Test WebSocket streaming with a real session."""
    
    print("=" * 60)
    print("WebSocket Streaming Test")
    print("=" * 60)
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Step 1: Create a session
        print("\n1. Creating session...")
        response = await client.post(
            f"{BASE_URL}/sessions/",
            json={"session_metadata": {"test": "websocket_streaming"}}
        )
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"   ✓ Session created: {session_id}")
        
        # Step 2: Connect to WebSocket
        print(f"\n2. Connecting to WebSocket...")
        ws_url = f"{WS_URL}/ws/sessions/{session_id}/stream"
        
        async with websockets.connect(ws_url) as websocket:
            print(f"   ✓ WebSocket connected")
            
            # Receive connection confirmation
            message = await websocket.recv()
            data = json.loads(message)
            print(f"   ✓ Connection confirmed: {data.get('status')}")
            
            # Step 3: Send a message via REST API (in background)
            print(f"\n3. Sending message to session...")
            
            async def send_message():
                await asyncio.sleep(1)  # Give WebSocket time to be ready
                response = await client.post(
                    f"{BASE_URL}/sessions/{session_id}/messages",
                    json={
                        "role": "user",
                        "content": "Hello! Can you tell me what 2+2 equals?",
                        "message_metadata": {}
                    }
                )
                response.raise_for_status()
                print(f"   ✓ Message sent")
            
            # Start sending message in background
            send_task = asyncio.create_task(send_message())
            
            # Step 4: Receive streaming updates
            print(f"\n4. Receiving real-time updates...")
            print("-" * 60)
            
            update_count = 0
            timeout = 30  # 30 seconds timeout
            start_time = asyncio.get_event_loop().time()
            
            try:
                while True:
                    # Check timeout
                    if asyncio.get_event_loop().time() - start_time > timeout:
                        print("\n   ⚠ Timeout reached")
                        break
                    
                    try:
                        # Wait for message with timeout
                        message = await asyncio.wait_for(
                            websocket.recv(),
                            timeout=2.0
                        )
                        
                        data = json.loads(message)
                        update_count += 1
                        
                        # Display update
                        update_type = data.get("type", "unknown")
                        timestamp = data.get("timestamp", "")
                        
                        if update_type == "update":
                            content = data.get("content", "")
                            metadata = data.get("metadata", {})
                            print(f"\n[{update_count}] {timestamp}")
                            print(f"    Type: {metadata.get('update_type', 'unknown')}")
                            print(f"    Content: {content[:100]}...")
                            
                        elif update_type == "status":
                            status = data.get("status", "")
                            message_text = data.get("message", "")
                            print(f"\n[{update_count}] STATUS: {status}")
                            print(f"    {message_text}")
                            
                            # Stop if complete
                            if status == "complete":
                                print("\n   ✓ Processing completed!")
                                break
                        
                        elif update_type == "error":
                            error = data.get("error", "")
                            print(f"\n[{update_count}] ERROR: {error}")
                            break
                        
                        else:
                            print(f"\n[{update_count}] {update_type}: {data}")
                    
                    except asyncio.TimeoutError:
                        # No message received, continue waiting
                        continue
                    
            except websockets.exceptions.ConnectionClosed:
                print("\n   ⚠ WebSocket connection closed")
            
            # Wait for send task to complete
            await send_task
            
            print("-" * 60)
            print(f"\n5. Summary:")
            print(f"   Total updates received: {update_count}")
            
        # Step 6: Get message history
        print(f"\n6. Fetching message history...")
        response = await client.get(f"{BASE_URL}/sessions/{session_id}/messages")
        response.raise_for_status()
        messages = response.json()
        print(f"   ✓ Messages in history: {len(messages)}")
        for msg in messages:
            print(f"     - {msg['role']}: {msg['content'][:50]}...")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_websocket_streaming())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
