from google.adk.agents import Agent
from google.genai import types

from .prompts.system import MANGSTOON_DIRECTOR_INSTRUCTION
from .tools.story_engine import decompose_story
from .tools.image_gen import generate_all_panels
from .tools.panel_editor import edit_panel
from .tools.character import extract_character

root_agent = Agent(
    model="gemini-3.1-pro-preview",
    name="mangstoon_director",
    description="AI Webtoon Director that turns user fantasies into scroll-style webtoons",
    instruction=MANGSTOON_DIRECTOR_INSTRUCTION,
    tools=[decompose_story, generate_all_panels, edit_panel, extract_character],
    generate_content_config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="low"),
    ),
)
