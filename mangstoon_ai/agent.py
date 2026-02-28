from google.adk.agents import Agent

from .prompts.system import MANGSTOON_DIRECTOR_INSTRUCTION
from .tools.story_engine import decompose_story
from .tools.image_gen import generate_panel
from .tools.panel_editor import edit_panel
from .tools.character import extract_character

root_agent = Agent(
    model="gemini-3.1-pro-preview",
    name="mangstoon_director",
    description="AI Webtoon Director that turns user fantasies into Korean webtoons",
    instruction=MANGSTOON_DIRECTOR_INSTRUCTION,
    tools=[decompose_story, generate_panel, edit_panel, extract_character],
)
