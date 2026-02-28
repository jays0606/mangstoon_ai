"""
Test v2: Style-specific face refs + much more aggressive style prompts.
Each style gets its own face ref generated in that style, then a panel using it.
"""
import asyncio
import base64
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "style_test_v2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FACE_TEXT = (
    "Korean man, mid-20s. Messy black hair falling over forehead, slightly long. "
    "Sharp but tired eyes behind round thin-frame glasses. Slim face with slight jaw. "
    "Dark circles under eyes. Small mole near right ear."
)

# ── Much more aggressive style definitions ──

STYLES = {
    "webtoon": {
        "name": "Korean Webtoon",
        "aspect_ratio": "9:16",
        "face_ref_aspect": "1:1",
        "style_prompt": (
            "Korean webtoon style illustration. Clean digital line art with smooth cel-shading. "
            "Soft gradient coloring with vibrant pastel-to-warm accents. Large expressive anime-inspired eyes "
            "with detailed iris highlights and light reflections. Modern manhwa aesthetic with "
            "clean flat backgrounds and soft edge glow. Smooth skin rendering with subtle blush marks. "
            "Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
        "face_ref_style": (
            "Korean webtoon style character reference. Clean digital line art with smooth cel-shading. "
            "Large expressive eyes with detailed iris highlights. Soft gradient coloring. "
            "Modern manhwa aesthetic. Smooth skin with subtle color gradients."
        ),
    },
    "manga": {
        "name": "Japanese Manga",
        "aspect_ratio": "3:4",
        "face_ref_aspect": "1:1",
        "style_prompt": (
            "Japanese manga style illustration. STRICTLY BLACK AND WHITE ONLY — absolutely NO color, "
            "no grey tones from digital shading. Pure black ink on white paper. "
            "Bold confident ink lines with dramatic line weight variation — thick for contours, thin for details. "
            "Screen-tone dot patterns for mid-tone shading (visible dot grid pattern). "
            "Heavy cross-hatching for deep shadows. Speed lines and impact effects where appropriate. "
            "Dramatic high-contrast composition. Manga-proportioned eyes. "
            "Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
        "face_ref_style": (
            "Japanese manga style character reference. STRICTLY BLACK AND WHITE ONLY — NO color. "
            "Bold ink lines on white paper. Screen-tone dot-pattern shading on cheeks and hair. "
            "Cross-hatching for shadows. High contrast. Manga-proportioned features."
        ),
    },
    "comic": {
        "name": "American Comic",
        "aspect_ratio": "2:3",
        "face_ref_aspect": "1:1",
        "style_prompt": (
            "American superhero comic book style illustration. BOLD THICK ink outlines — much heavier than manga or webtoon. "
            "Rich DEEPLY SATURATED colors — primary reds, blues, yellows pushed to maximum vibrancy. "
            "Hard dramatic cel-shading with stark shadow/highlight contrast — no soft gradients. "
            "Strong muscular figure proportions even for non-heroes. Detailed crosshatching in all shadow areas. "
            "Dynamic heroic poses and compositions. Cinematic dramatic lighting with hard-edged shadows. "
            "Western comic book coloring style — flat bold color fills with minimal blending. "
            "Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
        "face_ref_style": (
            "American comic book style character reference. BOLD THICK ink outlines. "
            "Rich saturated colors with hard cel-shading. Strong jaw, defined features. "
            "Western comic coloring — flat bold fills, dramatic shadow shapes. Crosshatching in shadows."
        ),
    },
    "cinematic": {
        "name": "Cinematic Manhwa",
        "aspect_ratio": "9:16",
        "face_ref_aspect": "1:1",
        "style_prompt": (
            "Cinematic Korean manhwa digital painting in the style of Solo Leveling and Omniscient Reader's Viewpoint. "
            "NO line art — this is a PAINTING, not illustration. Semi-realistic rendered style with "
            "visible painterly brushstrokes in shading and backgrounds. Dramatic volumetric lighting "
            "with god-rays, rim light, and atmospheric haze. Rich deep color palette — dark navy, "
            "deep purple, midnight blue — with glowing neon accent highlights (electric blue, amber, magenta). "
            "Detailed realistic background environments with atmospheric perspective. "
            "Cinematic film color grading. Characters rendered with realistic proportions, not anime-proportioned. "
            "Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
        "face_ref_style": (
            "Cinematic Korean manhwa style character reference — digital PAINTING, NOT line art. "
            "Semi-realistic rendered face with visible brushwork. Dramatic rim lighting. "
            "Realistic proportions — NOT anime eyes. Rich moody color palette. "
            "Like a Solo Leveling character portrait."
        ),
    },
}

# ── Test scene (same content, different style rendering) ──

SCENE_TEMPLATE = """{style}

FACE: {face}

OUTFIT: Dark hoodie with the hood down, cargo pants, worn sneakers. Laptop bag slung across chest.

A young Korean man sprints through a neon-lit alley at night in a futuristic city. Rain pours down heavily.
Neon signs in Korean reflect off the wet pavement in streaks of vibrant color. He looks back over his
shoulder with an urgent, determined expression. His glasses catch the neon reflections. His messy hair
is wet, plastered to his forehead. Water splashes up from his footsteps.
Camera: dynamic dutch angle from low, motion blur on background, sharp focus on him.
Moody cyberpunk atmosphere with rain and neon.
Include a rectangular narration box at the bottom with dark semi-transparent background and white text: "그날 밤, 모든 것이 바뀌었다." """

FACE_REF_TEMPLATE = """{face_ref_style}

{face}

Draw HEAD AND NECK ONLY on a clean white background.
Two views side by side: front-facing (left) and three-quarter angle (right).
NO clothing visible — cut off at base of neck / collarbone.
Focus on capturing distinctive facial features for character consistency.
This is a reference sheet — clarity and recognizability are priority."""

executor = ThreadPoolExecutor(max_workers=4)
sem = asyncio.Semaphore(4)


def gen_sync(name: str, prompt: str, aspect_ratio: str) -> tuple[str, bytes | None]:
    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
    )
    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=[prompt],
        config=config,
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            raw = part.inline_data.data
            if isinstance(raw, str):
                raw = base64.b64decode(raw)
            return (name, raw)
    return (name, None)


async def gen_async(name: str, prompt: str, aspect_ratio: str):
    async with sem:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, gen_sync, name, prompt, aspect_ratio)


async def main():
    tasks = []

    for key, style in STYLES.items():
        # Face ref in this style
        face_prompt = FACE_REF_TEMPLATE.format(
            face_ref_style=style["face_ref_style"],
            face=FACE_TEXT,
        )
        tasks.append(gen_async(f"{key}_face", face_prompt, style["face_ref_aspect"]))

        # Action panel in this style
        scene_prompt = SCENE_TEMPLATE.format(
            style=style["style_prompt"],
            face=FACE_TEXT,
        )
        tasks.append(gen_async(f"{key}_panel", scene_prompt, style["aspect_ratio"]))

    print(f"Generating {len(tasks)} images (4 styles × face ref + panel)...")
    results = await asyncio.gather(*tasks)

    for name, img_bytes in results:
        if img_bytes:
            path = OUTPUT_DIR / f"{name}.png"
            path.write_bytes(img_bytes)
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} — FAILED")

    print(f"\nDone → {OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
