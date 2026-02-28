"""
Test all 4 art styles with the same scene to compare visual output.
Generates one panel per style in parallel.
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
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "style_test"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── The 4 Style Definitions ──

STYLES = {
    "webtoon": {
        "name": "Korean Webtoon",
        "aspect_ratio": "9:16",
        "base_prompt": (
            "Korean webtoon style illustration. Clean digital line art with smooth cel-shading. "
            "Soft gradient coloring with vibrant accents. Large expressive eyes with detailed highlights. "
            "Modern manhwa aesthetic. Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
    },
    "manga": {
        "name": "Japanese Manga",
        "aspect_ratio": "3:4",
        "base_prompt": (
            "Japanese manga style black and white illustration. Bold ink lines with varying "
            "line weight. Screen-tone dot-pattern shading for mid-tones, cross-hatching for "
            "deep shadows. High contrast pure black and white. No color. Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
    },
    "comic": {
        "name": "American Comic",
        "aspect_ratio": "2:3",
        "base_prompt": (
            "American comic book style illustration. Bold ink outlines with varying line weight. "
            "Rich saturated colors with dramatic cel-shading and strong cast shadows. "
            "Dynamic figure work. Detailed crosshatching in shadow areas. Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
    },
    "cinematic": {
        "name": "Cinematic Manhwa",
        "aspect_ratio": "9:16",
        "base_prompt": (
            "Cinematic Korean manhwa style. Semi-realistic digital painting with detailed "
            "rendering. Dramatic cinematic lighting with volumetric effects. Rich deep color "
            "palette with glowing accent highlights. Detailed background environments. "
            "Painterly brushwork visible in shading. Epic composition. Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
    },
}

# ── Same scene for all styles ──

FACE = (
    "Korean man, mid-20s. Messy black hair falling over forehead, slightly long. "
    "Sharp but tired eyes behind round thin-frame glasses. Slim face with slight jaw. "
    "Dark circles under eyes. Small mole near right ear."
)

# 3 test scenes to compare across styles
SCENES = [
    {
        "id": "stage",
        "prompt_template": """{style}

FACE: {face}

OUTFIT: Fitted black suit with thin tie and crisp white dress shirt. Polished leather shoes.

A young Korean man stands on a grand stage, gripping a golden trophy with both hands.
Bright spotlight illuminates him from above. Confetti rains down. Behind him, a massive screen
displays "1st Place" in English and Korean. His expression is pure shock and disbelief — mouth
slightly open, eyes wide behind his glasses. Camera: low angle looking up at him, emphasizing
the dramatic moment. Warm golden stage lighting with lens flare.
Include a white speech bubble with rounded edges near his face containing: "진짜...요?" """,
    },
    {
        "id": "cafe",
        "prompt_template": """{style}

FACE: {face}

OUTFIT: Oversized cream cable-knit sweater, worn-out jeans, white sneakers.

A cozy rainy-day café scene. The young man sits at a window table, laptop open in front of him,
staring out at the rain-streaked glass. A half-finished latte sits beside his laptop. His
reflection is faintly visible in the window. Outside, blurred city lights glow through the rain.
His expression is pensive and melancholic, one hand on his chin. Camera: medium shot from
slightly left, warm interior lighting contrasting with cool blue rain outside.
Include a cloud-shaped thought bubble near his head containing: "이게 현실이면 좋겠다..." """,
    },
    {
        "id": "action",
        "prompt_template": """{style}

FACE: {face}

OUTFIT: Dark hoodie pulled up, cargo pants, combat boots. Laptop bag slung across chest.

The young man sprints through a neon-lit Tokyo alley at night. Rain pours down. Neon signs
in Japanese and Korean reflect off the wet pavement in streaks of pink, cyan, and orange.
He looks back over his shoulder with an urgent, determined expression. His glasses catch the
neon light. His hair is wet and plastered to his forehead. Camera: dynamic dutch angle,
motion blur on background, sharp focus on him. Moody cyberpunk atmosphere.
Include a rectangular narration box at bottom with dark semi-transparent background and white text: "그날 밤, 모든 것이 바뀌었다." """,
    },
]

executor = ThreadPoolExecutor(max_workers=4)
sem = asyncio.Semaphore(4)


def gen_sync(style_key: str, scene: dict) -> tuple[str, str, bytes | None]:
    """Generate one panel. Returns (style_key, scene_id, image_bytes)."""
    style = STYLES[style_key]
    prompt = scene["prompt_template"].format(style=style["base_prompt"], face=FACE)

    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(aspect_ratio=style["aspect_ratio"]),
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
            return (style_key, scene["id"], raw)

    return (style_key, scene["id"], None)


async def gen_async(style_key: str, scene: dict):
    async with sem:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, gen_sync, style_key, scene)


async def main():
    # Generate all combinations: 4 styles × 3 scenes = 12 images
    tasks = []
    for style_key in STYLES:
        for scene in SCENES:
            tasks.append(gen_async(style_key, scene))

    print(f"Generating {len(tasks)} images (4 styles × 3 scenes)...")
    results = await asyncio.gather(*tasks)

    success = 0
    for style_key, scene_id, img_bytes in results:
        if img_bytes:
            path = OUTPUT_DIR / f"{style_key}_{scene_id}.png"
            path.write_bytes(img_bytes)
            print(f"  ✓ {STYLES[style_key]['name']:20s} | {scene_id:8s} → {path.name}")
            success += 1
        else:
            print(f"  ✗ {STYLES[style_key]['name']:20s} | {scene_id:8s} → FAILED")

    print(f"\nDone: {success}/{len(tasks)} generated → {OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
