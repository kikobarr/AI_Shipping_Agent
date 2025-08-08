"""
OpenAI ChatCompletions API Connector
Handles communication with OpenAI's GPT models for the chatbot
"""

import os
import openai
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIConnector:
    def __init__(self):
        """Initialize the OpenAI connector with API key from environment"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        self.model = "gpt-3.5-turbo"  # Default model
        self.system_message = {
            "role": "system",
            "content": """You are a helpful shipping assistant AI. You help users with:
            - Getting shipping quotes and rates
            - Tracking packages
            - Explaining shipping options and services
            - Answering questions about FedEx services
            - General shipping and logistics advice
            
            Be friendly, professional, and helpful. If you need specific information like addresses, weights, or tracking numbers, ask the user for those details."""
        }
    
    def initialize_connection(self) -> tuple[bool, str]:
        """
        Initialize connection to OpenAI API
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.api_key:
                return False, "OpenAI API key not found in environment variables"
            
            # Initialize the OpenAI client
            self.client = openai.OpenAI(api_key=self.api_key)
            
            # Test the connection with a simple request
            test_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a test assistant."},
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=10
            )
            
            return True, "Successfully connected to OpenAI API"
            
        except Exception as e:
            return False, f"Failed to connect to OpenAI API: {str(e)}"
    
    def send_message(self, message: str, conversation_history: List[Dict] = None) -> str:
        """
        Send a message to OpenAI and get a response
        
        Args:
            message: User's message
            conversation_history: Previous conversation messages
            
        Returns:
            AI response as string
        """
        try:
            if not self.client:
                return "Error: OpenAI client not initialized. Please check your connection."
            
            # Build messages list
            messages = [self.system_message]
            
            # Add conversation history if provided
            if conversation_history:
                # Only include the last 10 messages to stay within token limits
                recent_history = conversation_history[-10:]
                for msg in recent_history:
                    if msg["role"] in ["user", "assistant"]:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            return response.choices[0].message.content.strip()
            
        except openai.RateLimitError:
            return "I'm currently experiencing high demand. Please try again in a moment."
        except openai.APIError as e:
            return f"I'm having trouble connecting right now. Please try again later. (Error: {str(e)})"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
    
    def set_model(self, model: str):
        """
        Set the OpenAI model to use
        
        Args:
            model: Model name (e.g., 'gpt-3.5-turbo', 'gpt-4')
        """
        self.model = model
    
    def update_system_message(self, system_content: str):
        """
        Update the system message for the AI assistant
        
        Args:
            system_content: New system message content
        """
        self.system_message["content"] = system_content
