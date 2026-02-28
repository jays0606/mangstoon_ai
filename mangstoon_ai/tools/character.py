import base64
from pathlib import Path
from google import genai
from google.genai import types


def extract_character(selfie_path: str) -> dict:
    """Extract visual character traits from a selfie for consistent panel generation.

    Args:
        selfie_path: Absolute path to the uploaded selfie image file.

    Returns:
        dict with 'character_prompt' (reusable template string for all panel generations)
        and 'description' (human-readable summary).
    """
    client = genai.Client()

    image_bytes = Path(selfie_path).read_bytes()
    mime_type = "image/jpeg" if selfie_path.endswith((".jpg", ".jpeg")) else "image/png"

    prompt = """Analyze this person's appearance and write a character description for use in Korean webtoon image generation.

Return a JSON object:
{
  "character_prompt": "A concise, reusable visual description for consistent image generation. Include: hair color and style, face shape, skin tone, distinctive features. Written as a clause to embed in image prompts, e.g. 'a young Korean man with short black hair, sharp jawline, and warm brown eyes'",
  "description": "Human-readable summary of the person's appearance in Korean"
}

Be specific but not exaggerated. Focus on features that can be consistently reproduced across multiple webtoon panels.
Return ONLY valid JSON."""

    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=[
            types.Part(text=prompt),
            types.Part(
                inline_data=types.Blob(mime_type=mime_type, data=base64.b64encode(image_bytes).decode()),
                media_resolution={"level": "media_resolution_high"},
            ),
        ],
        config=types.GenerateContentConfig(
            http_options={"api_version": "v1alpha"},
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        ),
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    import json
    return json.loads(raw)
