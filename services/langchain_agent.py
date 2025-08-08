"""
LangChain-powered OpenAI Agent with FedEx Tool Calling
Enhanced AI agent that can directly call FedEx API for shipping quotes
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory

from .fedex_tool import fedex_single_tool, fedex_multi_tool

# Load environment variables
load_dotenv()


class LangChainFedExAgent:
    def __init__(self):
        """Initialize the LangChain agent with FedEx tools"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.llm = None
        self.agent_executor = None
        self.memory = None
        self.model = "gpt-3.5-turbo"
        
        # System prompt for the shipping assistant
        self.system_prompt = """You are an expert AI shipping assistant with access to live FedEx API data. 
        You help users with shipping quotes, package tracking guidance, and logistics advice.

        IMPORTANT CAPABILITIES:
        - You can get REAL shipping quotes from FedEx using live API data
        - You have access to current FedEx rates and transit times
        - You can compare different FedEx services for users

        TOOLS AVAILABLE:
        1. get_fedex_shipping_quote: Get a quote for a specific FedEx service
        2. get_fedex_all_services: Get quotes for ALL FedEx services to compare options

        WHEN TO USE TOOLS:
        - User asks for shipping rates, costs, or quotes
        - User wants to compare shipping options
        - User provides origin/destination addresses and package details
        - User asks "how much does it cost to ship..."

        REQUIRED INFORMATION FOR QUOTES:
        - Origin: city, state, postal code
        - Destination: city, state, postal code  
        - Package weight (in pounds)
        - Package dimensions (length, width, height in inches) - use 12x12x12 as default if not provided

        CONVERSATION STYLE:
        - Be helpful and professional
        - Ask for missing information politely
        - Explain shipping options clearly
        - Provide context about delivery times
        - Suggest the best service based on user needs (speed vs cost)

        EXAMPLE INTERACTIONS:
        User: "How much to ship a 5lb package from Los Angeles, CA to Atlanta, GA?"
        You: I'll get you current FedEx shipping rates for that. Let me check all available services for you.
        [Use get_fedex_all_services tool]

        User: "I need overnight shipping from 90210 to 30309"
        You: I can help with overnight shipping options. What's the weight and dimensions of your package?
        [Get details, then use tools]

        Remember: Always use the tools when users ask for shipping quotes - don't provide estimated prices without calling the API!
        """
    
    def initialize_connection(self) -> tuple[bool, str]:
        """Initialize the LangChain agent with tools"""
        try:
            if not self.api_key:
                return False, "OpenAI API key not found in environment variables"
            
            # Initialize the LLM
            self.llm = ChatOpenAI(
                api_key=self.api_key,
                model=self.model,
                temperature=0.7
            )
            
            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            # Initialize memory
            self.memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                k=10  # Keep last 10 exchanges
            )
            
            # Create the agent with tools
            tools = [fedex_single_tool, fedex_multi_tool]
            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=tools,
                prompt=prompt
            )
            
            # Create the agent executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                memory=self.memory,
                verbose=False,  # Set to True for debugging
                handle_parsing_errors=True,
                max_iterations=3
            )
            
            # Test the connection
            test_response = self.agent_executor.invoke({
                "input": "Hello, I'm testing the connection."
            })
            
            return True, "Successfully connected to OpenAI with FedEx tools enabled"
            
        except Exception as e:
            return False, f"Failed to initialize LangChain agent: {str(e)}"
    
    def send_message(self, message: str, conversation_history: List[Dict] = None) -> str:
        """
        Send a message to the LangChain agent
        
        Args:
            message: User's message
            conversation_history: Previous conversation (optional, memory handles this)
            
        Returns:
            AI response as string
        """
        try:
            if not self.agent_executor:
                return "Error: Agent not initialized. Please check your connection."
            
            # The agent executor handles the conversation through memory
            response = self.agent_executor.invoke({
                "input": message
            })
            
            return response["output"]
            
        except Exception as e:
            return f"Error processing your request: {str(e)}"
    
    def set_model(self, model: str):
        """
        Set the OpenAI model to use
        
        Args:
            model: Model name (e.g., 'gpt-3.5-turbo', 'gpt-4')
        """
        self.model = model
        if self.llm:
            self.llm.model_name = model
    
    def clear_memory(self):
        """Clear the conversation memory"""
        if self.memory:
            self.memory.clear()
    
    def get_memory_summary(self) -> str:
        """Get a summary of the current conversation memory"""
        if self.memory and hasattr(self.memory, 'chat_memory'):
            messages = self.memory.chat_memory.messages
            return f"Conversation has {len(messages)} messages in memory"
        return "No conversation memory available"
