from google.adk.agents import Agent
from .tools import decompose_story, generate_panel, edit_panel, extract_character
from .prompts.system import MANGSTOON_INSTRUCTION

root_agent = Agent(
    model="gemini-3.1-pro-preview",
    name="mangstoon_director",
    description="AI 망상툰 Director — turns user fantasies into Korean scroll webtoons",
    instruction=MANGSTOON_INSTRUCTION,
    tools=[decompose_story, generate_panel, edit_panel, extract_character],
)
