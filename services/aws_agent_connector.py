import boto3
import time

class AWSAgentConnector:
    def __init__(self):
        self.bedrock_agent = None
        self.session = None
        self.agent_id = None
        self.agent_alias_id = None

    def initialize_connection(self, aws_access_key, aws_secret_key, region, agent_id, agent_alias_id):
        """
        Initialize a connection to AWS Bedrock Agent Runtime.
        """
        try:
            self.session = boto3.Session(
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region
            )
            self.bedrock_agent = self.session.client('bedrock-agent-runtime')
            self.agent_id = agent_id
            self.agent_alias_id = agent_alias_id

            # Test connection
            test_session_id = f"test-session-{int(time.time())}"
            self.bedrock_agent.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=test_session_id,
                inputText="Hello, are you working?"
            )
            return True, "Successfully connected to AWS Bedrock Agent!"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def send_message(self, message, session_id):
        """
        Send a message to the AWS Bedrock Agent and return its response.
        """
        if not self.bedrock_agent:
            return "Error: Agent not connected. Please configure connection first."

        try:
            response = self.bedrock_agent.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=session_id,
                inputText=message
            )

            # Extract and decode response (works for streaming-style responses)
            response_text = ""
            if 'completion' in response:
                for event in response['completion']:
                    if 'chunk' in event and 'bytes' in event['chunk']:
                        response_text += event['chunk']['bytes'].decode('utf-8')

            return response_text or "Agent processed your request successfully."

        except Exception as e:
            return f"Error communicating with agent: {str(e)}"