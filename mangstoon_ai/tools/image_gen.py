import base64
import os
from pathlib import Path
from google import genai
from google.genai import types


OUTPUT_DIR = Path(__file__).parent.parent.parent / "output" / "panels"


def generate_panel(image_prompt: str, panel_number: int, character_description: str = "") -> dict:
    """Generate a single webtoon panel image using Gemini Flash Image (Nano Banana 2).

    Args:
        image_prompt: Detailed scene description for this panel.
        panel_number: Panel position (1-8) in the webtoon sequence.
        character_description: Visual description of the main character for consistency.

    Returns:
        dict with 'panel_number', 'image_path' (saved file path), and 'status'.
    """
    client = genai.Client()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build the full prompt following best practices:
    # narrative paragraph, hyper-specific, webtoon style, negative space for bubbles
    full_prompt = f"""Korean webtoon panel {panel_number}. {image_prompt}

The main character is {character_description}.

Art style: clean Korean webtoon line art with cel-shading, bold outlines, vibrant colors. \
Vertical composition optimized for mobile scroll reading. \
Leave an empty area at the bottom 20% of the frame for speech bubble overlays — \
that area should have a plain or minimal background with no important visual elements. \
No text, no captions, no watermarks within the image itself."""

    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=full_prompt,
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
