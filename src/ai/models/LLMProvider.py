
from enum import Enum
from typing import Optional
from ai.models.OpenAIConfig import OpenAIConfig
from ai.models.LLMConfig import LLMConfig
from ai.models.SafetyConfig import SafetyConfig
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider:
    @staticmethod
    def get_default_safety_config(**kwargs) -> SafetyConfig:
        safetyConfig = SafetyConfig(
            allow_adult_content=False,
            allow_explicit_content=False,
            allow_violence=False,
            allow_controversial_topics=False,
            allow_sexual_content=False,
            content_rating="PG",
            sensitive_topics=[]
        )
        for key, value in kwargs.items():
            if hasattr(safetyConfig, key):
                setattr(safetyConfig, key, value)
            else:
                logger.warning(f"Unknown safety config parameter: {key}")
        return safetyConfig

    @staticmethod
    def create_openai_config(**kwargs) -> OpenAIConfig:
        openAIConfig = OpenAIConfig(
            temperature=0.7,
            max_tokens=None,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None,
            api_key=None,
            organization=None,
            config=LLMProvider.get_default_safety_config()
        )
        for key, value in kwargs.items():
            if hasattr(openAIConfig, key):
                setattr(openAIConfig, key, value)
            else:
                logger.warning(f"Unknown OpenAI config parameter: {key}")
        return openAIConfig

    @staticmethod
    def create_llm_config(base_url="http://localhost:11434", model = "phi4", openAIConfig = None) -> LLMConfig:
        if openAIConfig is None:
            openAIConfig = LLMProvider.create_openai_config()
        return LLMConfig(
            base_url=base_url,
            model=model,
            openAIConfig=openAIConfig
        )
