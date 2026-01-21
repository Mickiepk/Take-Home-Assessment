"""
Agent service that integrates the Computer Use Agent from computer_use_demo.
"""

import asyncio
import os
from typing import AsyncIterator, List, Dict, Any, Optional
from datetime import datetime

# Import from the existing computer_use_demo
from computer_use_demo.loop import sampling_loop, APIProvider
from computer_use_demo.tools import (
    ToolCollection,
    TOOL_GROUPS_BY_VERSION,
    ToolVersion,
    ToolResult,
)
from anthropic.types.beta import (
    BetaMessageParam,
    BetaContentBlockParam,
    BetaTextBlockParam,
)

from ..models.schemas import AgentUpdate, UpdateType, MessageRole
from ..config import get_settings
from ..logging_config import get_logger

logger = get_logger(__name__)

class AgentService:
    """
    Service that wraps the original Computer Use Agent and provides
    integration with the new backend architecture.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.settings = get_settings()
        
        # Set required environment variables for Computer Use Agent
        os.environ["WIDTH"] = str(self.settings.width)
        os.environ["HEIGHT"] = str(self.settings.height)
        os.environ["DISPLAY_NUM"] = str(self.settings.display_num)
        
        # Agent configuration
        self.model = self.settings.default_model
        self.provider = APIProvider.ANTHROPIC
        self.api_key = self.settings.anthropic_api_key
        self.max_tokens = self.settings.max_tokens
        self.tool_version: ToolVersion = "computer_use_20250124"
        
        # Message history for the agent
        self.messages: List[BetaMessageParam] = []
        
        # Tool collection setup
        tool_group = TOOL_GROUPS_BY_VERSION[self.tool_version]
        self.tool_collection = ToolCollection(*(ToolCls() for ToolCls in tool_group.tools))
        
        logger.info("AgentService initialized", 
                   session_id=session_id, 
                   model=self.model,
                   tool_version=self.tool_version,
                   display_size=f"{self.settings.width}x{self.settings.height}")
    
    async def process_message(
        self, 
        message_content: str,
        message_role: MessageRole = MessageRole.USER
    ) -> AsyncIterator[AgentUpdate]:
        
        try:
            # Add the user message to the conversation history
            self.messages.append({
                "role": message_role.value,
                "content": [
                    BetaTextBlockParam(type="text", text=message_content)
                ]
            })
            
            logger.info("Processing message with agent", 
                       session_id=self.session_id,
                       message_length=len(message_content))
            
            # Yield initial thinking update
            yield AgentUpdate(
                update_type=UpdateType.THINKING,
                content="Starting to process your request with Computer Use Agent...",
                timestamp=datetime.utcnow(),
                metadata={"session_id": self.session_id}
            )
            
            # Create callbacks to capture agent output
            output_queue: asyncio.Queue = asyncio.Queue()
            tool_output_queue: asyncio.Queue = asyncio.Queue()
            
            def output_callback(content_block: BetaContentBlockParam) -> None:
                """Callback for agent output."""
                asyncio.create_task(output_queue.put(content_block))
            
            def tool_output_callback(tool_result: ToolResult, tool_id: str) -> None:
                """Callback for tool execution results."""
                asyncio.create_task(tool_output_queue.put((tool_result, tool_id)))
            
            def api_response_callback(request, response, error) -> None:
                """Callback for API responses (for logging)."""
                if error:
                    logger.error("API error", session_id=self.session_id, error=str(error))
            
            # Run the sampling loop in a background task
            async def run_agent():
                try:
                    updated_messages = await sampling_loop(
                        model=self.model,
                        provider=self.provider,
                        system_prompt_suffix="",
                        messages=self.messages,
                        output_callback=output_callback,
                        tool_output_callback=tool_output_callback,
                        api_response_callback=api_response_callback,
                        api_key=self.api_key,
                        only_n_most_recent_images=3,
                        max_tokens=self.max_tokens,
                        tool_version=self.tool_version,
                        thinking_budget=None,
                        token_efficient_tools_beta=False,
                    )
                    # Update our message history
                    self.messages = updated_messages
                    # Signal completion
                    await output_queue.put(None)
                except Exception as e:
                    logger.error("Agent execution failed", 
                               session_id=self.session_id, 
                               error=str(e))
                    await output_queue.put({"error": str(e)})
            
            # Start the agent task
            agent_task = asyncio.create_task(run_agent())
            
            # Stream updates as they come in
            while True:
                try:
                    # Check for output updates
                    try:
                        content_block = await asyncio.wait_for(
                            output_queue.get(), 
                            timeout=0.1
                        )
                        
                        if content_block is None:
                            # Agent completed
                            break
                        
                        if isinstance(content_block, dict) and "error" in content_block:
                            # Error occurred
                            yield AgentUpdate(
                                update_type=UpdateType.ERROR,
                                content=f"Agent error: {content_block['error']}",
                                timestamp=datetime.utcnow(),
                                metadata={"session_id": self.session_id}
                            )
                            break
                        
                        # Process the content block
                        update = self._content_block_to_update(content_block)
                        if update:
                            yield update
                            
                    except asyncio.TimeoutError:
                        pass
                    
                    # Check for tool output updates
                    try:
                        tool_result, tool_id = await asyncio.wait_for(
                            tool_output_queue.get(),
                            timeout=0.1
                        )
                        
                        # Yield tool result update
                        yield self._tool_result_to_update(tool_result, tool_id)
                        
                    except asyncio.TimeoutError:
                        pass
                    
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.05)
                    
                except Exception as e:
                    logger.error("Error streaming updates", 
                               session_id=self.session_id,
                               error=str(e))
                    yield AgentUpdate(
                        update_type=UpdateType.ERROR,
                        content=f"Streaming error: {str(e)}",
                        timestamp=datetime.utcnow(),
                        metadata={"session_id": self.session_id}
                    )
                    break
            
            # Wait for agent task to complete
            await agent_task
            
            # Yield final completion update
            yield AgentUpdate(
                update_type=UpdateType.COMPLETE,
                content="Agent processing completed",
                timestamp=datetime.utcnow(),
                metadata={"session_id": self.session_id, "completed": True}
            )
            
            logger.info("Message processing completed", session_id=self.session_id)
            
        except Exception as e:
            logger.error("Failed to process message", 
                        session_id=self.session_id,
                        error=str(e))
            yield AgentUpdate(
                update_type=UpdateType.ERROR,
                content=f"Failed to process message: {str(e)}",
                timestamp=datetime.utcnow(),
                metadata={"session_id": self.session_id, "error": str(e)}
            )
    def _content_block_to_update(self, content_block: BetaContentBlockParam) -> Optional[AgentUpdate]:
        """Convert a content block from the agent to an AgentUpdate."""
        try:
            if isinstance(content_block, dict):
                block_type = content_block.get("type")
                
                if block_type == "text":
                    return AgentUpdate(
                        update_type=UpdateType.THINKING,
                        content=content_block.get("text", ""),
                        timestamp=datetime.utcnow(),
                        metadata={"session_id": self.session_id}
                    )
                
                elif block_type == "thinking":
                    return AgentUpdate(
                        update_type=UpdateType.THINKING,
                        content=content_block.get("thinking", ""),
                        timestamp=datetime.utcnow(),
                        metadata={"session_id": self.session_id, "is_thinking": True}
                    )
                
                elif block_type == "tool_use":
                    tool_name = content_block.get("name", "unknown")
                    tool_input = content_block.get("input", {})
                    return AgentUpdate(
                        update_type=UpdateType.TOOL_USE,
                        content=f"Using tool: {tool_name}",
                        timestamp=datetime.utcnow(),
                        metadata={
                            "session_id": self.session_id,
                            "tool_name": tool_name,
                            "tool_input": tool_input
                        }
                    )
            
            return None
            
        except Exception as e:
            logger.error("Failed to convert content block", error=str(e))
            return None
    
    def _tool_result_to_update(self, tool_result: ToolResult, tool_id: str) -> AgentUpdate:
        """Convert a tool result to an AgentUpdate."""
        content = ""
        metadata: Dict[str, Any] = {
            "session_id": self.session_id,
            "tool_id": tool_id
        }
        
        if tool_result.error:
            content = f"Tool error: {tool_result.error}"
            metadata["error"] = tool_result.error
        elif tool_result.output:
            content = f"Tool output: {tool_result.output[:200]}..."  # Truncate for streaming
            metadata["has_output"] = True
        
        if tool_result.base64_image:
            metadata["has_screenshot"] = True
            content += " (Screenshot captured)"
        
        return AgentUpdate(
            update_type=UpdateType.TOOL_RESULT,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation history."""
        return [dict(msg) for msg in self.messages]
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.messages = []
        logger.info("Conversation history cleared", session_id=self.session_id)
