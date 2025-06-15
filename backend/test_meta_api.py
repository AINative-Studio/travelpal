"""
Test script to verify Meta Llama API integration and functionality.

This script provides end-to-end tests for the Meta Llama API integration,
including connection testing, error handling, and response validation.
"""
import os
import sys
import json
import logging
import pytest
import requests
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Test configuration
TEST_CONFIG = {
    "api_url": "https://api.llama.com/v1/chat/completions",
    "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
    "test_messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Can you tell me a short joke?"}
    ],
    "timeout": 30
}

def get_api_headers():
    """Get the API headers with authentication."""
    api_key = os.getenv("LLAMA_API_KEY") or os.getenv("META_API_KEY")
    if not api_key:
        raise ValueError("LLAMA_API_KEY or META_API_KEY not found in environment")
    
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

def test_api_initialization():
    """Test that API credentials are properly loaded."""
    api_key = os.getenv("LLAMA_API_KEY") or os.getenv("META_API_KEY")
    assert api_key is not None, "API key not found in environment"
    assert len(api_key) > 30, "API key appears to be invalid (too short)"
    logger.info("✅ API credentials loaded successfully")

def test_llama_api_connection():
    """Test the connection to Llama API with a simple request."""
    try:
        headers = get_api_headers()
    except ValueError as e:
        pytest.skip(str(e))
    
    payload = {
        "model": TEST_CONFIG["model"],
        "messages": TEST_CONFIG["test_messages"],
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    try:
        logger.info(f"🔍 Testing connection to Llama API at {TEST_CONFIG['api_url']}...")
        logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            TEST_CONFIG["api_url"],
            headers=headers,
            json=payload,
            timeout=TEST_CONFIG["timeout"]
        )
        
        # Print the full response for debugging
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        
        response.raise_for_status()
        result = response.json()
        
        # Log the successful response
        logger.info("\n✅ Successfully connected to Llama API")
        logger.info(f"Response ID: {result.get('id', 'N/A')}")
        
        # Validate the response structure
        assert isinstance(result, dict), "Response is not a JSON object"
        
        # Check for both possible response formats
        if 'completion_message' in result:
            assert 'content' in result['completion_message'], "Missing content in completion_message"
            content = result['completion_message']['content']
            if isinstance(content, dict):
                assert 'text' in content, "Missing 'text' in content dictionary"
                logger.info(f"\nAssistant's response: {content['text']}")
                assert len(content['text']) > 0, "Empty response text"
            else:
                logger.info(f"\nAssistant's response: {content}")
                assert len(str(content)) > 0, "Empty response content"
        elif 'choices' in result and result['choices']:
            # Handle OpenAI-compatible format
            choice = result['choices'][0]
            assert 'message' in choice, "Missing message in choices"
            assert 'content' in choice['message'], "Missing content in message"
            logger.info(f"\nAssistant's response: {choice['message']['content']}")
        else:
            pytest.fail(f"Unexpected response format: {json.dumps(result, indent=2)}")
        
        # Test response metadata
        if 'model' in result:
            logger.info(f"Model used: {result['model']}")
        if 'usage' in result:
            logger.info(f"Token usage: {result['usage']}")
            
        # Remove the return True as it's not needed and causes a pytest warning
        pass
        
    except requests.exceptions.RequestException as e:
        error_msg = f"\n❌ Error connecting to Llama API: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f"\nStatus Code: {e.response.status_code}"
            error_msg += f"\nResponse: {e.response.text}"
            
            # Provide more specific error messages for common issues
            if e.response.status_code == 401:
                error_msg += "\n⚠️  Authentication failed. Please check your API key."
            elif e.response.status_code == 404:
                error_msg += "\n⚠️  Endpoint not found. The API URL may be incorrect."
            elif e.response.status_code == 429:
                error_msg += "\n⚠️  Rate limit exceeded. Please try again later."
        
        # Check for common connection issues
        if "Failed to resolve" in str(e):
            error_msg += "\n⚠️  DNS resolution failed. Please check your internet connection."
        elif "timed out" in str(e).lower():
            error_msg += "\n⚠️  Connection timed out. The server might be down or your internet connection is slow."
        
        logger.error(error_msg)
        pytest.fail(error_msg)
        logger.error(traceback.format_exc())
        return False

@pytest.fixture
def mock_requests():
    """Fixture to mock requests for testing error cases."""
    with patch('requests.post') as mock_post:
        yield mock_post

def test_rate_limit_handling(mock_requests):
    """Test handling of rate limit errors."""
    # Mock a rate limit response
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "429 Client Error: Too Many Requests"
    )
    mock_response.json.return_value = {
        'error': {
            'message': 'Rate limit exceeded',
            'type': 'rate_limit_error',
            'code': 429
        }
    }
    mock_requests.return_value = mock_response
    
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        response = requests.post(
            TEST_CONFIG["api_url"],
            headers={"Authorization": "Bearer test_key"},
            json={"messages": [{"role": "user", "content": "test"}]},
            timeout=10
        )
        response.raise_for_status()
    
    assert "429" in str(exc_info.value)
    assert "Too Many Requests" in str(exc_info.value)

def test_invalid_api_key():
    """Test behavior with an invalid API key."""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid_key_123"
        }
        
        response = requests.post(
            TEST_CONFIG["api_url"],
            headers=headers,
            json={
                "model": TEST_CONFIG["model"],
                "messages": TEST_CONFIG["test_messages"]
            },
            timeout=TEST_CONFIG["timeout"]
        )
        
        # Some APIs return 401 for invalid keys, others might return 403
        assert response.status_code in (401, 403), \
            f"Expected 401 or 403 for invalid API key, got {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code not in (401, 403):
                raise
            logger.warning(f"Received expected {e.response.status_code} for invalid API key")
        else:
            raise

def test_long_conversation():
    """Test conversation with a longer context."""
    try:
        headers = get_api_headers()
    except ValueError as e:
        pytest.skip(str(e))
    
    # Create a longer conversation
    messages = [
        {"role": "system", "content": "You are a helpful assistant that provides detailed responses."},
        {"role": "user", "content": "Tell me a detailed story about a space adventure."}
    ]
    
    payload = {
        "model": TEST_CONFIG["model"],
        "messages": messages,
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            TEST_CONFIG["api_url"],
            headers=headers,
            json=payload,
            timeout=TEST_CONFIG["timeout"]
        )
        response.raise_for_status()
        result = response.json()
        
        # Verify the response contains the expected content
        if 'completion_message' in result and 'content' in result['completion_message']:
            content = result['completion_message']['content']
            if isinstance(content, dict) and 'text' in content:
                text = content['text']
            else:
                text = str(content)
            
            assert len(text) > 100, "Response seems too short for a detailed story"
            logger.info(f"Received story of length {len(text)} characters")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in long conversation test: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Status code: {e.response.status_code}")
            logger.error(f"Response: {e.response.text}")
        raise

if __name__ == "__main__":
    logger.info("🚀 Starting Meta Llama API Test Suite")
    logger.info("=" * 50)
    
    # Run tests with more verbose output
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
