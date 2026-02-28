import base64
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

OUTPUT_BASE = Path(__file__).parent.parent.parent / "output"
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)


def _get_session_dir(session_id: str | None = None) -> Path:
    """Get or create a session-specific output directory."""
    if not session_id:
        session_id = uuid.uuid4().hex[:8]
    session_dir = OUTPUT_BASE / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


# ── Proven webtoon style prompt — tested edge-to-edge, no white bars ──
WEBTOON_STYLE = (
    "Korean webtoon style illustration. Clean digital line art with smooth cel-shading. "
    "Soft gradient coloring with vibrant accents. Large expressive eyes with detailed highlights. "
    "Modern manhwa aesthetic. Single panel illustration. "
    "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
)


PROMPT_OPTIMIZER = """You are a Korean webtoon image prompt specialist.
Given panel metadata, craft ONE optimized image generation prompt.

RULES — follow these EXACTLY:
1. Write the prompt as a NARRATIVE PARAGRAPH describing the scene — NOT a keyword list.
2. Start with the style directive (provided below).
3. Include the character's FACE description for consistency (provided below — copy it exactly).
4. Include the OUTFIT for this specific scene (different from face — provided below).
5. The scene_description already contains the location/background details. Reproduce them
   faithfully — the background must look consistent across panels in the same setting.
6. Include camera angle, lighting, and mood naturally in the narrative.
7. If there is dialogue, add speech bubble instruction:
   - speech: 'Include a white speech bubble with rounded edges and black outline near the character containing the Korean text: "[text]"'
   - thought: 'Include a cloud-shaped thought bubble near the character containing: "[text]"'
   - narration: 'Include a rectangular narration box at the bottom with dark semi-transparent background and white text: "[text]"'
8. Keep speech bubble text under 15 words.
9. Do NOT include any instructions about leaving white space or margins.

STYLE DIRECTIVE (include at the start):
{style}

CHARACTER FACE (permanent — include exactly as-is):
{face_description}

PANEL METADATA:
- Outfit: {outfit}
- Expression: {character_expression}
- Scene: {scene_description}
- Camera: {camera_angle}
- Mood: {mood}
- Dialogue: {dialogue}
- Dialogue type: {dialogue_type}

Return ONLY the final image prompt. Nothing else."""


def _generate_single_panel(
    panel_number: int,
    scene_description: str,
    face_description: str,
    outfit: str,
    character_expression: str,
    camera_angle: str,
    mood: str,
    dialogue: str = "",
    dialogue_type: str = "speech",
    session_dir: Path | None = None,
) -> dict:
    """Internal: generate one panel (prompt optimize → image gen). No tool_context."""
    if session_dir is None:
        session_dir = _get_session_dir()
    client = genai.Client()

    # Step 1: Optimize the image prompt
    optimizer_response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[PROMPT_OPTIMIZER.format(
            style=WEBTOON_STYLE,
            face_description=face_description,
            outfit=outfit,
            character_expression=character_expression,
            scene_description=scene_description,
            camera_angle=camera_angle,
            mood=mood,
            dialogue=dialogue,
            dialogue_type=dialogue_type,
        )],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),
        ),
    )
    optimized_prompt = optimizer_response.text.strip()

    # Step 2: Generate the image
    try:
        image_response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[optimized_prompt],
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

                return {
                    "status": "success",
                    "panel_number": panel_number,
                    "image_path": str(image_path),
                    "artifact": filename,
                    "optimized_prompt": optimized_prompt[:300],
                }

        return {"status": "error", "panel_number": panel_number, "message": "No image in response"}

    except Exception as e:
        return {"status": "error", "panel_number": panel_number, "message": str(e)}


def generate_all_panels(panels_json: str, tool_context: Optional[object] = None) -> dict:
    """Generate ALL webtoon panels in parallel. This is the main batch generation tool.

    Takes the full storyboard JSON (from decompose_story) and generates all panel images
    simultaneously using ThreadPoolExecutor. Much faster than sequential generation.

    Each panel goes through a 2-step process:
    1) Gemini 3 Flash optimizes the image prompt from panel metadata.
    2) Gemini 3.1 Flash Image generates the actual panel image.

    Args:
        panels_json: JSON string containing the full storyboard. Must have:
            - "characters": list of {name, face_description, role}
            - "panels": list of {panel_number, scene_description, character_name,
              outfit, character_expression, camera_angle, mood, dialogue, dialogue_type}

    Returns:
        dict with total count, success/failure counts, and per-panel results.
    """
    import json

    try:
        storyboard = json.loads(panels_json)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON: {e}"}

    characters = {c["name"]: c["face_description"] for c in storyboard.get("characters", [])}
    locations = {loc["id"]: loc["description"] for loc in storyboard.get("locations", [])}
    panels = storyboard.get("panels", [])

    if not panels:
        return {"status": "error", "message": "No panels in storyboard"}

    # Create a session-specific output directory
    session_id = uuid.uuid4().hex[:8]
    session_dir = _get_session_dir(session_id)
    results = []

    # Generate all panels in parallel (max 6 concurrent to avoid rate limits)
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {}
        for panel in panels:
            char_name = panel.get("character_name", "")
            face_desc = characters.get(char_name, "")

            # Prepend location description to scene_description for background consistency
            scene_desc = panel.get("scene_description", "")
            loc_id = panel.get("location_id", "")
            if loc_id and loc_id in locations:
                scene_desc = f"[Setting: {locations[loc_id]}] {scene_desc}"

            future = executor.submit(
                _generate_single_panel,
                panel_number=panel["panel_number"],
                scene_description=scene_desc,
                face_description=face_desc,
                outfit=panel.get("outfit", ""),
                character_expression=panel.get("character_expression", ""),
                camera_angle=panel.get("camera_angle", "medium shot"),
                mood=panel.get("mood", ""),
                dialogue=panel.get("dialogue", ""),
                dialogue_type=panel.get("dialogue_type", "none"),
                session_dir=session_dir,
            )
            futures[future] = panel["panel_number"]

        for future in as_completed(futures):
            panel_num = futures[future]
            try:
                result = future.result()
                # Save as ADK artifact if tool_context available
                if tool_context is not None and result.get("status") == "success":
                    image_path = Path(result["image_path"])
                    if image_path.exists():
                        img_bytes = image_path.read_bytes()
                        artifact_part = types.Part(
                            inline_data=types.Blob(
                                mime_type="image/png",
                                data=img_bytes,
                            )
                        )
                        tool_context.save_artifact(result["artifact"], artifact_part)
                results.append(result)
            except Exception as e:
                results.append({"status": "error", "panel_number": panel_num, "message": str(e)})

    # Sort by panel number
    results.sort(key=lambda r: r.get("panel_number", 0))

    success_count = sum(1 for r in results if r.get("status") == "success")
    return {
        "status": "success",
        "session_id": session_id,
        "output_dir": str(session_dir),
        "total_panels": len(panels),
        "generated": success_count,
        "failed": len(panels) - success_count,
        "results": results,
    }


# Keep single panel gen for edit_panel's use and standalone testing
generate_panel = _generate_single_panel
