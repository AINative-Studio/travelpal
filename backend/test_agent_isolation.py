"""
Isolated test for the TravelAgent class.
This test doesn't load the application's conftest.py to avoid dependency issues.
"""
import pytest
from unittest.mock import MagicMock, patch, ANY
import sys
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Mock the LangChain imports before importing our module
with patch.dict('sys.modules', {
    'langchain_openai': MagicMock(),
    'langchain.chains': MagicMock(),
    'langchain.prompts': MagicMock(),
    'langchain.schema': MagicMock(),
    'langchain.memory': MagicMock(),
    'langchain_community': MagicMock(),
    'langchain_core': MagicMock(),
}):
    # Now import our module
    from app.services.langchain.agent import TravelAgent, LANGCHAIN_AVAILABLE

def test_agent_initialization():
    """Test that the TravelAgent can be initialized."""
    logger.info("Starting test_agent_initialization")
    
    # Skip if LangChain is not available
    if not LANGCHAIN_AVAILABLE:
        logger.warning("LangChain is not available, skipping test")
        pytest.skip("LangChain is not available")
    
    try:
        # Create a test agent
        logger.info("Creating TravelAgent instance")
        agent = TravelAgent()
        
        # Verify the agent was created
        assert agent is not None, "Agent should not be None"
        assert hasattr(agent, 'llm'), "Agent should have 'llm' attribute"
        assert hasattr(agent, 'memory'), "Agent should have 'memory' attribute"
        assert hasattr(agent, 'conversation'), "Agent should have 'conversation' attribute"
        
        logger.info("Test passed: TravelAgent initialized successfully")
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        raise

def test_process_message():
    """Test processing a message with the agent."""
    logger.info("Starting test_process_message")
    
    # Skip if LangChain is not available
    if not LANGCHAIN_AVAILABLE:
        logger.warning("LangChain is not available, skipping test")
        pytest.skip("LangChain is not available")
    
    try:
        # Create a test agent
        logger.info("Creating TravelAgent instance")
        agent = TravelAgent()
        
        # Mock the conversation chain's run method
        with patch.object(agent.conversation, 'run') as mock_run:
            # Set up the mock to return a test response
            test_response = "Test response from agent"
            mock_run.return_value = test_response
            
            # Test with a valid message
            test_message = "Hello, test!"
            logger.info(f"Processing test message: {test_message}")
            response = agent.process_message(test_message)
            
            # Verify the response
            assert isinstance(response, str), "Response should be a string"
            assert len(response) > 0, "Response should not be empty"
            assert response == test_response, "Response should match the expected test response"
            
            # Verify the mock was called correctly
            mock_run.assert_called_once_with({"input": test_message})
            
            logger.info("Test passed: Message processed successfully")
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Run the tests directly with more verbose output
    logger.info("Starting test execution")
    exit_code = pytest.main([
        __file__,
        "-v",
        "-s",
        "--log-cli-level=INFO",
        "--log-cli-format=%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ])
    logger.info(f"Test execution completed with exit code: {exit_code}")
    sys.exit(exit_code)
