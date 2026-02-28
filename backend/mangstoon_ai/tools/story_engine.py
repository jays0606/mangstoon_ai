import json

from google import genai
from google.genai import types

from ..styles import get_style_writer


STORYBOARD_PROMPT = """You are a professional {writer_persona}.
Given a user's fantasy scenario, create a detailed storyboard in {style_name} style.

Rules:
- Create exactly {num_panels} panels.
- If 6-8 panels: use a tight 3-act structure (Setup 2 → Conflict/Development 3-4 → Payoff 2).
- If 12-16 panels: use a 5-act structure: Setup (2-3) → Rising Action (3-4) → Climax (2-3) → Resolution (2-3) → Epilogue (1-2).
- If 20-24 panels: use a full 5-act structure: Setup (4-5) → Rising Action (5-7) → Climax (3-4) → Resolution (4-5) → Epilogue (2-3).
- If 25+ panels: use an extended 5-act structure: Setup (5-6) → Rising Action (7-9) → Climax (4-5) → Resolution (5-6) → Epilogue (2-4).
- Vary pacing: quiet moments, action beats, emotional close-ups.
- If real people are mentioned, convert them to original fictional characters with similar vibes.
- CRITICAL: ALL text fields (title, dialogue, act names, character names, descriptions) MUST be in the SAME language as the user's input. If user writes in English, everything is English. If user writes in Korean, everything is Korean. NEVER mix languages within the same storyboard.
- Dialogue must be SHORT — maximum 8 words per speech bubble for readability when rendered in images.
- Each scene_description must be a SELF-CONTAINED visual paragraph that an image generator can
  use WITHOUT any other context. It must include BOTH:
  (a) BACKGROUND/ENVIRONMENT: specific physical details of the location (furniture, lighting,
      colors, props, weather, time of day). Panels in the same location must repeat the
      same background description word-for-word or very similarly.
  (b) CHARACTER ACTION: what the character is physically doing in this moment.
  BAD: "Doyun checks code on the plane" (too vague — what does the plane look like?)
  GOOD: "Inside a spacious business class cabin with cream leather seats and warm overhead
  reading lights, small oval windows showing a sunset sky outside. Doyun sits reclined in his
  seat, laptop open on the fold-down tray table, fingers hovering over the keyboard as he
  reviews lines of code on screen."
- Vary outfits across scenes. Characters should NOT wear the same thing for the whole story.

CRITICAL — Location & Scene Continuity:
- Define LOCATIONS first. Each location is a specific place (e.g., "business class cabin of a Boeing 777").
- Consecutive panels in the SAME location MUST share the same background, props, and environment.
- scene_description MUST explicitly name the location and describe it consistently.
  Example: If panels 3-6 are all in "the business class cabin", every scene_description must
  reference the same cabin interior (cream leather seats, warm overhead lighting, small windows).
- Characters in the same location keep the SAME outfit until they physically change clothes.
- Only change outfit when the location/time changes (e.g., next day, different venue).
- When transitioning locations, use a clear establishing shot (wide/bird's eye) for the first panel.

CRITICAL — Character definition rules:
- face_description is PERMANENT: hair, eyes, face shape, skin, distinguishing features. It NEVER changes.
- For attractive characters (love interests, idols), include beauty descriptors:
  "strikingly beautiful", "idol-level visual", detailed eye sparkle, skin glow, hair texture.
- outfit is PER-LOCATION: what the character wears at this location. It stays the SAME across
  consecutive panels in the same place. Only changes with location/time transitions.
- A panel can have 1 or 2 characters. Use character_names as a list. Most panels have 1 character
  (close-ups, solo moments). Use 2 characters for interaction scenes (conversations, confrontations).
  outfits and character_expressions are dicts keyed by character name.

Return ONLY valid JSON. No markdown, no code fences. Exactly this structure:

{{
  "title": "webtoon title",
  "characters": [
    {{
      "name": "character name",
      "face_description": "PERMANENT physical face/hair/features only. NO clothing. Example: Korean man, mid-20s, messy black hair falling over forehead, sharp tired eyes behind round thin-frame glasses, slim face, dark circles under eyes, small mole near right ear",
      "role": "protagonist / love interest / etc"
    }}
  ],
  "locations": [
    {{
      "id": "location_1",
      "name": "Business class cabin",
      "description": "Spacious business class cabin of a long-haul flight. Cream leather seats with wide armrests, warm overhead reading lights, small oval windows showing clouds or sunset. Soft ambient airline lighting."
    }}
  ],
  "panels": [
    {{
      "panel_number": 1,
      "act": "setup",
      "location_id": "location_1",
      "scene_description": "SELF-CONTAINED visual paragraph: describe the FULL BACKGROUND (room, lighting, props, colors) + what the character is doing. Must work as a standalone image prompt. Panels in the same location must repeat the same background details.",
      "character_names": ["primary character", "optional second character if present in scene"],
      "outfits": {{"Character Name": "outfit description for each character in the panel"}},
      "character_expressions": {{"Character Name": "expression and body language for each character"}},
      "dialogue": "speech bubble text (MAX 8 words, English only) or empty string",
      "dialogue_type": "speech / thought / narration / none — use 'thought' for inner monologue moments (e.g. realizations, nervousness, secret feelings)",
      "camera_angle": "wide shot / close-up / medium shot / low angle / bird's eye / dutch angle / over-shoulder / extreme close-up",
      "mood": "lighting and color mood description"
    }}
  ]
}}

User's story:
{user_story}"""


def decompose_story(user_story: str, num_panels: int = 30, style: str = "k-webtoon") -> dict:
    """Analyze a user's fantasy and produce a structured webtoon storyboard as JSON.

    Calls Gemini 3 Flash (low thinking) to act as a professional webtoon writer. Takes the user's
    raw story idea and returns a full storyboard with character definitions (face
    separate from outfit), narrative arc, per-panel scene descriptions, dialogue,
    camera angles, and mood.

    The orchestrator should present this storyboard to the user for review and editing
    before proceeding to image generation.

    Args:
        user_story: The user's fantasy/delusion scenario in free text. Any language.
        num_panels: Target number of panels. Default 30 for rich stories, minimum 6.

    Returns:
        dict with 'storyboard' containing the full structured JSON storyboard,
        or 'error' if generation failed.
    """
    if num_panels < 6:
        num_panels = 6

    client = genai.Client()

    response = None
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[STORYBOARD_PROMPT.format(
                user_story=user_story,
                num_panels=num_panels,
                writer_persona=get_style_writer(style),
                style_name=style,
            )],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_level="low"),
            ),
        )

        storyboard = json.loads(response.text)
        return {
            "status": "success",
            "storyboard": storyboard,
            "panel_count": len(storyboard.get("panels", [])),
        }

    except json.JSONDecodeError as e:
        raw = response.text[:500] if response else "(no response)"
        return {"status": "error", "message": f"Invalid JSON from model: {e}", "raw": raw}
    except Exception as e:
        return {"status": "error", "message": str(e)}
