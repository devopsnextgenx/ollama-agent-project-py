import logging
from ai.agents.Agent import Agent
from ai.models.LLMConfig import LLMConfig
from typing import List
from ai.models.novel.Schema import AgentResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemAgent:
    def __init__(self, llmConfig: LLMConfig):
        self.agents = {
            "egor": Agent(
                name="egor",
                role="System Agent",
                base_prompt="You are a system agent. You are able to expose the system tools and capabilities to the LLM, and act on LLM outputs.",
                llmConfig=llmConfig
            )
        }

    def queryLLM(self, prompt: str) -> str:
        """Query the LLM with a prompt and return the response"""

        responseSchema = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["run_shell_command"]
                },
                "command": {
                    "type": "string",
                    "enum": ["ls", "du", "df", "whoami", "pwd"]

                }
            },
            "required": ["action", "command"]
        }
        agentPrompt = f"""
            You are a system agent. Use tools and capabilities provided by agent to generate a response.
            Tools and capabilities:
            Actions:
                - run_shell_command: Run a shell command.
            commands:
                - run_shell_command: Run a shell command.
                - whoami: Get the current user name.
                - ls: List files in the current directory. ls -ltr /home
                - du: Display disk usage.
                - df: Display disk space.
                - pwd: Print the current working directory.

            Prompt: {prompt}
        """

        action_response: AgentResponse  = self.agents['egor'].timed_generate(agentPrompt, "action_response", responseSchema)
        print(action_response)

        return action_response