
import datetime
from ai.models.LLMProvider import LLMProvider
from ai.agents.SystemAgent import SystemAgent
from ai.models.novel.Schema import AgentResponse
from ai.operators.executer import process_command
import time

llmConfig = LLMProvider.create_llm_config(base_url="http://localhost:11434", model = "phi4")

systemAgent = SystemAgent(llmConfig)

async def main():
    start_time = time.time()
    print(datetime.datetime.now())
    print("Starting novel generation...")
    
    response: AgentResponse = systemAgent.queryLLM("How to check current user name")
    actionResponse = process_command(response.content)
    print(actionResponse)

    response: AgentResponse = systemAgent.queryLLM("How to get current directory name")
    actionResponse = process_command(response.content)
    print(actionResponse)

    end_time = time.time()
    duration = end_time - start_time
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    print(f"System command completed in {duration:.2f} seconds.")
    print(f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())