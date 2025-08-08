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
        - Origin: COMPLETE street address, city, state, postal code
        - Destination: COMPLETE street address, city, state, postal code  
        - Package weight (in pounds)
        - Package dimensions (length, width, height in inches) - use 12x12x12 as default if not provided

        CRITICAL: Always ask for COMPLETE STREET ADDRESSES, not just city/state/zip!
        Street-level addresses provide more accurate FedEx pricing.

        Examples of COMPLETE addresses:
        ✅ GOOD: "913 Paseo Camarillo, Camarillo, CA 93010"
        ✅ GOOD: "1 Harpst St, Arcata, CA 95521"
        ❌ BAD: "Camarillo, CA 93010" (missing street address)
        ❌ BAD: "Los Angeles, CA" (missing street and zip)

        CONVERSATION STYLE:
        - Be helpful and professional
        - Ask for missing information politely, especially COMPLETE addresses
        - Explain shipping options clearly
        - Provide context about delivery times
        - Suggest the best service based on user needs (speed vs cost)

        EXAMPLE INTERACTIONS:
        User: "How much to ship a 5lb package from Los Angeles to Atlanta?"
        You: I'd be happy to get you FedEx shipping rates! To provide accurate quotes, I need the complete street addresses. Could you please provide:
        - Origin: Complete street address, city, state, zip (e.g., "123 Main St, Los Angeles, CA 90210")
        - Destination: Complete street address, city, state, zip (e.g., "456 Oak Ave, Atlanta, GA 30309")
        - Package dimensions (length x width x height in inches)

        User: "I need overnight shipping from 913 Paseo Camarillo, Camarillo, CA 93010 to 1 Harpst St, Arcata, CA 95521"
        You: Perfect! I have the complete addresses. What's the weight and dimensions of your package?
        [Get details, then use tools]

        Remember: Always use the tools when users ask for shipping quotes - don't provide estimated prices without calling the API!
        Always insist on complete street addresses for accurate pricing!
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
            
            # Create the agent executor with debugging enabled
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                memory=self.memory,
                verbose=True,  # Enable verbose logging for debugging
                handle_parsing_errors=True,
                max_iterations=3,
                return_intermediate_steps=True  # Return tool execution details
            )
            
            # Test the connection
            test_response = self.agent_executor.invoke({
                "input": "Hello, I'm testing the connection."
            })
            
            return True, "Successfully connected to OpenAI with FedEx tools enabled"
            
        except Exception as e:
            return False, f"Failed to initialize LangChain agent: {str(e)}"
    
    def send_message(self, message: str, conversation_history: List[Dict] = None) -> tuple[str, Dict]:
        """
        Send a message to the LangChain agent
        
        Args:
            message: User's message
            conversation_history: Previous conversation (optional, memory handles this)
            
        Returns:
            tuple: (AI response as string, debug_info dict)
        """
        try:
            if not self.agent_executor:
                return "Error: Agent not initialized. Please check your connection.", {}
            
            # The agent executor handles the conversation through memory
            response = self.agent_executor.invoke({
                "input": message
            })
            
            # Extract debug information
            debug_info = {
                "tools_used": [],
                "intermediate_steps": response.get("intermediate_steps", []),
                "tool_calls_made": False
            }
            
            # Check if tools were used
            if "intermediate_steps" in response and response["intermediate_steps"]:
                debug_info["tool_calls_made"] = True
                for step in response["intermediate_steps"]:
                    if len(step) >= 2:
                        action, observation = step[0], step[1]
                        debug_info["tools_used"].append({
                            "tool": action.tool if hasattr(action, 'tool') else "unknown",
                            "input": action.tool_input if hasattr(action, 'tool_input') else {},
                            "output": str(observation)[:200] + "..." if len(str(observation)) > 200 else str(observation)
                        })
            
            return response["output"], debug_info
            
        except Exception as e:
            return f"Error processing your request: {str(e)}", {"error": str(e)}
    
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
