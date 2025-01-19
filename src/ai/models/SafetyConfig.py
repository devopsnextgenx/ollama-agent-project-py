from typing import List
from dataclasses import dataclass

@dataclass
class SafetyConfig:
    allow_adult_content: bool = False
    allow_explicit_content: bool = False
    allow_violence: bool = False
    allow_controversial_topics: bool = False
    allow_sexual_content: bool = False
    content_rating: str = "PG"  # Options: G, PG, PG-13, R
    sensitive_topics: List[str] = None
    
    def to_prompt_guidelines(self) -> str:
        guidelines = ["Please write content following these guidelines:"]
        
        if  not self.allow_adult_content:
            guidelines.append("- Avoid adult content")
        if not self.allow_explicit_content:
            guidelines.append("- Avoid explicit or adult content")
        if not self.allow_violence:
            guidelines.append("- Avoid graphic violence")
        if not self.allow_controversial_topics:
            guidelines.append("- Avoid controversial topics")
        if not self.allow_sexual_content:
            guidelines.append("- Avoid sexual content")
        guidelines.append(f"- Keep content appropriate for {self.content_rating} rating")
        
        if self.sensitive_topics:
            topics = ", ".join(self.sensitive_topics)
            guidelines.append(f"- Avoid the following topics: {topics}")

        return "\n".join(guidelines)
