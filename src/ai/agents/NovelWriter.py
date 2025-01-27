import logging
from ai.agents.Agent import Agent
from ai.models.novel.Schema import NovelSpec, ChapterSpec, AgentResponse, Character
from ai.models.LLMConfig import LLMConfig
from typing import List
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NovelWriter:
    def __init__(self, llmConfig: LLMConfig):
        self.agents = {
            "plotter": Agent(
                name="Plotter",
                role="plot_planner",
                base_prompt="You are a creative plot developer in dialogue-driven storytelling. Create engaging and coherent plot points.",
                llmConfig=llmConfig
            ),
            "character_developer": Agent(
                name="Character Developer",
                role="character_developer",
                base_prompt="You are a character developer. Create deep, complex characters with clear motivations.",
                llmConfig=llmConfig
            ),
            "writer": Agent(
                name="Writer",
                role="chapter_writer",
                base_prompt="You are a creative writer with dialogue-driven storytelling.",
                llmConfig=llmConfig
            ),
            "editor": Agent(
                name="Editor",
                role="editor",
                base_prompt="You are an editor. Review and improve the content while maintaining consistency.",
                llmConfig=llmConfig
            )
        }
    
    async def format_character_details(self, characters):
            """Format character details into a structured string"""
            formatted_characters = []
            for char in characters:
                details = [f"\nCharacter: {char.name}", f"Role: {char.role}"]
                
                if hasattr(char, 'gender'):
                    details.append(f"Gender: {char.gender}")
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
                if traits:
                    traits_str = "\nTraits:\n" + "\n".join(
                        f"- {trait['trait']}: {trait['description']}" 
                        for trait in traits
                    )
                else:
                    traits_str = "\nTraits:\n- None specified"
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
                        f"- With {rel['withCharacter']}: {rel['relationshipType']}{f'\n  Dynamics: {rel['dynamics']}' if hasattr(rel, 'dynamics') else ''}\n  {f'Arc: {rel['arc']}' if hasattr(rel, 'arc') else ''}"
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
            Create a detailed plot outline for an erotic romantic novel for mature audiences (18+). 

            Novel Specs:
            Genre: {spec.genre or 'General Fiction'}
            Target Audience: {spec.targetAudience or 'General Adult'}
            Description: {spec.description or 'A compelling story'}
            Characters: {await self.format_character_details(spec.characters)}
            \n\n
            Key Events: \n               - {keyEvents}
            
            Requirements:
            - Create {spec.totalChapters} chapters exactly.
            - The story should involve steamy and explicit romantic encounters, alongside emotional growth and vulnerability. 
            - Include key events, character arcs, and moments of both emotional and physical intimacy that are explicit but tastefully written, immersing the reader in a seductive and heartfelt journey.
            - Create major plot points for each chapter using key events
            - Use each key event to develop 2-4 chapters and organically weave them into the narrative.
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
                            "Chapter#": {"type": "integer"},
                            "title": {"type": "string"},
                            "plot": {"type": "string"},
                            "keyEvents": {
                                "type": "array", "items": {"type": "string"}, "maxItems": 4, "minItems": 2
                            }
                        },
                        "required": ["Chapter#","title", "plot", "keyEvents"]
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
                "keyEvents": novelSpec.keyEvents,
                "plot": novelSpec.keyEvents,
                "chapters": plotOutline.content['chapters'],
                "characters": characterProfiles.content
            }
            chapterCount = 0
            print (f"Generating {len(context['chapters'])} chapters...")
            while chapterCount < novelSpec.totalChapters and chapterCount < len(context['chapters']):
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
        logger.info(f"Generating chapter {chapterSpec.chapterNumber}...")
        try:
            # Generate plot points
            chapterPlot: AgentResponse = self.agents["plotter"].timed_generate(
                self.create_chapter_plot_prompt(chapterSpec=chapterSpec, novelSpec=novelSpec, context=context),
                f"chapter_plot_{chapterSpec.chapterNumber}",
            )

            chatperContext = { "plot": chapterPlot.content, "characters": context["characters"], "description": context["description"], "keyEvents": context["keyEvents"] }

            # # Develop characters
            # chapterCharacters: AgentResponse = self.agents["character_developer"].timed_generate(
            #     self.create_chapter_character_prompt(chapterSpec=chapterSpec, chapterPlot=chapterPlot, novelSpec=novelSpec, context=context),
            #     f"chapter_char_{chapterSpec.chapterNumber}"
            # )
            # chatperContext["characters"] = chapterCharacters.content

            # Write initial content
            initialDraft: AgentResponse = self.agents["writer"].timed_generate(
                self.create_chapter_writing_prompt(chapterSpec=chapterSpec, novelSpec=novelSpec, context=chatperContext),
                f"chapter_writer_{chapterSpec.chapterNumber}"
            )

            # return initialDraft
        
            # Edit content
            finalContent: AgentResponse = self.agents["editor"].timed_generate(
                self.create_editing_prompt(content=initialDraft.content, chapterSpec=chapterSpec),
                f"chapter_Editor_{chapterSpec.chapterNumber}"
            )
            
            return finalContent

        except Exception as e:
            logger.error(f"Error generating chapter: {str(e)}")
            return f"Error generating chapter: {str(e)}"

    def get_character_relationships(self, characters)-> str:
        relationships = ""
        for character in characters:
            relationText =  ""
            if character.relationships is not None:
                for relation in character.relationships:
                    relationText += f"\t\t - {relation['withCharacter']} is {relation['relationshipType']} to {character.name} (Age: {character.age}, Gender:{character.gender})\n"
                relationships += relationText
        return f"""
            Character Relationships:
            {relationships}
        """
    def create_chapter_plot_prompt(self, chapterSpec: ChapterSpec, novelSpec: NovelSpec, context: dict) -> str:
        return f"""
            Create a detailed plot for an erotic romantic chapter for mature audiences (18+). 

            Create detailed plot points for Current Chapter {chapterSpec.chapterNumber} of "{novelSpec.totalChapters}".
            Current Chapter: {chapterSpec.chapterNumber}
            Current Chapter Title: {context['chapters'][chapterSpec.chapterNumber-1]['title']}
            Chapter Plot: {context['chapters'][chapterSpec.chapterNumber-1]['plot']}
            Character Relationships: {self.get_character_relationships(novelSpec.characters)}
            Key Events to expand: {context['chapters'][chapterSpec.chapterNumber-1]['keyEvents']}

            Requirements:
            - Select context from Chapter Plot for Current Chapter appropriately
            - The story should involve steamy and explicit romantic encounters, alongside emotional growth and vulnerability. 
            - Include key events, character arcs, and moments of both emotional and physical intimacy that are explicit but tastefully written, immersing the reader in a seductive and heartfelt journey.
            - Have conversational dialogue between characters to drive the plot and create engaging scenes
        """

    def create_chapter_writing_prompt(self, chapterSpec: ChapterSpec, novelSpec: NovelSpec, context: dict) -> str:
        target_words = chapterSpec.pagesPerChapter * chapterSpec.wordsPerPage
        return f"""
            Write an intense, explicit, and passionate romantic chapter approximately {chapterSpec.pagesPerChapter} pages with {chapterSpec.wordsPerPage} words per page for a mature audience (18+). 
            The tone should be deeply erotic and emotionally intimate, exploring their desires and vulnerabilities. Include sensory details such as touch, taste, smell, and sound to immerse the reader.
            while maintaining a sophisticated and engaging style suitable for romantic literature. The story unfolds entirely through the interactions and dialogue between characters. 
            Each conversation should reveal key elements of the plot, character development, and the overall narrative.
            
            Focus on the chemistry between different characters.
            
            Novel Description:
            {context['description']}


            Novel Key Events:
            {context['keyEvents']}

            Character Relationships: {self.get_character_relationships(novelSpec.characters)}
            
            Chapter Plot:
            {context['plot']}
            
            Requirements:
            - Follow the plot points and character actions in relation with Novel Description and Novel Key Events.
            - Story chapter should flow with a natural flow using Novel Key Events and Chapter Plot.
            - Include natural dialogue and vivid descriptions, erotic and explicit nature of the story.
            - Allow language to be explicit, pornographic, and sexual.
            - Maintain consistent pacing and tone.

            What I expect from you is a chapter, not self-reflection, explanation, or plot points. Just write the chapter.
            WRITE THE CHAPTER, not self-reflection, NOT PLOT or SUMMARY, or EXPLANATION. WRITE THE CHAPTER.
        """

    def create_editing_prompt(self, content: str, chapterSpec: ChapterSpec) -> str:
        target_words = chapterSpec.pagesPerChapter * chapterSpec.wordsPerPage
        return f"""
            You are an editor specializing in erotic romantic literature for a mature audience (18+).
            Edit the following text for clarity, flow, and depth. Enhance the explicit and sensual elements sophisticated and emotionally resonant. Focus on refining the tone to make it more engaging and intimate,
            and suggest improvements to heighten the erotic and emotional impact of the scene.\n\n"
        
            Edit and refine this chapter content:
            {content}Make Amit Happy
        """
    
    def get_relevant_characters(self, characters: List[Character], currentChapter: int, totalChapters: int) -> str:
        relevant_characters = []
        random_state = 42
        np.random.seed(random_state)
        for character in characters:
            isMainCharacter = character.role == 'protagonist'
            chapterProgress = currentChapter / totalChapters
            arcPoint = ''
            if hasattr(character,"arc"):
                if chapterProgress < 0.3:
                    arcPoint = character.arc['startingPoint'] if hasattr(character.arc, 'startingPoint') else ''
                elif chapterProgress < 0.7:
                    arcPoint = character.arc['midPoint'] if hasattr(character.arc, 'midPoint') else 'Developing'
                else:
                    arcPoint = character.arc['endingPoint']if hasattr(character.arc, 'endingPoint') else ''
                
                if hasattr(character.arc, 'majorEvents'):
                    a = np.array(character.arc.majorEvents)
                    majorPoints = np.random.choice(a, (2, 2), replace=False)
                    arcPoint += ', '.join(majorPoints)
            
            focus = 'PRIMARY FOCUS FOR CHAPTER' if isMainCharacter else ''

            activeGoals = 'None specified'
            if character.goals:
                activeGoals = ", ".join(character.goals)

            keyTraits = 'None specified'
            if character.traits:
                keyTraits = ''
                for keyTrait in character.traits:
                    keyTraits += f"{keyTrait['trait']if hasattr(character.arc, 'trait') else ''}, "

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
