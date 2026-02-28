import json
from google import genai
from google.genai import types


def decompose_story(user_story: str, character_description: str) -> dict:
    """Break a user's fantasy story into 6-8 webtoon panel descriptions.

    Args:
        user_story: The user's delusion/fantasy scenario in free text.
        character_description: Visual description of the main character (from extract_character or user input).

    Returns:
        dict with 'panels' list. Each panel has: panel_number, scene, dialogue, narration, image_prompt.
    """
    client = genai.Client()

    prompt = f"""You are a Korean webtoon writer. Break the following story into exactly 6 panels for a scroll-format webtoon.

Character: {character_description}

Story: {user_story}

Return a JSON object with this exact structure:
{{
  "panels": [
    {{
      "panel_number": 1,
      "scene": "brief scene description in English for image generation",
      "dialogue": ["Character: '대사 내용'"],
      "narration": "웹툰 나레이션 박스 텍스트 (Korean)",
      "image_prompt": "detailed English prompt for image generation in Korean webtoon style"
    }}
  ]
}}

Rules for image_prompt:
- Korean webtoon art style, clean line art, cel-shading
- Include: {character_description}
- Include scene details, lighting, camera angle
- Leave space at bottom for speech bubbles
- Aspect ratio: tall vertical panel (9:16)

Return ONLY valid JSON. No markdown, no explanation."""

    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        ),
    )

    raw = response.text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    return json.loads(raw)
