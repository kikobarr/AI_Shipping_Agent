import boto3
import os
from dotenv import load_dotenv

load_dotenv()

class AWSAgentConnector:
    def __init__(self):
        self.agent_id = "3XVI4HOXHU"
        self.agent_alias_id = "CLNNKMUSBC"
        self.region = os.getenv("AWS_REGION", "us-west-2")
        self.runtime_client = boto3.client(
            "bedrock-agent-runtime",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        )

    def initialize_connection(self):
        # You can still return a result if you want UI feedback
        try:
            return True, "Successfully loaded credentials from .env"
        except Exception as e:
            return False, f"Failed to initialize: {str(e)}"

    def send_message(self, prompt, session_id):
        response = self.runtime_client.invoke_agent(
            agentId=self.agent_id,
            agentAliasId=self.agent_alias_id,
            sessionId=session_id,
            inputText=prompt,
        )
        completion = ""
        for event in response.get("completion", []):
            chunk = event["chunk"]
            completion += chunk["bytes"].decode()
        return completion
