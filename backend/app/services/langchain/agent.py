"""
LangChain agent service for handling chat interactions.
"""
from typing import Dict, Any, Optional
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

class TravelAgent:
    """
    A LangChain-based travel agent that can handle natural language conversations
    and perform travel-related tasks.
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize the travel agent with a language model and memory.
        
        Args:
            model_name: Name of the OpenAI model to use (default: "gpt-3.5-turbo")
            temperature: Temperature for model generation (0.0 to 1.0, default: 0.7)
        """
        # Initialize the language model
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            streaming=False
        )
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize the conversation chain
        self.conversation = self._initialize_conversation()
        
    def _initialize_conversation(self) -> ConversationChain:
        """Initialize the conversation chain with a system message."""
        # Define the prompt template
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are a helpful travel assistant named TravelPal. 
                Your goal is to assist users with travel planning, including flights, 
                hotels, and activities. Be friendly, informative, and concise in your responses.
                If you don't know something, say so rather than making up information."""
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        
        # Create and return the conversation chain
        return ConversationChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )
    
    def process_message(self, message: str) -> str:
        """
        Process a user message and return the agent's response.
        
        Args:
            message: User's input message
            
        Returns:
            str: Agent's response
        """
        try:
            # Check if the message is empty
            if not message or not message.strip():
                return "I'm sorry, I didn't receive any message. How can I help you with your travel plans?"
                
            # Process the message with the conversation chain
            response = self.conversation.predict(input=message)
            
            # Ensure we return a string response
            if not response:
                return "I'm sorry, I didn't understand that. Could you please rephrase your question?"
                
            return str(response)
            
        except Exception as e:
            # Log the error for debugging
            import logging
            logging.error(f"Error processing message: {str(e)}", exc_info=True)
            
            # Return a user-friendly error message
            return "I'm sorry, I encountered an error while processing your request. Please try again later."

# Singleton instance of the travel agent
travel_agent = TravelAgent()
