"""Test better face prompting for 지수 — more attractive character design."""
import os, asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from google import genai
from google.genai import types

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

executor = ThreadPoolExecutor(max_workers=4)
sem = None

def save(response, filename):
    import base64
    for part in response.parts:
        if part.inline_data:
            raw = part.inline_data.data
            if isinstance(raw, str):
                raw = base64.b64decode(raw)
            path = OUTPUT / filename
            with open(str(path), "wb") as f:
                f.write(raw)
            print(f"  OK  {filename} ({len(raw)//1024}KB)")
            return str(path)
    return None

def gen_sync(contents, config, filename):
    try:
        r = client.models.generate_content(model=MODEL, contents=contents, config=config)
        return save(r, filename)
    except Exception as e:
        print(f"  ERR {filename}: {e}")
        return None

async def gen(contents, config, filename):
    async with sem:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, gen_sync, contents, config, filename)

# 3 variations of 지수 face ref with increasingly better beauty prompting
FACES = [
    ("face_jisoo_v2a.png", """Character face reference sheet for Korean webtoon.

FACE: Strikingly beautiful Korean woman, late-20s. Long flowing silky straight black hair
past shoulders, center-parted with subtle layering that frames the face elegantly.
Large expressive almond-shaped eyes with double eyelids, long curved lashes,
and multiple sparkling light reflections in dark brown irises — eyes that draw you in.
Perfectly balanced V-line jawline tapering to a delicate chin. High sculpted cheekbones
with a natural soft shadow beneath. Small refined nose with a gentle slope.
Naturally full lips with a subtle knowing smile that's both warm and captivating.
Flawless luminous porcelain skin with a soft dewy glow.
She has the visual beauty and charisma of a top Korean idol — effortlessly stunning.

Draw HEAD AND NECK ONLY on a clean white background.
Two views: front-facing (left) and elegant three-quarter angle (right).
NO clothing below collarbone.
Korean webtoon style with clean line art and soft cel-shading.
Emphasize the beauty: detailed eye reflections, soft skin rendering, elegant hair flow.
This is a character reference sheet — prioritize clarity and beauty."""),

    ("face_jisoo_v2b.png", """Character face reference sheet for Korean webtoon.

FACE: A breathtakingly beautiful Korean woman in her late 20s with the kind of face
that makes people stop and stare. Her long jet-black hair cascades past her shoulders
like silk, center-parted, each strand catching the light with a subtle blue-black sheen.
Her eyes are her most captivating feature — large, bright, slightly upturned at the
outer corners, framed by naturally long dark lashes. They have a warm depth to them
with multiple light reflections that make them sparkle. Her face is a perfect oval
with refined cheekbones, a small nose, and softly full lips curved in an almost-smile.
Her skin has a luminous, dewy quality — the kind that looks lit from within.
She radiates the effortless elegance of a Korean drama lead actress.

Draw HEAD AND NECK ONLY on clean white background.
Two views: front (left) and three-quarter angle looking slightly over shoulder (right).
NO clothing below collarbone.
Korean webtoon style. Clean line art, soft cel-shading.
Draw her as genuinely beautiful — this character needs to look like the love interest
in a romance webtoon. Big detailed eyes with sparkle. Soft skin glow. Elegant hair."""),

    ("face_jisoo_v2c.png", """Character face reference sheet for Korean webtoon romance heroine.

Draw a stunningly beautiful Korean woman for a romance webtoon. She should be
the kind of character that readers fall in love with at first sight.

FACE DETAILS:
- HAIR: Long flowing black hair past shoulders, silky and slightly wavy at the ends,
  center-parted. Individual strands visible, catching light beautifully.
- EYES: Large luminous almond eyes, double eyelids, dark brown irises with warm depth.
  Multiple light reflections making them sparkle. Long natural lashes.
  Slightly gentle, slightly playful expression in the eyes.
- FACE SHAPE: Elegant oval face, V-line jaw, high cheekbones with natural contour.
- NOSE: Small, refined, delicate.
- LIPS: Naturally full, soft pink tint, curved in a subtle captivating smile.
- SKIN: Flawless, luminous, dewy porcelain glow.
- VIBE: Top Korean actress beauty. Think the most beautiful woman you've ever drawn.

HEAD AND NECK ONLY. Clean white background.
Front view (left) and three-quarter view with slight head tilt (right).
NO clothing below collarbone.
Korean webtoon style — clean line art, soft cel-shading, detailed eye rendering.
Make her BEAUTIFUL. This is the female lead of a romance webtoon."""),
]

async def main():
    global sem
    sem = asyncio.Semaphore(3)

    print("=== Generating 3 variations of 지수 face ref ===\n")
    tasks = [gen(prompt, FACE_CFG, fname) for fname, prompt in FACES]
    await asyncio.gather(*tasks)

    # Also generate one test panel with the best one to verify outfit works
    print("\n=== Test panel with each face ref ===\n")
    from PIL import Image

    panel_tasks = []
    for fname, _ in FACES:
        ref_path = OUTPUT / fname
        if not ref_path.exists():
            continue
        ref = Image.open(str(ref_path))
        ref.load()
        panel_fname = fname.replace("face_", "test_panel_")

        panel_tasks.append(gen(
            [ref, f"""Using the character face from the reference image, draw this EXACT same person.
Match the face EXACTLY. The CLOTHING is different — use outfit below.

Korean webtoon style illustration. Clean line art, soft cel-shading.
Single panel. Fill entire frame edge-to-edge. No white borders.

OUTFIT: Elegant beige trench coat over black turtleneck, black heels.
Polished celebrity off-duty look.

SCENE: Walking through a luxury hotel lobby, phone in one hand, looking effortlessly
stunning. People glancing at her. Warm golden lighting, sparkle effects around her.
Camera: full body medium shot.
Include thought bubble: "스케줄 끝나면 카페 가야지..." """],
            PANEL_CFG, panel_fname
        ))

    if panel_tasks:
        await asyncio.gather(*panel_tasks)

    print("\n=== Done! ===")

if __name__ == "__main__":
    asyncio.run(main())
