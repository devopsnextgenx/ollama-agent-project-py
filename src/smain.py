
import datetime
from ai.models.LLMProvider import LLMProvider
from ai.agents.SystemAgent import SystemAgent
from ai.models.novel.Schema import AgentResponse
from ai.operators.executer import process_command
import time

llmConfig = LLMProvider.create_llm_config(base_url="http://localhost:11434", model = "phi4")

systemAgent = SystemAgent(llmConfig)

EXIT_COMMANDS = ["exit", "bye", "quit"]

def processPrompt(prompt):
        start_time = time.time()
        print(datetime.datetime.now())
        response: AgentResponse = systemAgent.queryLLM(prompt)
        actionResponse = process_command(response.content)
        print(actionResponse)
        end_time = time.time()
        duration = end_time - start_time
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        print(f"System command completed in {duration:.2f} seconds.")
        print(f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")

async def main():
    exit_flag = False
    while not exit_flag:
        user_input = input("Enter your command (or 'exit','bye','quit' to quit): ")
        if EXIT_COMMANDS.__contains__(user_input):
            exit_flag = True
            continue
        
        processPrompt(user_input)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())