import base64
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

from .image_gen import OUTPUT_BASE

# Same style as image_gen — must match for visual consistency
WEBTOON_STYLE = (
    "Korean webtoon style illustration. Clean digital line art with smooth cel-shading. "
    "Soft gradient coloring with vibrant accents. Large expressive eyes with detailed highlights. "
    "Modern manhwa aesthetic. Single panel illustration. "
    "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
)


EDIT_PROMPT_TEMPLATE = """You are a Korean webtoon image prompt specialist.
Given an original panel's metadata and an edit instruction, create a NEW optimized
image generation prompt that applies ONLY the requested edit while preserving everything else.

RULES:
1. Write as a narrative paragraph, NOT keywords.
2. Start with the style directive below.
3. Keep the character's FACE description exactly as provided (permanent identity).
4. Apply the edit instruction — change ONLY what was requested.
5. Preserve: camera angle, mood, outfit, expression UNLESS the edit explicitly changes them.
6. Include speech bubble instructions if dialogue is present.
7. Do NOT add white borders or margins.

STYLE DIRECTIVE:
{style}

CHARACTER FACE (permanent):
{face_description}

ORIGINAL PANEL:
- Scene: {scene_description}
- Outfit: {outfit}
- Expression: {character_expression}
- Camera: {camera_angle}
- Mood: {mood}
- Dialogue: {dialogue}

EDIT INSTRUCTION: {edit_instruction}

Return ONLY the new image prompt. Nothing else."""


def edit_panel(
    panel_number: int,
    edit_instruction: str,
    session_id: str,
    scene_description: str,
    face_description: str,
    outfit: str,
    character_expression: str = "",
    camera_angle: str = "",
    mood: str = "",
    dialogue: str = "",
    tool_context: Optional[object] = None,
) -> dict:
    """Regenerate a specific panel with edits. Two-step process:
    1) Gemini 3 Flash (minimal thinking) creates an updated image prompt applying the edit.
    2) Gemini 3.1 Flash Image generates the new panel image.

    The orchestrator passes the original panel metadata plus the user's edit request.
    Only the specified edit is applied — everything else is preserved.

    Args:
        panel_number: Which panel to edit (1-25).
        edit_instruction: What the user wants changed (e.g., "change background to Han River at night").
        session_id: The session ID from generate_all_panels — used to save edited panel in the same folder.
        scene_description: Original scene description from the storyboard.
        face_description: PERMANENT character face/hair/features.
        outfit: What the character was wearing in this panel.
        character_expression: Original expression/pose.
        camera_angle: Original camera angle.
        mood: Original mood/lighting.
        dialogue: Original dialogue text.
        tool_context: Optional ADK ToolContext — saves artifacts when running via adk web.

    Returns:
        dict with updated artifact filename, panel_number, image_path, and the edit applied.
    """
    client = genai.Client()

    # Use the same session directory as the original generation
    session_dir = OUTPUT_BASE / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate edited prompt
    edit_response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[EDIT_PROMPT_TEMPLATE.format(
            style=WEBTOON_STYLE,
            face_description=face_description,
            scene_description=scene_description,
            outfit=outfit,
            character_expression=character_expression,
            camera_angle=camera_angle,
            mood=mood,
            dialogue=dialogue,
            edit_instruction=edit_instruction,
        )],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),
        ),
    )
    edited_prompt = edit_response.text.strip()

    # Step 2: Generate image
    try:
        image_response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[edited_prompt],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="9:16"),
            ),
        )

        for part in image_response.candidates[0].content.parts:
            if part.inline_data is not None:
                filename = f"panel_{panel_number:02d}.png"
                image_path = session_dir / filename

                raw_bytes = part.inline_data.data
                if isinstance(raw_bytes, str):
                    raw_bytes = base64.b64decode(raw_bytes)
                with open(image_path, "wb") as f:
                    f.write(raw_bytes)

                if tool_context is not None:
                    artifact_part = types.Part(
                        inline_data=types.Blob(
                            mime_type=part.inline_data.mime_type,
                            data=part.inline_data.data,
                        )
                    )
                    tool_context.save_artifact(filename, artifact_part)

                return {
                    "status": "success",
                    "panel_number": panel_number,
                    "image_path": str(image_path),
                    "artifact": filename,
                    "edit_applied": edit_instruction,
                }

        return {"status": "error", "panel_number": panel_number, "message": "No image in response"}

    except Exception as e:
        return {"status": "error", "panel_number": panel_number, "message": str(e)}
