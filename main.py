import boto3
import uuid
import asyncio
import logging
from dotenv import load_dotenv
import os

load_dotenv()

client = boto3.client("bedrock-agent-runtime")

REGION = "us-west-2"

class BedrockAgentInvoker:
    def __init__(self, agent_id, agent_alias_id):
        self.agent_id = agent_id
        self.agent_alias_id = agent_alias_id
        self.runtime_client = boto3.client("bedrock-agent-runtime", region_name=REGION)

    def chat(self):
        print("=" * 60)
        print("Chat session with Bedrock Agent started.")
        print("Type 'exit' to quit.")
        print("=" * 60)

        session_id = uuid.uuid4().hex

        while True:
            prompt = input("Prompt: ").strip()
            if prompt.lower() == "exit":
                print("Exiting chat.")
                break
            response = asyncio.run(self._invoke_agent(prompt, session_id))
            print(f"Agent: {response}")

    async def _invoke_agent(self, prompt, session_id):
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    AGENT_ID = "3XVI4HOXHU"
    AGENT_ALIAS_ID = "CLNNKMUSBC"

    agent = BedrockAgentInvoker(agent_id=AGENT_ID, agent_alias_id=AGENT_ALIAS_ID)
    agent.chat()
