"""
Mock Agent Service for demo purposes (no API key required).
"""

import asyncio
from typing import AsyncIterator
from datetime import datetime

from ..models.schemas import AgentUpdate, UpdateType, MessageRole
from ..logging_config import get_logger

logger = get_logger(__name__)


class MockAgentService:
    """
    Mock agent service that simulates Computer Use Agent responses
    without requiring an Anthropic API key.
    
    Perfect for demos, testing, and development.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages = []
        logger.info("MockAgentService initialized", session_id=session_id)
    
    async def process_message(
        self, 
        message_content: str,
        message_role: MessageRole = MessageRole.USER
    ) -> AsyncIterator[AgentUpdate]:
        """
        Process a message and yield mock updates simulating real agent behavior.
        """
        try:
            # Store the message
            self.messages.append({
                "role": message_role.value,
                "content": message_content
            })
            
            logger.info("Processing message with mock agent", 
                       session_id=self.session_id,
                       message_length=len(message_content))
            
            # Yield thinking update
            yield AgentUpdate(
                update_type=UpdateType.THINKING,
                content="Analyzing your request...",
                timestamp=datetime.utcnow(),
                metadata={"session_id": self.session_id}
            )
            
            await asyncio.sleep(0.5)
            
            # Simulate tool use based on message content
            if any(word in message_content.lower() for word in ["calculate", "math", "+", "-", "*", "/", "="]):
                yield AgentUpdate(
                    update_type=UpdateType.TOOL_USE,
                    content="Using calculator tool",
                    timestamp=datetime.utcnow(),
                    metadata={
                        "session_id": self.session_id,
                        "tool_name": "calculator",
                        "tool_input": {"expression": message_content}
                    }
                )
                
                await asyncio.sleep(0.3)
                
                yield AgentUpdate(
                    update_type=UpdateType.TOOL_RESULT,
                    content="Calculation completed successfully",
                    timestamp=datetime.utcnow(),
                    metadata={"session_id": self.session_id}
                )
            
            elif any(word in message_content.lower() for word in ["file", "list", "directory", "ls"]):
                yield AgentUpdate(
                    update_type=UpdateType.TOOL_USE,
                    content="Using bash tool",
                    timestamp=datetime.utcnow(),
                    metadata={
                        "session_id": self.session_id,
                        "tool_name": "bash",
                        "tool_input": {"command": "ls -la"}
                    }
                )
                
                await asyncio.sleep(0.4)
                
                yield AgentUpdate(
                    update_type=UpdateType.TOOL_RESULT,
                    content="Command executed: Found 15 files in directory",
                    timestamp=datetime.utcnow(),
                    metadata={"session_id": self.session_id}
                )
            
            elif any(word in message_content.lower() for word in ["weather", "temperature"]):
                yield AgentUpdate(
                    update_type=UpdateType.TOOL_USE,
                    content="Using web search tool",
                    timestamp=datetime.utcnow(),
                    metadata={
                        "session_id": self.session_id,
                        "tool_name": "web_search",
                        "tool_input": {"query": message_content}
                    }
                )
                
                await asyncio.sleep(0.5)
                
                yield AgentUpdate(
                    update_type=UpdateType.TOOL_RESULT,
                    content="Retrieved weather data successfully",
                    timestamp=datetime.utcnow(),
                    metadata={"session_id": self.session_id, "has_screenshot": True}
                )
            
            await asyncio.sleep(0.3)
            
            # Generate response based on message content
            response = self._generate_response(message_content)
            
            yield AgentUpdate(
                update_type=UpdateType.THINKING,
                content=response,
                timestamp=datetime.utcnow(),
                metadata={"session_id": self.session_id}
            )
            
            await asyncio.sleep(0.2)
            
            # Yield completion
            yield AgentUpdate(
                update_type=UpdateType.COMPLETE,
                content="Processing completed successfully",
                timestamp=datetime.utcnow(),
                metadata={"session_id": self.session_id, "completed": True}
            )
            
            logger.info("Mock message processing completed", session_id=self.session_id)
            
        except Exception as e:
            logger.error("Failed to process message", 
                        session_id=self.session_id,
                        error=str(e))
            yield AgentUpdate(
                update_type=UpdateType.ERROR,
                content=f"Error: {str(e)}",
                timestamp=datetime.utcnow(),
                metadata={"session_id": self.session_id, "error": str(e)}
            )
    
    def _generate_response(self, message: str) -> str:
        """Generate a mock response based on the message content."""
        message_lower = message.lower()
        
        # Math/calculation
        if "2+2" in message_lower or "2 + 2" in message_lower:
            return "The answer is 4. I calculated this using basic arithmetic."
        
        if "25" in message_lower and "4" in message_lower and any(op in message_lower for op in ["*", "times", "multiply"]):
            return "25 times 4 equals 100."
        
        if any(op in message_lower for op in ["+", "-", "*", "/", "calculate"]):
            return "I've performed the calculation and the result is ready."
        
        # Weather
        if "weather" in message_lower:
            if "dubai" in message_lower:
                return "The weather in Dubai is currently sunny with a temperature of 28°C (82°F). It's a typical warm day with clear skies and low humidity."
            return "I can check the weather for you. The current conditions show clear skies with moderate temperatures."
        
        # Files/directory
        if any(word in message_lower for word in ["file", "list", "directory", "ls"]):
            return "Here are the files in the current directory:\n- computer_use_backend/\n- computer_use_demo/\n- docker-compose.yml\n- README.md\n- requirements.txt\n\nTotal: 15 files and 5 directories."
        
        # Greetings
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm the Computer Use Agent. I can help you with calculations, file operations, web searches, and more. What would you like me to do?"
        
        # Default response
        return f"I've processed your request about '{message}'. The task has been completed successfully."
    
    def get_conversation_history(self):
        """Get the conversation history."""
        return self.messages
    
    def clear_history(self):
        """Clear the conversation history."""
        self.messages = []
        logger.info("Conversation history cleared", session_id=self.session_id)
