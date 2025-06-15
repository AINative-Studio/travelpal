"""
LangChain agent service for handling chat interactions with Llama API.
"""
import logging
import sys
import os
import traceback
import json
import requests
from typing import Dict, Any, Optional, List, Union, Type

# Configure logging with detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('travel_agent_debug.log')
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Python path: {sys.path}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Environment variables: {os.environ.get('PYTHONPATH', 'Not set')}")

# Try to import LangChain components
try:
    logger.info("Attempting to import LangChain components...")
    
    try:
        import langchain
        import langchain_core
        import langchain_community
        logger.info(f"Successfully imported langchain ({langchain.__version__}), langchain_core, and langchain_community")
    except ImportError as e:
        logger.error(f"Failed to import LangChain core packages: {e}")
        raise
    
    try:
        # Import required components
        import requests
        import json
        from typing import Dict, Any, Optional
        from langchain.chains import LLMChain
        from langchain.prompts import (
            SystemMessagePromptTemplate,
            HumanMessagePromptTemplate,
            ChatPromptTemplate,
        )
        logger.info("Successfully imported components for Meta Cloud API")
    except ImportError as e:
        logger.error(f"Failed to import required components: {e}")
        raise
    
    try:
        # Import memory components
        from langchain.memory import ConversationBufferMemory
        # Try different import paths for BaseChatMessageHistory
        try:
            from langchain.memory.chat_message_histories.base import BaseChatMessageHistory
            logger.info("Successfully imported BaseChatMessageHistory from langchain.memory.chat_message_histories.base")
        except ImportError:
            try:
                from langchain.schema import BaseChatMessageHistory
                logger.info("Successfully imported BaseChatMessageHistory from langchain.schema")
            except ImportError as e:
                logger.error(f"Failed to import BaseChatMessageHistory: {e}")
                raise
        logger.info("Successfully imported memory components")
    except ImportError as e:
        logger.error(f"Failed to import memory components: {e}")
        raise
    
    try:
        # Import our custom memory implementation
        from app.services.langchain.memory import PydanticV2CompatibleChatMessageHistory
        logger.info("Successfully imported custom memory implementation")
    except ImportError as e:
        logger.error(f"Failed to import custom memory implementation: {e}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Files in current directory: {os.listdir()}")
        raise
    
    try:
        # Set up the chat message history class to use our custom implementation
        class CustomChatMessageHistory(PydanticV2CompatibleChatMessageHistory, BaseChatMessageHistory):
            """Wrapper class to make our custom history work with LangChain."""
            pass
        logger.info("Successfully created CustomChatMessageHistory class")
    except Exception as e:
        logger.error(f"Failed to create CustomChatMessageHistory: {e}")
        raise
    
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import LangChain components: {e}", exc_info=True)
    LANGCHAIN_AVAILABLE = False

class TravelAgent:
    """A LangChain-based travel agent for handling chat interactions.
    
    This class provides a simple interface for processing chat messages using LangChain's
    LLMChain with conversation memory.
    
    Attributes:
        llm: The language model used for generating responses.
        memory: The conversation memory for storing chat history.
        conversation: The LLMChain for processing messages.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of TravelAgent exists (singleton pattern)."""
        # Skip singleton behavior during test runs to avoid import-time side effects
        if 'pytest' in sys.modules and cls._instance is None:
            return super().__new__(cls)
            
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 500,
        verbose: bool = True,
        **model_kwargs
    ) -> None:
        """Initialize the TravelAgent with the specified language model.
        
        Args:
            model_name: The name of the model to use.
            temperature: Controls randomness in the output (0.0 to 1.0).
            max_tokens: Maximum number of tokens to generate.
            verbose: Whether to enable verbose mode.
            **model_kwargs: Additional keyword arguments to pass to the model.
        """
        # Skip initialization if already initialized to avoid reinitialization in singleton pattern
        if hasattr(self, 'initialized') and self.initialized:
            return
            
        if not LANGCHAIN_AVAILABLE:
            logger.error("LangChain is not available. Please install the required dependencies.")
            return
            
        try:
            # Initialize Llama API settings
            self.api_url = os.getenv('LLAMA_API_URL', 'https://api.llama.com/v1/chat/completions')
            self.api_key = os.getenv('LLAMA_API_KEY') or os.getenv('META_API_KEY')
            self.model_name = model_name or "Llama-4-Maverick-17B-128E-Instruct-FP8"
            self.temperature = temperature
            self.max_tokens = max_tokens
            self.model_kwargs = model_kwargs
            
            if not self.api_key:
                raise ValueError("LLAMA_API_KEY or META_API_KEY environment variable is not set")
                
            logger.info(f"Initializing TravelAgent with Llama API at {self.api_url}")
            logger.info(f"Using model: {self.model_name}")
                
            # Initialize conversation memory with our custom implementation
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                chat_memory=CustomChatMessageHistory()
            )
            
            self.initialized = True
            logger.info(f"TravelAgent initialized with model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize TravelAgent: {e}")
            raise
    
    def process_message(self, message: str) -> str:
        """Process a message using Llama API and return the assistant's response.
        
        Args:
            message: The user's message to process
            
        Returns:
            str: The assistant's response
            
        Raises:
            ValueError: If the message is empty or contains only whitespace
            requests.exceptions.RequestException: If there's an error making the API request
            Exception: For other unexpected errors
        """
        # Validate input
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")
            
        if not self.api_key:
            raise ValueError("API key is not set. Please set LLAMA_API_KEY environment variable.")
            
        message = message.strip()
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare the conversation history
            messages = [
                {"role": "system", "content": "You are a helpful travel assistant."}
            ]
            
            # Add conversation history if available
            if hasattr(self, 'memory') and hasattr(self.memory, 'chat_memory'):
                for msg in self.memory.chat_memory.messages:
                    role = "user" if msg.type == "human" else "assistant"
                    messages.append({
                        "role": role,
                        "content": msg.content
                    })
            
            # Add the new message
            messages.append({"role": "user", "content": message})
            
            # Prepare the request payload
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                **self.model_kwargs
            }
            
            logger.debug(f"Sending request to {self.api_url} with payload: {json.dumps(payload, indent=2)}")
            
            # Make the API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Extract the response
            result = response.json()
            logger.debug(f"Received response: {json.dumps(result, indent=2)}")
            
            # Handle error responses
            if 'error' in result:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                logger.error(f"API error: {error_msg}")
                raise requests.exceptions.HTTPError(f"API error: {error_msg}", response=response)
            
            # Handle different successful response formats
            if 'completion_message' in result and 'content' in result['completion_message']:
                content = result['completion_message']['content']
                if isinstance(content, dict) and 'text' in content:
                    assistant_message = content['text']
                else:
                    assistant_message = str(content)
            elif 'choices' in result and result['choices']:
                assistant_message = result['choices'][0]['message']['content']
            else:
                logger.error(f"Unexpected response format: {result}")
                raise ValueError("Unexpected response format from API")
            
            # Update conversation memory
            if hasattr(self, 'memory') and hasattr(self.memory, 'chat_memory'):
                self.memory.chat_memory.add_user_message(message)
                self.memory.chat_memory.add_ai_message(assistant_message)
            
            return assistant_message
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error making request to Llama API: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nStatus code: {e.response.status_code}"
                try:
                    error_msg += f"\nResponse: {e.response.text}"
                except:
                    pass
            logger.error(error_msg)
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error processing message: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "I'm sorry, I encountered an error while processing your request. Please try again later."

# Singleton instance of the travel agent
# Only create the singleton if we're not in test mode
if 'pytest' not in sys.modules and LANGCHAIN_AVAILABLE:
    try:
        travel_agent = TravelAgent()
        logger.info("Initialized global travel_agent instance")
    except Exception as e:
        logger.error(f"Failed to initialize global travel_agent: {e}")
        travel_agent = None
else:
    # In test mode, we'll create the instance in the tests
    travel_agent = None
