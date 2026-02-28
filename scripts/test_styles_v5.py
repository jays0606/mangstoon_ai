"""
Test v5: Bright scene to expose style differences. Dark scenes make everything converge.
Two scenes: one bright (stage win), one emotional (cafe). Same character, 4 styles each.
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
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "style_test_v5"
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
            "Korean webtoon style illustration in the style of True Beauty (여신강림) and Lore Olympus. "
            "Clean THIN digital line art with smooth soft cel-shading and NO hard shadows. "
            "PASTEL color palette — soft pinks, lavender, cream, baby blue, warm peach. NO saturated or dark colors. "
            "Large sparkling manhwa eyes taking up 1/3 of the face, with heart-shaped light reflections in irises. "
            "Skin rendered impossibly smooth with visible pink blush patches on cheeks and nose. "
            "Soft dreamy background with watercolor wash effect and floating sparkle particles. "
            "Everything looks PRETTY, SOFT, and ROMANTIC — like a shoujo manga cover. "
            "Thin delicate line weight throughout. Soft diffused lighting with no harsh shadows. "
            "Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
    },
    "anime": {
        "name": "Japanese Anime",
        "aspect_ratio": "9:16",
        "style_prompt": (
            "Japanese anime illustration in the style of Makoto Shinkai films (Your Name, Suzume) and ufotable animation. "
            "HYPER-SATURATED vivid colors pushed to maximum — electric neon blues, hot magentas, burning oranges, "
            "glowing cyans. Colors should look like they're GLOWING from within. "
            "Dramatic cinematic lighting with visible god-rays, lens flares, floating light particles, and bloom effects. "
            "Very large detailed anime eyes with MULTIPLE layered catchlights, gradient rainbow irises, and sparkle effects. "
            "Ultra-detailed background rivaling a Shinkai film — every surface has texture, reflections, light interaction. "
            "Glossy shiny rendering on hair with colored specular highlights (blue/purple sheen on black hair). "
            "Strong rim lighting on character edges. Dramatic color contrast — warm vs cool light sources. "
            "ANIME proportions — slightly elongated, large head-to-body ratio, expressive. "
            "Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
    },
    "comic": {
        "name": "Marvel Comic",
        "aspect_ratio": "2:3",
        "style_prompt": (
            "Marvel Comics art style by Jim Lee and J. Scott Campbell. "
            "EXTREMELY THICK bold black ink outlines — 3-4x thicker than any manga or webtoon line. "
            "Flat BOLD saturated color fills with ZERO gradients — pure flat color areas like classic comic printing. "
            "Colors: strong primary RED, BLUE, YELLOW dominance. Pop art level saturation. "
            "HARD BLACK shadow shapes — shadows are pure solid black areas with sharp geometric edges, NOT soft. "
            "Dense crosshatching ink texture in ALL mid-tone and shadow areas — visible parallel ink lines. "
            "Ben-Day dot halftone pattern visible in lighter areas (like classic comic book printing). "
            "HEROIC proportions — shoulders 3x wider than head, defined muscles visible through clothing. "
            "Exaggerated dynamic poses — even standing looks like an action pose. "
            "Speed lines, impact marks, and motion effects. "
            "Square confident jawline on all characters regardless of build. "
            "Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
    },
    "cinematic": {
        "name": "Cinematic Manhwa",
        "aspect_ratio": "9:16",
        "style_prompt": (
            "Cinematic Korean manhwa in the style of Solo Leveling (나 혼자만 레벨업) art by DUBU (장성락). "
            "ZERO line art — this is purely a DIGITAL PAINTING. No visible outlines or ink lines anywhere. "
            "Semi-photorealistic rendering — faces and bodies look almost like stylized photographs. "
            "DARK moody atmosphere — even bright scenes have deep shadows and desaturated midtones. "
            "Dramatic volumetric lighting: strong single directional light source, deep shadows, rim light glow. "
            "Color palette: DARK — navy, charcoal, deep purple as base. Glowing ACCENT colors: electric blue, "
            "amber gold, neon purple on edges and highlights only. Midtones are desaturated and muted. "
            "Visible oil-painting brushstroke texture in skin, clothing folds, and backgrounds. "
            "Photorealistic proportions — NO anime eyes, NO exaggeration. Mature realistic faces. "
            "Background environments painted with cinematic depth of field — sharp foreground, soft background. "
            "Film color grading — teal-and-orange or cold-blue tone shift across entire image. "
            "Single panel illustration. "
            "The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."
        ),
    },
}

# BRIGHT scene — style differences can't hide in darkness
SCENE_BRIGHT = """
FACE: {face}

OUTFIT: Fitted black suit with thin tie and crisp white dress shirt. Polished leather shoes.

A young Korean man stands center stage at a huge tech conference, holding a golden trophy high above
his head with both hands. He's grinning with pure joy and disbelief — eyes squeezed shut from smiling so hard,
tears of happiness streaming down his cheeks. Bright white spotlight from directly above creates
a halo of light around him. Golden confetti rains down everywhere. Behind him, a massive LED screen
shows "GRAND PRIZE WINNER" in bold text. The audience is a blur of clapping silhouettes below the stage.
Camera: medium shot from slightly below, capturing his full upper body and the trophy, bright stage lighting.
Include a white speech bubble with rounded edges near his face containing: "엄마 나 1등했어!!"
"""

# CALM scene — emotional, intimate, shows how each style handles subtlety
SCENE_CALM = """
FACE: {face}

OUTFIT: Oversized cream cable-knit sweater, sleeves pulled over his hands.

A young Korean man sits alone on a park bench under a large cherry blossom tree in full bloom.
Soft pink petals drift down around him. He's looking up at the sky with a peaceful, content smile,
holding a warm coffee cup in both hands. Sunlight filters through the blossoms creating dappled
light patterns on his face and sweater. A gentle breeze ruffles his messy hair. The park stretches
out behind him with green grass and distant trees.
Camera: medium close-up from slightly right, warm golden hour sunlight, shallow depth of field.
Include a cloud-shaped thought bubble near his head containing: "이 순간이 영원하면 좋겠다"
"""

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
        # Bright stage scene
        bright = style["style_prompt"] + "\n" + SCENE_BRIGHT.format(face=FACE_TEXT)
        tasks.append(gen_async(f"{key}_bright", bright, style["aspect_ratio"]))

        # Calm cherry blossom scene
        calm = style["style_prompt"] + "\n" + SCENE_CALM.format(face=FACE_TEXT)
        tasks.append(gen_async(f"{key}_calm", calm, style["aspect_ratio"]))

    print(f"Generating {len(tasks)} images (4 styles × 2 scenes)...")
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
