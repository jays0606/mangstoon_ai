import base64
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

from ..gcs import upload_panel
from ..styles import get_character_design, STYLE_NAMES


def extract_character(image_path: str, style: str = "k-webtoon", session_id: str = "") -> dict:
    """Extract character from a selfie image and generate a face reference sheet.

    Two-step process:
    1) Gemini Pro analyzes the selfie image → face_description text + face_ref_prompt
    2) Gemini Flash Image generates a face reference sheet image from the prompt

    Args:
        image_path: Path to the uploaded selfie image file.
        style: Art style ID for style-specific character design.
        session_id: Session ID for GCS upload. If provided, uploads face ref to GCS.

    Returns:
        dict with:
        - face_description: Detailed style-optimized face description (no clothing).
        - face_ref_image: GCS URL (if session_id provided) or base64 data URL.
    """
    client = genai.Client()
    style_name = STYLE_NAMES.get(style, "Korean Webtoon")
    char_design = get_character_design(style)

    # Load the selfie image
    selfie = Image.open(image_path)
    selfie.load()

    # Step 1: Analyze selfie → face_description + face_ref_prompt
    try:
        response = client.models.generate_content(
            model="gemini-3.1-pro-preview",
            contents=[
                selfie,
                f"""You are a {style_name} character designer.

Analyze this selfie photo and create TWO outputs:

1. FACE_DESCRIPTION: A detailed face-only character description optimized for {style_name}
   illustration. Include ONLY permanent facial features — NO clothing.
   Cover: hair (style, length, color, texture, shine), eyes (shape, size, color, lashes,
   distinctive features), face shape, skin quality, nose, lips, any distinguishing marks.
   Use beauty-enhancing descriptors: "luminous skin with soft glow", "expressive eyes with
   light reflections", "silky hair with subtle sheen".
   Style direction: {char_design}
   Write as a single paragraph.

2. FACE_REF_PROMPT: A complete image generation prompt to create a 1:1 square face reference
   sheet showing this character HEAD AND NECK ONLY on white background, front view and
   three-quarter view side by side. {style_name} style. No clothing below collarbone.
   Include the full face description in the prompt for the image generator.

Return as JSON:
{{"face_description": "...", "face_ref_prompt": "..."}}""",
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_level="low"),
            ),
        )

        import json
        result = json.loads(response.text)
        face_description = result.get("face_description", "")
        face_ref_prompt = result.get("face_ref_prompt", "")

    except Exception as e:
        return {"status": "error", "message": f"Step 1 failed: {e}"}

    # Step 2: Generate face reference sheet image (using selfie as visual reference)
    face_ref_image = ""
    if face_ref_prompt:
        try:
            img_response = client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=[
                    selfie,
                    f"Using the photo above as visual reference for the character's face, generate: {face_ref_prompt}",
                ],
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio="1:1", image_size="1K"),
                ),
            )

            for part in img_response.candidates[0].content.parts:
                if part.inline_data is not None:
                    raw_bytes = part.inline_data.data
                    if isinstance(raw_bytes, str):
                        raw_bytes = base64.b64decode(raw_bytes)

                    # Save to disk
                    out_dir = Path(image_path).parent
                    ref_path = out_dir / "face_ref.png"
                    with open(ref_path, "wb") as f:
                        f.write(raw_bytes)

                    # Upload to GCS if session_id provided, otherwise fall back to base64
                    if session_id:
                        try:
                            face_ref_image = upload_panel(session_id, "face_ref.png", raw_bytes)
                        except Exception:
                            b64 = base64.b64encode(raw_bytes).decode()
                            face_ref_image = f"data:image/png;base64,{b64}"
                    else:
                        b64 = base64.b64encode(raw_bytes).decode()
                        face_ref_image = f"data:image/png;base64,{b64}"
                    break

        except Exception:
            # Non-fatal — we still have the text description
            pass

    return {
        "status": "success",
        "face_description": face_description,
        "face_ref_image": face_ref_image,
    }
