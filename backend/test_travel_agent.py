"""
Test suite for the TravelAgent class with Llama API integration.

This test suite verifies the functionality of the TravelAgent class
when interacting with the Llama API.
"""
import sys
import os
import json
import logging
import pytest
import requests
import traceback
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Check for required environment variables
LLAMA_API_KEY = os.getenv('LLAMA_API_KEY') or os.getenv('META_API_KEY')
if not LLAMA_API_KEY:
    logger.error("LLAMA_API_KEY or META_API_KEY is not set in the environment variables")
    logger.info("Please set the LLAMA_API_KEY in your .env file")
    logger.info("You can get an API key from the Llama Developer Portal")
    sys.exit(1)

# Test fixtures
@pytest.fixture(scope="module")
def travel_agent():
    """Create a TravelAgent instance for testing."""
    from app.services.langchain.agent import TravelAgent, LANGCHAIN_AVAILABLE
    
    if not LANGCHAIN_AVAILABLE:
        pytest.skip("LangChain is not available. Skipping tests.")
    
    agent = TravelAgent(
        model_name="Llama-4-Maverick-17B-128E-Instruct-FP8",
        temperature=0.7,
        max_tokens=500,
        verbose=True
    )
    return agent

# Test cases
class TestTravelAgent:
    """Test cases for the TravelAgent class with Llama API integration."""
    
    def test_initialization(self, travel_agent):
        """Test that the TravelAgent initializes correctly."""
        assert travel_agent is not None
        assert hasattr(travel_agent, 'process_message')
        assert callable(travel_agent.process_message)
    
    def test_process_message_valid_input(self, travel_agent):
        """Test processing a valid message."""
        response = travel_agent.process_message("Hello, can you help me plan a trip?")
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Check that the conversation history was updated
        assert hasattr(travel_agent.memory, 'chat_memory')
        assert len(travel_agent.memory.chat_memory.messages) >= 2  # System + User + Assistant
    
    def test_process_message_empty_input(self, travel_agent):
        """Test processing an empty message."""
        # Clear any existing messages in the conversation
        travel_agent.memory.chat_memory.clear()
        
        # Test with empty string
        with pytest.raises(ValueError, match="Message cannot be empty"):
            travel_agent.process_message("")
            
        # Test with whitespace only
        with pytest.raises(ValueError, match="Message cannot be empty"):
            travel_agent.process_message("   ")
    
    def test_process_message_long_input(self, travel_agent):
        """Test processing a very long message."""
        long_message = "A" * 10000  # 10k characters
        response = travel_agent.process_message(long_message)
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_conversation_history(self, travel_agent):
        """Test that conversation history is maintained."""
        # Clear any previous conversation
        travel_agent.memory.chat_memory.clear()
        
        # First message
        response1 = travel_agent.process_message("What's the weather like today?")
        assert len(travel_agent.memory.chat_memory.messages) == 2  # System + User + Assistant
        
        # Second message that references previous context
        response2 = travel_agent.process_message("What about tomorrow?")
        assert len(travel_agent.memory.chat_memory.messages) == 4  # System + 2x(User + Assistant)
        
        # The second response should be different from the first
        assert response1 != response2

    @patch('requests.post')
    def test_api_error_handling(self, mock_post, travel_agent):
        """Test that API errors are handled gracefully."""
        # Mock a failed API response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_response.json.return_value = {
            'completion_message': {
                'content': 'An error occurred',
                'role': 'assistant'
            },
            'error': {
                'message': 'Internal Server Error',
                'type': 'server_error',
                'code': 500
            }
        }
        mock_post.return_value = mock_response
        
        # The error should be propagated up as an HTTPError
        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            travel_agent.process_message("This should fail")
        assert "Internal Server Error" in str(exc_info.value)
    
    @patch('requests.post')
    def test_rate_limit_handling(self, mock_post, travel_agent):
        """Test that rate limit errors are handled."""
        # Mock a rate limit response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = 'Rate limit exceeded'
        mock_response.json.return_value = {
            'completion_message': {
                'content': 'Rate limit exceeded',
                'role': 'assistant'
            },
            'error': {
                'message': 'Rate limit exceeded',
                'type': 'rate_limit_error',
                'code': 429
            }
        }
        mock_post.return_value = mock_response
        
        # The error should be propagated up as an HTTPError
        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            travel_agent.process_message("This should hit rate limit")
        assert "Rate limit exceeded" in str(exc_info.value)

# Command-line test runner
def main():
    """Run the test suite from the command line."""
    try:
        # Add the backend directory to the Python path
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
        
        # Run pytest programmatically
        import pytest
        exit_code = pytest.main([
            '-v',
            '--tb=short',
            '--log-level=INFO',
            __file__
        ])
        
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Test runner failed with error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
