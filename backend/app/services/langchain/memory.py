"""
Custom memory implementations for LangChain to handle Pydantic v2 compatibility.
"""
import logging
import sys
from typing import List, Dict, Any, Optional, Sequence

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Try to import LangChain message types
try:
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, message_to_dict, messages_from_dict
    LANGCHAIN_MESSAGES_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import LangChain message types: {e}")
    logger.error(f"Python path: {sys.path}")
    logger.error(f"Installed packages: {__import__('pip').internal.utils.misc.get_installed_distributions()}")
    LANGCHAIN_MESSAGES_AVAILABLE = False
    
    # Create dummy classes for type checking when imports fail
    class BaseMessage:
        pass
    
    class HumanMessage:
        def __init__(self, content: str):
            self.content = content
    
    class AIMessage:
        def __init__(self, content: str):
            self.content = content
    
    class SystemMessage:
        def __init__(self, content: str):
            self.content = content
            
    def message_to_dict(msg):
        return {"content": msg.content, "type": msg.__class__.__name__}
        
    def messages_from_dict(messages):
        return [msg for msg in messages]  # Simplified for testing

class PydanticV2CompatibleChatMessageHistory:
    """A chat message history that's compatible with Pydantic v2 and LangChain."""
    
    def __init__(self, messages: Optional[List[BaseMessage]] = None):
        """Initialize with optional list of messages."""
        logger.debug("Initializing PydanticV2CompatibleChatMessageHistory")
        if not LANGCHAIN_MESSAGES_AVAILABLE:
            logger.warning("LangChain message types not available, using fallback implementation")
        self._messages: List[BaseMessage] = messages or []
        logger.debug(f"Initialized with {len(self._messages)} messages")
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve the current list of messages."""
        logger.debug(f"Getting {len(self._messages)} messages")
        return self._messages
    
    @messages.setter
    def messages(self, value: List[BaseMessage]) -> None:
        """Set the messages list."""
        logger.debug(f"Setting {len(value) if value else 0} messages")
        if not isinstance(value, list):
            logger.warning(f"Expected list of messages, got {type(value)}")
            value = []
        self._messages = value
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the history."""
        logger.debug(f"Adding message: {getattr(message, 'content', '[no content]')}")
        if not hasattr(self, '_messages'):
            self._messages = []
        self._messages.append(message)
    
    def add_user_message(self, message: str) -> None:
        """Add a user message to the history."""
        self._messages.append(HumanMessage(content=message))
    
    def add_ai_message(self, message: str) -> None:
        """Add an AI message to the history."""
        self._messages.append(AIMessage(content=message))
    
    def add_system_message(self, message: str) -> None:
        """Add a system message to the history."""
        self._messages.append(SystemMessage(content=message))
    
    def clear(self) -> None:
        """Clear all messages from the history."""
        self._messages = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the history to a dictionary."""
        return {"messages": [message_to_dict(msg) for msg in self._messages]}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PydanticV2CompatibleChatMessageHistory':
        """Create a new instance from a dictionary."""
        messages = messages_from_dict(data.get("messages", []))
        return cls(messages=messages)
    
    def __getitem__(self, index: int) -> BaseMessage:
        """Get a message by index."""
        return self._messages[index]
    
    def __len__(self) -> int:
        """Get the number of messages in the history."""
        return len(self._messages)
    
    def __iter__(self):
        """Iterate over messages."""
        return iter(self._messages)
    
    def __add__(self, other: 'PydanticV2CompatibleChatMessageHistory') -> 'PydanticV2CompatibleChatMessageHistory':
        """Combine two chat histories."""
        return PydanticV2CompatibleChatMessageHistory(messages=self._messages + other.messages)
