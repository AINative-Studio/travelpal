"""
Unit tests for the LangChain TravelAgent.
"""
import pytest
from unittest.mock import MagicMock, patch, ANY
import logging
from typing import List, Dict, Any, Optional

# Import the agent module to test
from app.services.langchain.agent import TravelAgent, travel_agent, LANGCHAIN_AVAILABLE

# Skip all tests if LangChain is not available
pytestmark = pytest.mark.skipif(
    not LANGCHAIN_AVAILABLE,
    reason="LangChain is not available. Skipping tests."
)

# Mock classes for testing
class MockMessage:
    def __init__(self, content: str, type: str = "human"):
        self.content = content
        self.type = type

    def dict(self) -> Dict[str, Any]:
        return {"content": self.content, "type": self.type}

class MockChatMessageHistory:
    def __init__(self, messages: Optional[List[Any]] = None):
        self.messages: List[Any] = messages or []
    
    def add_message(self, message: Any) -> None:
        self.messages.append(message)
    
    def clear(self) -> None:
        self.messages = []

class MockConversationBufferMemory:
    def __init__(self, *args, **kwargs):
        self.chat_memory = MockChatMessageHistory()
        self.return_messages = True
        self.memory_key = kwargs.get("memory_key", "chat_history")
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        pass
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {self.memory_key: self.chat_memory.messages}

@pytest.fixture
def mock_chat_openai():
    with patch('app.services.langchain.agent.ChatOpenAI') as mock:
        yield mock

@pytest.fixture
def mock_conversation_chain():
    with patch('app.services.langchain.agent.LLMChain') as mock:
        yield mock

@pytest.fixture
def mock_memory():
    with patch('app.services.langchain.agent.ConversationBufferMemory', new=MockConversationBufferMemory) as mock:
        yield mock

class TestTravelAgent:
    """Test cases for the TravelAgent class."""
    
    def test_initialization(self, mock_chat_openai, mock_conversation_chain, mock_memory):
        """Test that the TravelAgent initializes correctly."""
        # Setup mocks
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        mock_chain = MagicMock()
        mock_conversation_chain.return_value = mock_chain
        
        mock_mem = MagicMock()
        mock_memory.return_value = mock_mem
        
        # Test with default parameters
        agent = TravelAgent()
        
        # Verify initialization
        assert agent is not None
        assert hasattr(agent, 'llm')
        assert hasattr(agent, 'memory')
        assert hasattr(agent, 'conversation')
        
        # Verify LLM was initialized with correct defaults
        mock_chat_openai.assert_called_once_with(
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # Verify memory was initialized correctly
        mock_memory.assert_called_once_with(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Verify conversation chain was set up
        mock_conversation_chain.assert_called_once()
    
    def test_custom_initialization(self, mock_chat_openai, mock_conversation_chain, mock_memory):
        """Test initialization with custom parameters."""
        # Setup mocks
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        mock_chain = MagicMock()
        mock_conversation_chain.return_value = mock_chain
        
        # Test with custom parameters
        agent = TravelAgent(
            model_name="gpt-4",
            temperature=0.5,
            max_tokens=1000
        )
        
        # Verify custom parameters were passed to ChatOpenAI
        mock_chat_openai.assert_called_once_with(
            model_name="gpt-4",
            temperature=0.5,
            max_tokens=1000
        )
    
    def test_process_message_empty_input(self, mock_chat_openai, mock_conversation_chain, mock_memory):
        """Test processing an empty message returns a helpful response."""
        # Setup mocks
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        mock_chain = MagicMock()
        mock_conversation_chain.return_value = mock_chain
        
        agent = TravelAgent()
        
        # Test with empty message
        response = agent.process_message("")
        assert "I'm sorry, I didn't receive any message" in response
        
        # Test with whitespace message
        response = agent.process_message("   ")
        assert "I'm sorry, I didn't receive any message" in response
        
        # Verify the conversation chain was not called for empty inputs
        assert not mock_chain.run.called
    
    def test_process_message_valid_input(self, mock_chat_openai, mock_conversation_chain, mock_memory):
        """Test processing a valid message returns a response."""
        # Setup mocks
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        mock_chain = MagicMock()
        mock_chain.run.return_value = "This is a test response"
        mock_conversation_chain.return_value = mock_chain
        
        # Create a test agent
        agent = TravelAgent()
        
        # Test with a valid message
        response = agent.process_message("Hello, test!")
        
        # Verify response
        assert response == "This is a test response"
        
        # Verify run was called with the correct input
        mock_chain.run.assert_called_once_with(input="Hello, test!")
    
    def test_process_message_exception_handling(self, mock_chat_openai, mock_conversation_chain, mock_memory, caplog):
        """Test that exceptions are properly caught and handled."""
        # Setup mocks
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        mock_chain = MagicMock()
        mock_chain.run.side_effect = Exception("Test error")
        mock_conversation_chain.return_value = mock_chain
        
        # Set up logging capture
        caplog.set_level(logging.ERROR)
        
        agent = TravelAgent()
        
        # Should not raise an exception
        response = agent.process_message("This will cause an error")
        
        # Verify error response
        assert "I'm sorry, I encountered an error" in response
        
        # Verify error was logged
        assert "Error processing message" in caplog.text
        assert "Test error" in caplog.text
    
    def test_singleton_instance(self, mock_chat_openai, mock_conversation_chain, mock_memory):
        """Test that travel_agent is a singleton instance when not in test mode."""
        # In test mode, travel_agent should be None
        assert travel_agent is None
        
        # Create instances directly
        agent1 = TravelAgent()
        agent2 = TravelAgent()
        
        # In test mode, each instance should be different
        assert agent1 is not agent2
        
        # Test that the instances are of the correct type
        assert isinstance(agent1, TravelAgent)
        assert isinstance(agent2, TravelAgent)
