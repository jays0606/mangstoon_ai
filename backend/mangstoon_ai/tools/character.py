from google import genai
from google.genai import types


def extract_character(selfie_description: str) -> dict:
    """Extract a detailed face-only character description from a selfie description.

    Takes a text description of a user's selfie (provided by the orchestrator after
    viewing the uploaded image) and generates a webtoon-optimized face description
    that can be used as the permanent character identity across all panels.

    The output separates FACE (permanent features) from any clothing, ensuring
    the character can wear different outfits across scenes while maintaining
    facial consistency.

    For attractive character rendering, the description includes beauty-specific
    descriptors: eye sparkle, skin glow, hair texture, facial proportions.

    Args:
        selfie_description: Text description of the uploaded selfie — what the person
            looks like (hair, eyes, face shape, distinguishing features, approximate age).

    Returns:
        dict with:
        - face_description: Detailed webtoon-optimized face description (no clothing).
        - face_ref_prompt: Prompt to generate a 1:1 face reference sheet.
    """
    client = genai.Client()

    try:
        response = client.models.generate_content(
            model="gemini-3.1-pro-preview",
            contents=[f"""You are a Korean webtoon character designer.

Given a description of a real person's appearance from their selfie, create TWO outputs:

1. FACE_DESCRIPTION: A detailed face-only character description optimized for Korean webtoon
   illustration. Include ONLY permanent facial features — NO clothing.
   Cover: hair (style, length, color, texture, shine), eyes (shape, size, color, lashes,
   distinctive features), face shape, skin quality, nose, lips, any distinguishing marks.
   Use beauty-enhancing descriptors: "luminous skin with soft glow", "expressive eyes with
   light reflections", "silky hair with subtle sheen".
   Write as a single paragraph.

2. FACE_REF_PROMPT: A complete image generation prompt to create a 1:1 square face reference
   sheet showing this character HEAD AND NECK ONLY on white background, front view and
   three-quarter view side by side. Korean webtoon style. No clothing below collarbone.

Person's appearance:
{selfie_description}

Return as JSON:
{{"face_description": "...", "face_ref_prompt": "..."}}"""],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_level="low"),
            ),
        )

        import json
        result = json.loads(response.text)
        return {
            "status": "success",
            "face_description": result.get("face_description", ""),
            "face_ref_prompt": result.get("face_ref_prompt", ""),
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
