import yaml
import logging
from typing import List, Optional, Dict, Union, Any
from dataclasses import dataclass
from ai.models.SafetyConfig import SafetyConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GenerationConfig:
    wordsPerPage: int
    model: str
    temperature: Optional[float] = None
    maxTokens: Optional[int] = None
    safetyConfig: Optional[SafetyConfig] = None

@dataclass
class ChapterSpec:
    chapterNumber: int
    pagesPerChapter: int = 5
    wordsPerPage: int = 500
    title: Optional[str] = None
    description: Optional[str] = None

@dataclass
class CharacterTrait:
    trait: str
    description: str

@dataclass
class CharacterArc:
    startingPoint: Optional[str] = None
    midPoint: Optional[str] = None
    endingPoint: Optional[str] = None
    majorEvents: Optional[List[str]] = None

@dataclass
class CharacterRelationship:
    withCharacter: str
    relationshipType: str
    dynamics: Optional[str] = None
    arc: Optional[str] = None

@dataclass
class Character:
    name: str
    role: str
    age: Optional[int]
    gender: Optional[str] = ''
    background: Optional[str] = ''
    motivation: Optional[str] = ''
    traits: Optional[List[CharacterTrait]] = None
    arc: Optional[CharacterArc] = None
    relationships: Optional[List[CharacterRelationship]] = None
    physicalDescription: Optional[str] = None
    goals: Optional[List[str]] = None

@dataclass
class NovelSpec:
    title: str
    totalChapters: int
    pagesPerChapter: int
    wordsPerPage: int
    genre: str
    targetAudience: str
    mainCharacterName: str
    characters: List[Character]
    description: str
    keyEvents: Optional[List[str]] = None

    @classmethod
    def from_yaml(cls, file_path: str) -> 'NovelSpec':
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            characters = [Character(**char) for char in data['characters']]
            keyEvents = None
            if data['keyEvents']:
                keyEvents = [keyEvent for keyEvent in data['keyEvents']]
            return cls(
                title=data['title'],
                totalChapters=data['totalChapters'],
                pagesPerChapter=data['pagesPerChapter'],
                wordsPerPage=data['wordsPerPage'],
                genre=data['genre'],
                targetAudience=data['targetAudience'],
                mainCharacterName=data['mainCharacterName'],
                characters=characters,
                description=data['description'],
                keyEvents=keyEvents
            )

@dataclass
class AgentResponse:
    content: Optional[Union[str, Dict[str, Any]]] = None
    metadata: Optional[Dict] = None
    
def loadNovelSpec(file_path: str = '.novel-spec.yml') -> NovelSpec:
    return NovelSpec.from_yaml(file_path)