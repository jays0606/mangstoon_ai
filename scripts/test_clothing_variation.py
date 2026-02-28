"""
Test: Face-only refs + clothing variation per scene
Runs all panel generations in PARALLEL using asyncio + ThreadPoolExecutor
"""
import os
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Load .env from project root
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
MODEL = "gemini-3.1-flash-image-preview"
OUTPUT = ROOT / "output" / "v3"
OUTPUT.mkdir(parents=True, exist_ok=True)

FACE_CFG = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    image_config=types.ImageConfig(aspect_ratio="1:1"),
)
PANEL_CFG = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    image_config=types.ImageConfig(aspect_ratio="9:16"),
)

STYLE = """Korean webtoon style illustration. Clean digital line art with smooth cel-shading.
Soft gradient coloring with vibrant accents. Large expressive eyes with detailed highlights.
Modern manhwa aesthetic. Single panel illustration.
The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."""

FACE_MC = """FACE: Korean man, mid-20s. Messy black hair falling over forehead, slightly long.
Sharp but tired eyes behind round thin-frame glasses. Slim face with slight jaw.
Dark circles under eyes. Small mole near right ear."""

FACE_JISOO = """FACE: Korean woman, late-20s. Long straight black hair past shoulders, center-parted.
Sharp cat-like eyes with double eyelids, high cheekbones, small nose, full lips.
Flawless clear skin. Celebrity-level beauty."""

executor = ThreadPoolExecutor(max_workers=4)
semaphore = None  # set in main()


def save(response, filename):
    import base64
    for part in response.parts:
        if part.inline_data:
            # Save raw bytes to avoid PIL decode issues in parallel
            raw = part.inline_data.data
            if isinstance(raw, str):
                raw = base64.b64decode(raw)
            mime = part.inline_data.mime_type or "image/png"
            ext = "jpg" if "jpeg" in mime else "png"
            # Force .png filename but save actual format
            path = OUTPUT / filename
            with open(str(path), "wb") as f:
                f.write(raw)
            print(f"  OK  {filename} ({len(raw)//1024}KB)")
            return str(path)
    print(f"  WARN no image in {filename}")
    return None


def gen_image(contents, config, filename):
    """Synchronous call — will be run in thread pool."""
    try:
        r = client.models.generate_content(model=MODEL, contents=contents, config=config)
        return save(r, filename)
    except Exception as e:
        print(f"  ERR {filename}: {e}")
        return None


async def gen_async(contents, config, filename):
    """Async wrapper around sync API call, with semaphore to limit concurrency."""
    async with semaphore:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, gen_image, contents, config, filename)


async def main():
    global semaphore
    semaphore = asyncio.Semaphore(4)  # max 4 concurrent API calls

    # ── Step 1: Face refs (must complete before panels) ──
    print("=== STEP 1: Face-Only Refs (parallel) ===\n")

    face_tasks = [
        gen_async(
            f"""{FACE_MC}

Character face reference sheet for Korean webtoon.
HEAD AND NECK ONLY on clean white background.
Two views side by side: front-facing (left) and three-quarter angle (right).
NO clothing visible — cut off at base of neck.
Focus on: messy hair, round glasses, tired eyes, dark circles.
Korean webtoon style, clean line art, soft cel-shading.""",
            FACE_CFG, "face_minsu.png"
        ),
        gen_async(
            f"""{FACE_JISOO}

Character face reference sheet for Korean webtoon.
HEAD AND NECK ONLY on clean white background.
Two views side by side: front-facing (left) and three-quarter angle (right).
NO clothing visible — cut off at base of neck.
Focus on: sharp cat eyes, long black hair, high cheekbones, elegant features.
Korean webtoon style, clean line art, soft cel-shading.""",
            FACE_CFG, "face_jisoo.png"
        ),
    ]
    await asyncio.gather(*face_tasks)

    # Load refs as PIL images (re-open saved bytes)
    minsu_ref = Image.open(str(OUTPUT / "face_minsu.png"))
    jisoo_ref = Image.open(str(OUTPUT / "face_jisoo.png"))
    # Ensure they're fully loaded into memory
    minsu_ref.load()
    jisoo_ref.load()

    # ── Step 2: All outfit panels in parallel ──
    print("\n=== STEP 2: Outfit Variations (ALL parallel) ===\n")

    def minsu_panel(fname, outfit_scene):
        return gen_async(
            [minsu_ref, f"""Using the character face from the reference image, draw this EXACT same person.
Match the face EXACTLY: same hair, same glasses, same facial features.
The CLOTHING is DIFFERENT from the reference — use the outfit described below.

{STYLE}
{FACE_MC}
{outfit_scene}"""],
            PANEL_CFG, fname
        )

    def jisoo_panel(fname, outfit_scene):
        return gen_async(
            [jisoo_ref, f"""Using the character face from the reference image, draw this EXACT same person.
Match the face EXACTLY: same eyes, same hair, same facial features.
The CLOTHING is DIFFERENT from the reference — use the outfit described below.

{STYLE}
{FACE_JISOO}
{outfit_scene}"""],
            PANEL_CFG, fname
        )

    all_panels = [
        # ── 민수 4 outfits ──
        minsu_panel("minsu_01_hackathon.png", """
OUTFIT: Worn black hoodie (hood down), wrinkled grey t-shirt underneath, dark jeans, white sneakers.
SCENE: Sitting at hackathon desk typing on laptop, energy drinks scattered. Dark room, laptop glow.
Camera: medium shot, blue lighting with warm screen glow.
Include speech bubble: "제발 돌아가라..." """),

        minsu_panel("minsu_02_suit.png", """
OUTFIT: Fitted navy blue suit, thin black tie, white dress shirt, polished black shoes.
Hair slightly tidier but still messy. Same glasses.
SCENE: Standing on stage holding trophy, shocked but happy. Spotlight, confetti, crowd behind.
Camera: full body shot, dramatic stage lighting.
Include speech bubble: "진짜...요?" """),

        minsu_panel("minsu_03_casual.png", """
OUTFIT: Oversized cream cable-knit sweater, brown chinos, white canvas shoes. Relaxed weekend look.
SCENE: At a cozy café, leaning on table, smiling warmly at someone across. Latte on table, golden light.
Camera: medium close-up, warm tones.
Include speech bubble: "그래서 그 AI가 진짜 재밌는 게..." """),

        minsu_panel("minsu_04_travel.png", """
OUTFIT: Grey zip-up travel hoodie, black jogger pants, neck pillow. Cozy travel look.
SCENE: In business class seat, grinning, taking selfie. Champagne, clouds in window.
Camera: medium shot, warm amber cabin lighting.
Include speech bubble: "엄마 나 비즈니스석ㅋㅋㅋ" """),

        # ── 지수 4 outfits ──
        jisoo_panel("jisoo_01_trench.png", """
OUTFIT: Elegant beige trench coat over black turtleneck, black heels, small designer bag.
SCENE: Walking through hotel lobby, on phone, effortlessly stylish. People glancing, sparkle effect.
Camera: full body medium shot, warm golden lighting.
Include floating thought: "스케줄 끝나면 카페 가야지..." """),

        jisoo_panel("jisoo_02_stage.png", """
OUTFIT: Sparkling black sequin mini dress, high black boots, silver earrings. Stage makeup, hair flowing.
SCENE: Performing on concert stage, mic in hand, dynamic pose. Blue/purple lights, crowd hands raised.
Camera: low angle dynamic shot, dramatic concert lighting.
Include speech bubble: "모두 소리 질러!!" """),

        jisoo_panel("jisoo_03_casual.png", """
OUTFIT: Simple white t-shirt, high-waisted blue jeans, white sneakers, baseball cap.
Minimal makeup, hair in low ponytail. Incognito casual.
SCENE: On park bench eating ice cream, relaxed natural smile. Trees, sunlight.
Camera: medium shot, bright natural daylight.
Include speech bubble: "아 이 맛이야~" """),

        jisoo_panel("jisoo_04_cozy.png", """
OUTFIT: Oversized light pink knit cardigan over white camisole, grey sweatpants.
Hair messy, no makeup. At-home cozy look.
SCENE: On hotel bed, video-calling, laughing genuinely. Warm bedside lamp.
Camera: medium close-up, warm intimate lighting.
Include speech bubble: "ㅋㅋㅋ 진짜? 그래서 어떻게 됐어?" """),
    ]

    await asyncio.gather(*all_panels)
    print(f"\n=== Done! {len(all_panels)} panels in output/v3/ ===")


if __name__ == "__main__":
    asyncio.run(main())
