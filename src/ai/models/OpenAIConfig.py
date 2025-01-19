
from dataclasses import dataclass
from typing import Optional
from .SafetyConfig import SafetyConfig

@dataclass
class OpenAIConfig:
    """Configuration for OpenAI LLM models"""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[list[str]] = None
    api_key: Optional[str] = None
    organization: Optional[str] = None
    config: Optional[SafetyConfig] = None