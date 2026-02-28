import json
from pathlib import Path
from google import genai
from google.genai import types
from .image_gen import OUTPUT_DIR


def edit_panel(panel_number: int, edit_instruction: str, character_description: str, original_image_prompt: str = "") -> dict:
    """Edit a specific webtoon panel based on user's chat instruction.

    Args:
        panel_number: Which panel to edit (1-8).
        edit_instruction: What to change, in the user's own words (e.g. '한강 배경으로 바꿔줘').
        character_description: Visual description of the main character for consistency.
        original_image_prompt: The original prompt used to generate this panel (for context).

    Returns:
        dict with 'panel_number', 'image_path', and 'status'.
    """
    client = genai.Client()

    # Step 1: Use Pro to translate the edit instruction into a refined image prompt
    refine_prompt = f"""You are a Korean webtoon art director. Rewrite the image prompt for panel {panel_number} based on the edit instruction.

Original prompt: {original_image_prompt or "Not provided."}
Edit instruction: {edit_instruction}
Character: {character_description}

Write a single, refined English image generation prompt that incorporates the requested change.
Keep what should stay the same. Apply only the requested change.
The prompt should be a narrative paragraph, not a keyword list.
Return ONLY the prompt text — no JSON, no explanation."""

    refine_response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=refine_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        ),
    )
    refined_prompt = refine_response.text.strip()

    # Step 2: Check if we have the original image for reference-based editing
    original_path = OUTPUT_DIR / f"panel_{panel_number:02d}.png"

    full_prompt = f"""Korean webtoon panel {panel_number}. {refined_prompt}

The main character is {character_description}.

Art style: clean Korean webtoon line art with cel-shading, bold outlines, vibrant colors. \
Vertical composition for mobile scroll. \
Leave the bottom 20% clear for speech bubble overlays. \
No text or captions within the image."""

    if original_path.exists():
        # Reference-based edit: pass original image for visual context
        from PIL import Image as PILImage
        original_image = PILImage.open(str(original_path))
        contents = [full_prompt, original_image]
    else:
        contents = [full_prompt]

    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="9:16",
                image_size="1K",
            ),
        ),
    )

    for part in response.parts:
        if part.inline_data is not None:
            image = part.as_image()
            output_path = OUTPUT_DIR / f"panel_{panel_number:02d}.png"
            image.save(str(output_path))
            return {
                "panel_number": panel_number,
                "image_path": str(output_path),
                "status": "success",
            }

    return {
        "panel_number": panel_number,
        "image_path": None,
        "status": "error: no image in response",
    }
