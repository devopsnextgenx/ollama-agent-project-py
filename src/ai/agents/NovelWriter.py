import logging
from ai.agents.Agent import Agent
from ai.models.novel.Schema import NovelSpec, ChapterSpec, AgentResponse, Character
from ai.models.LLMConfig import LLMConfig
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NovelWriter:
    def __init__(self, llmConfig: LLMConfig):
        self.agents = {
            "plotter": Agent(
                name="Plotter",
                role="plot_development",
                base_prompt="You are a creative plot developer. Create engaging and coherent plot points.",
                llmConfig=llmConfig
            ),
            "character_developer": Agent(
                name="Character Developer",
                role="character_development",
                base_prompt="You are a character developer. Create deep, complex characters with clear motivations.",
                llmConfig=llmConfig
            ),
            "writer": Agent(
                name="Writer",
                role="content_writing",
                base_prompt="You are a creative writer. Transform plot points and character details into engaging prose.",
                llmConfig=llmConfig
            ),
            "editor": Agent(
                name="Editor",
                role="editing",
                base_prompt="You are an editor. Review and improve the content while maintaining consistency.",
                llmConfig=llmConfig
            )
        }
    
    async def format_character_details(self, characters):
            """Format character details into a structured string"""
            formatted_characters = []
            for char in characters:
                details = [f"Character: {char.name}", f"Role: {char.role}"]
                
                if hasattr(char, 'age'):
                    details.append(f"Age: {char.age}")
                if hasattr(char, 'physicalDescription'):
                    details.append(f"Appearance: {char.physicalDescription}")
                if hasattr(char, 'background'):
                    details.append(f"Background: {char.background}")
                if hasattr(char, 'motivation'):
                    details.append(f"Motivation: {char.motivation}")
                
                # Goals
                goals = getattr(char, 'goals', None)
                goals_str = "\nGoals:\n" + "\n".join(f"- {goal}" for goal in goals) if goals else "- None specified"
                details.append(goals_str)
                
                # Traits
                traits = getattr(char, 'traits', None)
                traits_str = "\nTraits:\n" + "\n".join(f"- {trait['trait']}: {trait['description']}" for trait in traits) if traits else "- None specified"
                details.append(traits_str)
                
                # Character Arc
                arc = getattr(char, 'arc', None)
                if arc:
                    arc_str = f"\nCharacter Arc:\n- Starting: {getattr(arc, 'startingPoint', 'To be developed')}\n- Middle: {getattr(arc, 'midPoint', 'To be developed')}\n- Ending: {getattr(arc, 'endingPoint', 'To be developed')}"
                else:
                    arc_str = "\nCharacter Arc:\n- To be developed"
                details.append(arc_str)
                
                # Relationships
                relationships = getattr(char, 'relationships', None)
                if relationships:
                    rel_str = "\nRelationships:\n" + "\n".join(
                        f"- With {rel['withCharacter']}: {rel['relationshipType']}\n  Dynamics: {rel['dynamics']}\n  {f'Arc: {rel['arc']}' if hasattr(rel, 'arc') else ''}"
                        for rel in relationships
                    )
                else:
                    rel_str = "\nRelationships:\n- None specified"
                details.append(rel_str)
                
                formatted_characters.append("\n".join(details))
            
            return "\n\n---\n\n".join(formatted_characters)
    

    async def createNovelOutline(self, spec: NovelSpec) -> AgentResponse:
        """Create a detailed plot outline for the novel"""
        keyEvents = ''
        if spec.keyEvents is not None:
            keyEvents = '\n               - '.join(spec.keyEvents)
        prompt = f"""
            Create a detailed plot outline for a {spec.totalChapters}-chapter novel titled "{spec.title}".
            Genre: {spec.genre or 'General Fiction'}
            Target Audience: {spec.targetAudience or 'General Adult'}
            Description: {spec.description or 'A compelling story'}
            Characters: {await self.format_character_details(spec.characters)}
            key events: \n               - {keyEvents}
            
            Requirements:
            - Create {spec.totalChapters} chapters
            - Create major plot points for each chapter using key events
            - Ensure narrative arc across all {spec.totalChapters} chapters
            - Create 3 key events or turning points
            - Consider pacing and tension
        """

        responseSchema = {
            "type": "object",
            "properties": {
                "chapters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "plot": {"type": "string"},
                            "keyEvents": {
                                "type": "array", "items": {"type": "string"}, "maxItems": 3
                            }
                        },
                        "required": ["title", "plot", "keyEvents"]
                    }
                }
            },
            "required": ["chapters"]
        }
        return self.agents["plotter"].timed_generate(prompt, "novel_outline", responseSchema)

    async def createCharacterProfiles(self, spec: NovelSpec, plotOutline: AgentResponse) -> AgentResponse:
        """Create a detailed plot outline for the novel"""
        prompt = f"""
            Create character profiles for the novel "${spec.title}".
            Plot Outline: ${plotOutline.content}

            Requirements:
            - Define main and supporting characters
            - Include character motivations and arcs
            - Consider character relationships
            - Describe character clothing, appearance erotically and more feminine way
            - Plan character development across ${spec.totalChapters} chapters
        """
        return self.agents["character_developer"].timed_generate(prompt, "novel_outline")

    async def generateNovel(self, novelSpec: NovelSpec) -> str:
        """Generate a novel using all agents in sequence"""
        print("Generating novel...")
        chapterContent = []
        try:
            # Generate plot points
            plotOutline: AgentResponse = await self.createNovelOutline(novelSpec)
            characterProfiles: AgentResponse = await self.createCharacterProfiles(novelSpec, plotOutline)

            context = {
                "description": novelSpec.description,
                "plot": novelSpec.keyEvents,
                "chapters": plotOutline.content['chapters'],
                "characters": characterProfiles.content
            }
            chapterCount = 0
            while chapterCount < novelSpec.totalChapters:
                chapterSpec = ChapterSpec(
                    chapterNumber=chapterCount + 1,
                    pagesPerChapter=novelSpec.pagesPerChapter,
                    wordsPerPage=novelSpec.wordsPerPage,
                    title=f"Chapter {chapterCount + 1}",
                    description=f"Part {chapterCount + 1} of {novelSpec.totalChapters}"
                )
                chapter: AgentResponse = self.generateChapter(chapterSpec, novelSpec, context)
                chapterCount += 1
                chapterContent.append(chapter.content)

        except Exception as e:
            logger.error(f"Error generating chapter loop: {str(e)}")
        
        return chapterContent
        
    def generateChapter(self, chapterSpec: ChapterSpec, novelSpec: NovelSpec, context) -> AgentResponse:
        """Generate a chapter using all agents in sequence"""
        logger.debug(f"=====================================================================")
        logger.debug(f"Generating chapter {chapterSpec.chapterNumber}...")
        try:
            # Generate plot points
            chapterPlot: AgentResponse = self.agents["plotter"].timed_generate(
                self.create_chapter_plot_prompt(chapterSpec=chapterSpec, novelSpec=novelSpec, context=context),
                f"chapter_plot_{chapterSpec.chapterNumber}",
            )

            chatperContext = { "plot": chapterPlot.content, "characters": context["characters"] }

            # Develop characters
            chapterCharacters: AgentResponse = self.agents["character_developer"].timed_generate(
                self.create_chapter_character_prompt(chapterSpec=chapterSpec, chapterPlot=chapterPlot, novelSpec=novelSpec, context=context),
                f"chapter_char_{chapterSpec.chapterNumber}"
            )
            chatperContext["characters"] = chapterCharacters.content

            # Write initial content
            initialDraft: AgentResponse = self.agents["writer"].timed_generate(
                self.create_chapter_writing_prompt(chapterSpec=chapterSpec, novelSpec=novelSpec, context=chatperContext),
                f"chapter_writer_{chapterSpec.chapterNumber}"
            )

            # Edit content
            finalContent: AgentResponse = self.agents["editor"].timed_generate(
                self.create_editing_prompt(content=initialDraft.content, chapterSpec=chapterSpec),
                f"chapter_Editor_{chapterSpec.chapterNumber}"
            )

            return finalContent

        except Exception as e:
            logger.error(f"Error generating chapter: {str(e)}")
            return f"Error generating chapter: {str(e)}"

    def create_chapter_plot_prompt(self, chapterSpec: ChapterSpec, novelSpec: NovelSpec, context: dict) -> str:
        return f"""
            Create detailed plot points for Current Chapter {chapterSpec.chapterNumber} of "{novelSpec.totalChapters}".
            Current Chapter: {chapterSpec.chapterNumber}
            Current Chapter Title: {context['chapters'][chapterSpec.chapterNumber-1]['title']}
            Overall Plot Description: {context['description']}
            Overall Plot: {context['plot']}
            Chapter Plot: {context['chapters'][chapterSpec.chapterNumber-1]['plot']}
            Key Events to expand: {context['chapters'][chapterSpec.chapterNumber-1]['keyEvents']}

            Requirements:
            - Select context from Chapter Plot for Current Chapter appropriately
            - Create specific plot points for selected context in above step while considering the overall plot
            - Have conversational dialogue between characters to drive the plot and create engaging scenes
            - Do not drop any plot points associated with current chapter
            - Maintain consistency with overall story and plot points
            - Target length: {chapterSpec.pagesPerChapter} pages
            - Consider chapter's position ({chapterSpec.chapterNumber} of {novelSpec.totalChapters})
        """

    def create_chapter_writing_prompt(self, chapterSpec: ChapterSpec, novelSpec: NovelSpec, context: dict) -> str:
        target_words = chapterSpec.pagesPerChapter * chapterSpec.wordsPerPage
        return f"""
            Write Chapter {chapterSpec.chapterNumber} of "{novelSpec.totalChapters}".
            Plot Points: {context['plot']}
            Character Actions: {context['characters']}
            
            Requirements:
            - Content is targeted for adults and mature audiences
            - Write approximately {chapterSpec.pagesPerChapter} pages with {chapterSpec.wordsPerPage} words per page
            - Follow the plot points and character actions
            - Keep content sensual and engaging, erotic and exciting, romatic and passionate, sexual and explicite
            - Include natural dialogue and vivid descriptions, erotic and explicit nature of the story
            - Maintain consistent pacing and tone
        """

    def create_editing_prompt(self, content: str, chapterSpec: ChapterSpec) -> str:
        target_words = chapterSpec.pagesPerChapter * chapterSpec.wordsPerPage
        return f"""
            Edit and refine this chapter content:
            
            {content}
            
            Requirements:
            - Content is targeted for adults and mature audiences
            - Ensure consistent style and tone
            - Check for proper pacing
            - Maintain target length approximately {target_words} words per page
            - Maintain target length ({chapterSpec.pagesPerChapter} pages)
            - Polish dialogue and descriptions
            - Enhance dramatic tension
        """
    
    def get_relevant_characters(self, characters: List[Character], currentChapter: int, totalChapters: int) -> str:
        relevant_characters = []

        for character in characters:
            isMainCharacter = character.role == 'protagonist'
            chapterProgress = currentChapter / totalChapters
            arcPoint = ''
            if character.arc:
                if chapterProgress < 0.3:
                    arcPoint = character.arc['startingPoint'] if hasattr(character.arc, 'startingPoint') else ''
                elif chapterProgress < 0.7:
                    arcPoint = character.arc['midPoint'] if hasattr(character.arc, 'midPoint') else 'Developing'
                else:
                    arcPoint = character.arc['endingPoint']if hasattr(character.arc, 'endingPoint') else ''
            
            focus = 'PRIMARY FOCUS FOR CHAPTER' if isMainCharacter else ''

            activeGoals = 'None specified'
            if character.goals:
                activeGoals = ", ".join(character.goals)

            keyTraits = 'None specified'
            if character.traits:
                keyTraits = ''
                for keyTrait in character.traits:
                    keyTraits += f"{keyTrait['trait']}, "

            relevant_characters.append(
            f"""
            Character: {character.name} ({character.role})
            Current Arc Point: {arcPoint}
            Active Goals: {activeGoals}
            Key Traits: {keyTraits}
            {focus}
            """)

        return "\n".join(relevant_characters)
            

    def create_chapter_character_prompt(self, chapterSpec: ChapterSpec, chapterPlot: AgentResponse, 
                                      novelSpec: NovelSpec, context: dict) -> str:
        relevant_characters = self.get_relevant_characters(
            novelSpec.characters,
            chapterSpec.chapterNumber,
            novelSpec.totalChapters
        )
        return f"""
        Develop character actions and development for Chapter {chapterSpec.chapterNumber}.
        
        Relevant Characters for this chapter:
        {relevant_characters}
        
        Chapter Plot: {chapterPlot.content}
        
        Requirements:
        - Focus on the main character ({novelSpec.mainCharacterName})
        - Include meaningful interactions between characters
        - Add more descriptions to clothing of female characters and explicit descriptions of their bodies
        - Include descriptions for effeminiate characters
        - Show character growth and development
        - Maintain consistent character voices and behaviors
        - Ensure actions align with established traits and motivations
        - Develop relationships according to their defined dynamics
    """
