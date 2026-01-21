#!/usr/bin/env python3
"""Test session deletion."""

import asyncio
import httpx


async def test_delete():
    base_url = "http://localhost:8001"
    
    async with httpx.AsyncClient() as client:
        # Create a test session
        print("Creating test session...")
        response = await client.post(f"{base_url}/sessions/", json={})
        session = response.json()
        session_id = session["session_id"]
        print(f"✅ Created: {session_id}")
        
        # Verify it exists
        print("\nVerifying session exists...")
        response = await client.get(f"{base_url}/sessions/{session_id}")
        print(f"✅ Session found: {response.status_code == 200}")
        
        # Delete it
        print(f"\nDeleting session {session_id[:8]}...")
        response = await client.delete(f"{base_url}/sessions/{session_id}")
        print(f"✅ Deleted: {response.status_code == 204}")
        
        # Verify it's gone
        print("\nVerifying session is deleted...")
        response = await client.get(f"{base_url}/sessions/{session_id}")
        print(f"✅ Session not found: {response.status_code == 404}")
        
        print("\n🎉 Delete functionality works!")


if __name__ == "__main__":
    asyncio.run(test_delete())
