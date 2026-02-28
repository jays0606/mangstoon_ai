"""
Test v4: 4 maximally distinct styles. Same scene, no ref images.
Webtoon (soft/clean) vs Anime (vibrant/glossy) vs Marvel (ink/bold) vs Cinematic (painted/dark)
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
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "style_test_v4"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FACE_TEXT = (
    "Korean man, mid-20s. Messy black hair falling over forehead, slightly long. "
    "Sharp but tired eyes behind round thin-frame glasses. Slim face with slight jaw. "
    "Dark circles under eyes. Small mole near right ear."
)

STYLES = {
    "webtoon": {
        "name": "Korean Webtoon",
        "aspect_ratio": "9:16",
        "style_prompt": (
            "Korean webtoon style illustration. Clean digital line art with smooth cel-shading. "
            "Soft gradient coloring with warm pastel tones and gentle vibrant accents. "
            "Large expressive manhwa-style eyes with detailed iris highlights and light reflections. "
            "Smooth flawless skin rendering with subtle pink blush marks. "
            "Soft diffused lighting with gentle edge glow. Clean minimal backgrounds with soft color washes. "
            "Modern romance manhwa aesthetic — pretty, clean, inviting. "
            "Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
        "face_ref_style": (
            "Korean webtoon style character reference. Clean digital line art with smooth cel-shading. "
            "Soft pastel gradient coloring. Large expressive manhwa eyes with iris highlights. "
            "Smooth skin with subtle blush. Modern romance manhwa aesthetic — pretty and clean."
        ),
    },
    "anime": {
        "name": "Japanese Anime",
        "aspect_ratio": "9:16",
        "style_prompt": (
            "High-quality Japanese anime illustration style, like a key visual from a modern anime series "
            "(Makoto Shinkai, ufotable, MAPPA studio quality). "
            "Vibrant rich colors with dramatic contrast — deep saturated shadows and brilliant glowing highlights. "
            "Glossy shiny rendering on hair and eyes — visible specular highlights and light streaks. "
            "VERY large detailed anime eyes with multiple layered light reflections, gradient irises, and catchlights. "
            "Dramatic cinematic lighting effects — lens flares, light particles floating in air, god-rays, bloom glow. "
            "Hyper-detailed backgrounds with atmospheric perspective and bokeh. "
            "Vivid color palette pushed to maximum saturation — electric blues, hot pinks, burning oranges. "
            "Anime proportions — elongated limbs, expressive faces, dynamic hair movement. "
            "Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
        "face_ref_style": (
            "Japanese anime character reference — high-quality modern anime style (Makoto Shinkai / ufotable quality). "
            "Vibrant saturated colors with dramatic lighting. Glossy shiny hair with visible light streaks. "
            "VERY large detailed anime eyes with layered reflections, gradient irises, multiple catchlights. "
            "Dramatic rim lighting. Vivid color palette. Anime proportions."
        ),
    },
    "comic": {
        "name": "Marvel Comic",
        "aspect_ratio": "2:3",
        "style_prompt": (
            "Marvel comic book art style. Rendered exactly like a panel from a modern Marvel Comics series "
            "(Jim Lee, Stuart Immonen, Sara Pichelli era). "
            "VERY THICK bold black ink outlines on all figures and objects — outlines much heavier than anime or webtoon. "
            "Rich saturated flat color fills — bold primary reds, blues, yellows, no soft gradients. "
            "Hard-edged dramatic shadows with stark light/dark contrast — shadows are solid black shapes, not soft falloff. "
            "Detailed ink crosshatching in all shadow areas and textures. "
            "Slightly exaggerated heroic proportions — broader shoulders, defined musculature even on lean characters. "
            "Dynamic foreshortening and dramatic perspective. Cinematic action composition. "
            "Western comic book coloring — flat bold color areas separated by heavy black ink lines. "
            "Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
        "face_ref_style": (
            "Marvel comic book character reference sheet. VERY THICK bold black ink outlines. "
            "Rich saturated flat color fills — bold primaries, no soft gradients. "
            "Hard-edged shadows as solid black shapes. Crosshatching in shadow areas. "
            "Slightly heroic proportions — defined jawline, broader neck. "
            "Western Marvel comic coloring style."
        ),
    },
    "cinematic": {
        "name": "Cinematic Manhwa",
        "aspect_ratio": "9:16",
        "style_prompt": (
            "Cinematic Korean manhwa digital painting in the style of Solo Leveling and Omniscient Reader's Viewpoint. "
            "This is a PAINTING — absolutely NO visible line art, no outlines, no ink lines. "
            "Semi-realistic rendered style with visible oil-painting-like brushstrokes in shading and textures. "
            "Dramatic volumetric lighting — god-rays cutting through darkness, strong rim light on characters, "
            "atmospheric haze and fog. Rich deep DARK color palette — midnight navy, deep purple, charcoal black — "
            "punctuated by glowing neon accent highlights (electric blue, burning amber, hot magenta). "
            "Detailed photorealistic background environments with atmospheric depth and perspective. "
            "Cinematic film color grading — desaturated midtones with vivid accent colors. "
            "Realistic human proportions — NOT anime or cartoon eyes. Mature, grounded aesthetic. "
            "Moody, intense, epic atmosphere. "
            "Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
        "face_ref_style": (
            "Cinematic Korean manhwa character reference — digital PAINTING, absolutely NO line art or outlines. "
            "Semi-realistic rendered face with visible painterly brushstrokes. Dramatic rim lighting against dark background. "
            "Realistic proportions — NOT anime eyes. Dark moody color palette with glowing accent highlights. "
            "Like a Solo Leveling character portrait. Mature, intense aesthetic."
        ),
    },
}

# Same scene for all
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
This is a reference sheet — clarity and recognizability are priority."""

executor = ThreadPoolExecutor(max_workers=4)
sem = asyncio.Semaphore(4)


def gen_sync(name, prompt, aspect):
    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(aspect_ratio=aspect),
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


async def gen_async(name, prompt, aspect):
    async with sem:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, gen_sync, name, prompt, aspect)


async def main():
    tasks = []
    for key, style in STYLES.items():
        face_prompt = FACE_REF_TEMPLATE.format(face_ref_style=style["face_ref_style"], face=FACE_TEXT)
        tasks.append(gen_async(f"{key}_face", face_prompt, "1:1"))

        scene_prompt = SCENE_TEMPLATE.format(style=style["style_prompt"], face=FACE_TEXT)
        tasks.append(gen_async(f"{key}_panel", scene_prompt, style["aspect_ratio"]))

    print(f"Generating {len(tasks)} images (4 styles × face + panel)...")
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
