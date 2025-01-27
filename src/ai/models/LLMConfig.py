from dataclasses import dataclass
from .OpenAIConfig import OpenAIConfig

class LLMConfig:
    base_url: str = "http://localhost:11434"
    model: str = "phi4"
    openAIConfig: OpenAIConfig = OpenAIConfig()
    modelStore: str = 'x'
    def __init__(self, base_url: str, model: str, openAIConfig: OpenAIConfig, modelStore: str = 'x'):
        self.model = model
        self.modelStore = modelStore
        self.base_url = base_url
        if openAIConfig is None:
            self.openAIConfig = OpenAIConfig()
        else:
            self.openAIConfig = openAIConfig
