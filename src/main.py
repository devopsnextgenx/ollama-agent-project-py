import customtkinter as ctk
import datetime
from ai.models.LLMProvider import LLMProvider
from ai.agents.NovelWriter import NovelWriter
from ai.models.novel.Schema import NovelSpec, loadNovelSpec
from ai.ui.novelSpecUi import App
import time

llmConfig = LLMProvider.create_llm_config(base_url="http://localhost:11434", model = "jaahas/tiger-gemma-v2:latest")

novelWriter = NovelWriter(llmConfig)

async def main():
    start_time = time.time()
    print(datetime.datetime.now())
    print("Starting novel generation...")
    
    # ctk.set_appearance_mode("dark")
    # app = App()
    # app.mainloop()

    novelSpec: NovelSpec =loadNovelSpec("./contents/.novel-fspec.yml")
    chapters = await novelWriter.generateNovel(novelSpec)

    # # Output the results
    novel_content = ''
    for index, chapter in enumerate(chapters):
        novel_content += f"\n--- Chapter {index + 1} ---\n"
        novel_content += chapter
    
    with open(f"{llmConfig.modelStore}/novel.md", "w") as f:
        f.write(novel_content)
    
    end_time = time.time()
    duration = end_time - start_time
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    print(f"Novel generation completed in {duration:.2f} seconds.")
    print(f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())