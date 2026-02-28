"""
Test v3: Push comic style to full Marvel. Generate face ref + 2 panels.
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
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "style_test_v3"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FACE_TEXT = (
    "Korean man, mid-20s. Messy black hair falling over forehead, slightly long. "
    "Sharp but tired eyes behind round thin-frame glasses. Slim face with slight jaw. "
    "Dark circles under eyes. Small mole near right ear."
)

COMIC_STYLE = (
    "Marvel comic book art style. Rendered exactly like a panel from a modern Marvel Comics series "
    "(Jim Lee, Stuart Immonen, Sara Pichelli era). "
    "VERY THICK bold black ink outlines on all figures and objects — outlines much heavier than manga or webtoon. "
    "Rich saturated flat color fills — bold primary reds, blues, yellows, no soft gradients. "
    "Hard-edged dramatic shadows with stark light/dark contrast — shadows are solid black shapes, not soft falloff. "
    "Detailed ink crosshatching in all shadow areas and textures. "
    "Slightly exaggerated heroic proportions — broader shoulders, defined musculature even on lean characters. "
    "Dynamic foreshortening and dramatic perspective. Cinematic action composition. "
    "Western comic book coloring — flat bold color areas separated by heavy black ink lines. "
    "Single panel illustration. "
    "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
)

COMIC_FACE_STYLE = (
    "Marvel comic book character reference sheet. VERY THICK bold black ink outlines. "
    "Rich saturated flat color fills — bold primaries, no soft gradients. "
    "Hard-edged shadows as solid black shapes. Crosshatching in shadow areas. "
    "Slightly heroic proportions — defined jawline, broader neck. "
    "Western Marvel comic coloring style. Like a character design from a Marvel series."
)

PROMPTS = {
    "comic_face_v3": {
        "prompt": f"""{COMIC_FACE_STYLE}

{FACE_TEXT}

Draw HEAD AND NECK ONLY on a clean white background.
Two views side by side: front-facing (left) and three-quarter angle (right).
NO clothing visible — cut off at base of neck / collarbone.
Render in full Marvel comic ink + color style — thick outlines, flat saturated fills, crosshatch shadows.
This is a character reference sheet.""",
        "aspect": "1:1",
    },
    "comic_action_v3": {
        "prompt": f"""{COMIC_STYLE}

FACE: {FACE_TEXT}

OUTFIT: Dark hoodie with the hood down, cargo pants, worn sneakers. Laptop bag slung across chest.

A young Korean man sprints through a neon-lit alley at night in a futuristic city. Rain pours down heavily.
Neon signs in Korean reflect off the wet pavement in streaks of vibrant color. He looks back over his
shoulder with an urgent, determined expression. His glasses catch the neon reflections. His messy hair
is wet, plastered to his forehead. Water splashes up from his footsteps.
Camera: dynamic dutch angle from low, motion blur on background, sharp focus on him.
Moody cyberpunk atmosphere with rain and neon.
Include a rectangular narration box at the bottom with dark semi-transparent background and white text: "그날 밤, 모든 것이 바뀌었다." """,
        "aspect": "2:3",
    },
    "comic_stage_v3": {
        "prompt": f"""{COMIC_STYLE}

FACE: {FACE_TEXT}

OUTFIT: Fitted black suit with thin tie and crisp white dress shirt.

A young Korean man stands on a grand stage, gripping a golden trophy with both hands raised above his head.
Bright spotlight beams down on him from above creating dramatic rim lighting. Golden confetti explodes around him.
Behind him, a massive LED screen displays "1st PLACE". His expression is pure triumphant shock — mouth open,
eyes wide behind his glasses, sweat on his brow. The crowd below is a sea of silhouettes with raised hands.
Camera: dramatic low angle looking up, emphasizing his heroic moment. Hard spotlight with lens flare.
Include a white speech bubble with thick black outline near his face containing: "진짜...요?" """,
        "aspect": "2:3",
    },
}

executor = ThreadPoolExecutor(max_workers=3)
sem = asyncio.Semaphore(3)


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
    tasks = [
        gen_async(name, p["prompt"], p["aspect"])
        for name, p in PROMPTS.items()
    ]
    print(f"Generating {len(tasks)} Marvel-style images...")
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
