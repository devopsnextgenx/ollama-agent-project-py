import time
import logging
from typing import List
from langchain_ollama import OllamaLLM
from ai.models import LLMConfig
from ai.models.novel.Schema import AgentResponse
from typing import Dict, Any, Optional
import requests
import json

from ollama import generate as ollama_generate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, name: str, role: str, base_prompt: str, llmConfig: LLMConfig):
        self.name = name
        self.role = role
        self.base_prompt = base_prompt
        self.memory: List[str] = []
        self.llmConfig: LLMConfig = llmConfig

    def timed_generate(self, prompt: str, file_name: str, responseSchema: Dict[str, Any] = None) -> AgentResponse:
        start_time = time.time()
        logger.info(f"{self.name} agent generating content...")
        
        response: AgentResponse = self.generate_structured(prompt, responseSchema) if responseSchema is not None else self.generate(prompt)
        
        with open(f"{self.llmConfig.modelStore}/{file_name}-{self.name}.md", 'w') as f:
            f.write(response.content if responseSchema is None else json.dumps(response.content, indent=4))
            
        logger.info(f"{self.name} agent generated content.")
        
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        logger.info(f"{self.name} agent generated content in {elapsed_time:.2f}ms.")
        
        return response

    def generate(self, prompt: str, responseSchema: Dict[str, Any] = None) -> AgentResponse:
        try:
            full_prompt = f"{self.base_prompt}\n\nRole: {self.role}\n\n{prompt}"
            
            self.llm = OllamaLLM(
                model=self.llmConfig.model,
                base_url=self.llmConfig.base_url,
                temperature=self.llmConfig.openAIConfig.temperature,
                max_tokens=8000
            )

            content = self.llm.invoke(full_prompt)
            
            self.memory.append(content)

            response = AgentResponse(content=content, metadata={"agent": self.name, "role": self.role, "json": False})
            return response
            
        except Exception as error:
            logger.error(f"Error in {self.name} agent:", error)
            raise Exception(f"{self.name} agent failed to generate content")

    def generate_structured(self, prompt: str, responseSchema: Dict[str, Any] = None) -> AgentResponse:
        """Generate content with structured response"""
        full_prompt = f"{self.base_prompt}\n\nRole: {self.role}\n\n{prompt}"
        response = ollama_generate(
                        model=self.llmConfig.model,
                        prompt=full_prompt,
                        format=responseSchema,
                        stream=False,
                        options={
                            "max_tokens": 8000,  # Set the max tokens
                            "temperature": self.llmConfig.openAIConfig.temperature,  # Optional: creativity level
                        }
                    )

        self.memory.append(response.response)

        response = AgentResponse(content=json.loads(response.response), metadata={"agent": self.name, "role": self.role, "json": True})
        return response

    def update_safety_config(self, **kwargs):
        """Update safety configuration with new settings"""
        for key, value in kwargs.items():
            if hasattr(self.llmConfig.openAIConfig.config, key):
                setattr(self.llmConfig.openAIConfig.config, key, value)
            else:
                logger.warning(f"Unknown safety config parameter: {key}")

    def update_open_ai_config(self, **kwargs):
        """Update OpenAI configuration with new settings"""
        for key, value in kwargs.items():
            if hasattr(self.llmConfig.openAIConfig, key):
                setattr(self.llmConfig.openAIConfig, key, value)
            else:
                logger.warning(f"Unknown OpenAI config parameter: {key}")