import base64
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

from ..gcs import upload_panel
from ..styles import get_style_prompt, get_style_config

OUTPUT_BASE = Path(__file__).parent.parent.parent / "output"
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)


def _get_session_dir(session_id: str | None = None) -> Path:
    """Get or create a session-specific output directory."""
    if not session_id:
        session_id = uuid.uuid4().hex[:8]
    session_dir = OUTPUT_BASE / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


PROMPT_OPTIMIZER = """You are an expert sequential art image prompt specialist.
Given panel metadata, craft ONE optimized image generation prompt.

RULES — follow these EXACTLY:
1. Write the prompt as a NARRATIVE PARAGRAPH describing the scene — NOT a keyword list.
2. Start with the style directive (provided below).
3. Include ALL characters' FACE descriptions for consistency (provided below — copy exactly).
   If multiple characters are listed, include BOTH in the scene with their distinct appearances.
4. Include the OUTFIT for each character in this specific scene (different from face — provided below).
5. The scene_description already contains the location/background details. Reproduce them
   faithfully — the background must look consistent across panels in the same setting.
6. Include camera angle, lighting, and mood naturally in the narrative.
7. If there is dialogue, add EXACTLY ONE speech bubble instruction — do NOT duplicate:
   - speech: 'Include exactly ONE LARGE white speech bubble with rounded edges and bold black outline near the character, containing LARGE BOLD readable text in {language}: "[text]"'
   - thought: 'Include exactly ONE LARGE cloud-shaped thought bubble near the character containing LARGE BOLD readable text in {language}: "[text]"'
   - narration: 'Include exactly ONE wide rectangular narration box at the bottom with dark semi-transparent background and LARGE BOLD white text in {language}: "[text]"'
   IMPORTANT: Each distinct quoted dialogue line = exactly ONE bubble. Multiple characters may each have their own bubble with DIFFERENT text, but never repeat the same text in two bubbles.
   Make text BIG and BOLD — at least 1/8 the width of the bubble.
8. Keep speech bubble text under 10 words for maximum readability.
9. Ensure the scene fills the entire canvas — describe a rich, detailed background that extends to every edge.
    Use "full-bleed composition" language. The background covers the entire frame corner to corner.
10. CRITICAL — LANGUAGE CONSISTENCY: ALL visible text in the image MUST be in {language}.
    This means speech bubbles, signs, storefronts, neon lights, posters, screens — everything readable is in {language}.
    Do NOT mix languages. Every piece of text must be consistently in {language}.
    At the END of your prompt, always append: "All visible text, signage, and speech bubbles in this image are written in {language} only. Do not mix languages."

STYLE DIRECTIVE (include at the start):
{style}

CHARACTER FACES (permanent — include exactly as-is for each character):
{face_description}

DIALOGUE LANGUAGE: {language}

PANEL METADATA:
- Outfits: {outfit}
- Expressions: {character_expression}
- Scene: {scene_description}
- Camera: {camera_angle}
- Mood: {mood}
- Dialogue: {dialogue}
- Dialogue type: {dialogue_type}

Return ONLY the final image prompt. Nothing else."""


def _detect_language(text: str) -> str:
    """Simple language detection based on character ranges."""
    if not text:
        return "English"
    korean_count = sum(1 for c in text if '\uac00' <= c <= '\ud7a3' or '\u3131' <= c <= '\u3163')
    japanese_count = sum(1 for c in text if '\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff')
    if korean_count > 2:
        return "Korean"
    if japanese_count > 2:
        return "Japanese"
    return "English"


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
    session_id: str | None = None,
    style: str = "k-webtoon",
    language: str | None = None,
) -> dict:
    """Internal: generate one panel (prompt optimize → image gen). No tool_context."""
    if session_dir is None:
        session_dir = _get_session_dir()
    if language is None:
        language = _detect_language(dialogue)
    client = genai.Client()

    # Step 1: Optimize the image prompt
    optimizer_response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[PROMPT_OPTIMIZER.format(
            style=get_style_prompt(style),
            face_description=face_description,
            outfit=outfit,
            character_expression=character_expression,
            scene_description=scene_description,
            camera_angle=camera_angle,
            mood=mood,
            dialogue=dialogue,
            dialogue_type=dialogue_type,
            language=language,
        )],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),
        ),
    )
    optimized_prompt = optimizer_response.text.strip()

    # Step 2: Generate the image
    style_cfg = get_style_config(style)
    try:
        image_response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[optimized_prompt],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=style_cfg["aspect_ratio"], image_size="1K"),
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

                # Upload to GCS
                gcs_url = ""
                if session_id:
                    try:
                        gcs_url = upload_panel(session_id, filename, raw_bytes)
                    except Exception:
                        pass  # fall back to local file

                return {
                    "status": "success",
                    "panel_number": panel_number,
                    "image_path": str(image_path),
                    "image_url": gcs_url,
                    "artifact": filename,
                    "optimized_prompt": optimized_prompt[:300],
                }

        return {"status": "error", "panel_number": panel_number, "message": "No image in response"}

    except Exception as e:
        return {"status": "error", "panel_number": panel_number, "message": str(e)}


def generate_all_panels(panels_json: str, style: str = "k-webtoon", tool_context: Optional[object] = None) -> dict:
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

    # Detect language from first panel's dialogue
    first_dialogue = next((p.get("dialogue", "") for p in panels if p.get("dialogue")), "")
    lang = _detect_language(first_dialogue)

    # Create a session-specific output directory
    session_id = uuid.uuid4().hex[:8]
    session_dir = _get_session_dir(session_id)
    results = []

    # Generate all panels in parallel (max 6 concurrent to avoid rate limits)
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {}
        for panel in panels:
            # Multi-character support
            char_names = panel.get("character_names", [])
            if not char_names:
                cn = panel.get("character_name", "")
                char_names = [cn] if cn else []

            face_parts = [f"[{cn}] {characters.get(cn, '')}" for cn in char_names if characters.get(cn)]
            face_desc = "\n".join(face_parts)

            outfits_raw = panel.get("outfits", {})
            exprs_raw = panel.get("character_expressions", {})
            outfit = "; ".join(f"{k}: {v}" for k, v in outfits_raw.items()) if isinstance(outfits_raw, dict) and outfits_raw else panel.get("outfit", "")
            char_expr = "; ".join(f"{k}: {v}" for k, v in exprs_raw.items()) if isinstance(exprs_raw, dict) and exprs_raw else panel.get("character_expression", "")

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
                outfit=outfit,
                character_expression=char_expr,
                camera_angle=panel.get("camera_angle", "medium shot"),
                mood=panel.get("mood", ""),
                dialogue=panel.get("dialogue", ""),
                dialogue_type=panel.get("dialogue_type", "none"),
                session_dir=session_dir,
                session_id=session_id,
                style=style,
                language=lang,
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
