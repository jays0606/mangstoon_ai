"""
V3 — Face-only character refs + clothing variation test
"""
import os
from google import genai
from google.genai import types
from PIL import Image

API_KEY = os.getenv("GOOGLE_API_KEY", "")
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.1-flash-image-preview"
OUTPUT = "output/v3"
os.makedirs(OUTPUT, exist_ok=True)

FACE_CONFIG = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    image_config=types.ImageConfig(aspect_ratio="1:1"),
)

PANEL_CONFIG = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    image_config=types.ImageConfig(aspect_ratio="9:16"),
)

STYLE = """Korean webtoon style illustration. Clean digital line art with smooth cel-shading.
Soft gradient coloring with vibrant accents. Large expressive eyes with detailed highlights.
Modern manhwa aesthetic. Single panel illustration.
The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."""

# Face-only descriptions (NO clothing)
FACE_MC = """FACE: Korean man, mid-20s. Messy black hair falling over forehead, slightly long.
Sharp but tired eyes behind round thin-frame glasses. Slim face with slight jaw.
Dark circles under eyes. Small mole near right ear. Gentle but awkward expression."""

FACE_JISOO = """FACE: Korean woman, late-20s. Long straight black hair past shoulders, center-parted.
Sharp cat-like eyes with double eyelids, high cheekbones, small nose, full lips.
Flawless clear skin. Elegant and confident expression. Celebrity-level beauty."""


def save(response, filename):
    for part in response.parts:
        if part.text:
            print(f"  {part.text[:80]}...")
        elif part.inline_data:
            img = part.as_image()
            path = os.path.join(OUTPUT, filename)
            img.save(path)
            print(f"  -> {path}")
            return path
    return None


# ════════════════════════════════════════
# STEP 1: Face-only refs (no clothing)
# ════════════════════════════════════════
print("=== STEP 1: Face-Only Refs ===\n")

print("[민수] face ref...")
r = client.models.generate_content(
    model=MODEL,
    contents=f"""{FACE_MC}

Character face reference sheet for Korean webtoon.
Draw this character's HEAD AND NECK ONLY on a clean white background.
Show two views side by side: front-facing view (left) and three-quarter angle view (right).
NO clothing visible — cut off at the base of the neck / collarbone.
Focus on capturing the distinctive facial features: messy hair, round glasses, tired eyes.
Korean webtoon style with clean line art and soft cel-shading.
This is a face reference for character consistency across panels.""",
    config=FACE_CONFIG,
)
save(r, "face_minsu.png")

print("[지수] face ref...")
r = client.models.generate_content(
    model=MODEL,
    contents=f"""{FACE_JISOO}

Character face reference sheet for Korean webtoon.
Draw this character's HEAD AND NECK ONLY on a clean white background.
Show two views side by side: front-facing view (left) and three-quarter angle view (right).
NO clothing visible — cut off at the base of the neck / collarbone.
Focus on capturing the distinctive facial features: sharp cat eyes, long black hair, high cheekbones.
Korean webtoon style with clean line art and soft cel-shading.
This is a face reference for character consistency across panels.""",
    config=FACE_CONFIG,
)
save(r, "face_jisoo.png")

# ════════════════════════════════════════
# STEP 2: 민수 in 4 different outfits
# using face ref image + outfit in prompt
# ════════════════════════════════════════
print("\n=== STEP 2: 민수 Outfit Variations (same face ref) ===\n")

minsu_ref = Image.open(os.path.join(OUTPUT, "face_minsu.png"))

minsu_outfits = [
    ("minsu_outfit1_hackathon.png",
     """OUTFIT: Worn black hoodie with the hood down, wrinkled grey t-shirt underneath, dark jeans,
     white sneakers. Looks like he's been coding for 12 hours straight.
     SCENE: 민수 sitting at a hackathon desk typing on laptop, surrounded by energy drinks.
     Dark room lit by laptop screens. Intense focused expression.
     Camera: medium shot, blue-tinted lighting with warm screen glow.
     Include speech bubble: "제발 돌아가라..." """),

    ("minsu_outfit2_suit.png",
     """OUTFIT: Fitted navy blue suit with thin black tie, white dress shirt, polished black shoes.
     Hair slightly more tidy than usual but still has that messy charm. Glasses same.
     SCENE: 민수 standing on stage at an awards ceremony, holding a trophy, looking shocked but happy.
     Spotlight on him, confetti falling. Crowd silhouettes cheering behind.
     Camera: full body medium shot, dramatic stage lighting.
     Include speech bubble: "진짜...요?" """),

    ("minsu_outfit3_casual.png",
     """OUTFIT: Oversized cream cable-knit sweater, brown chinos, white canvas shoes.
     Relaxed weekend look. Glasses same. Hair messy as always.
     SCENE: 민수 at a cozy café, leaning on the table with one hand, smiling warmly at someone
     across the table. Latte on the table. Warm golden afternoon light from window.
     Camera: medium close-up, warm tones.
     Include speech bubble: "그래서 그 AI가 진짜 재밌는 게..." """),

    ("minsu_outfit4_airplane.png",
     """OUTFIT: Comfortable grey zip-up travel hoodie, black jogger pants, neck pillow around neck.
     Looking cozy and relaxed. Glasses same.
     SCENE: 민수 in a business class airplane seat, grinning while taking a selfie.
     Champagne glass on armrest, window showing clouds. Luxury leather seat.
     Camera: medium shot, warm amber cabin lighting.
     Include speech bubble: "엄마 나 비즈니스석ㅋㅋㅋ" """),
]

for fname, outfit_prompt in minsu_outfits:
    print(f"[민수] {fname}...")
    try:
        r = client.models.generate_content(
            model=MODEL,
            contents=[
                minsu_ref,
                f"""Using the character face from the reference image, draw this EXACT same person
in a Korean webtoon panel. Match the face EXACTLY: same hair, same glasses, same facial features.
The CLOTHING is different from the reference — use the outfit described below.

{STYLE}
{FACE_MC}
{outfit_prompt}"""
            ],
            config=PANEL_CONFIG,
        )
        save(r, fname)
    except Exception as e:
        print(f"  ERROR: {e}")

# ════════════════════════════════════════
# STEP 3: 지수 in 4 different outfits
# ════════════════════════════════════════
print("\n=== STEP 3: 지수 Outfit Variations (same face ref) ===\n")

jisoo_ref = Image.open(os.path.join(OUTPUT, "face_jisoo.png"))

jisoo_outfits = [
    ("jisoo_outfit1_trench.png",
     """OUTFIT: Elegant beige trench coat over black turtleneck, black heels, small designer bag.
     Polished celebrity off-duty look.
     SCENE: 지수 walking through a hotel lobby, on her phone, looking effortlessly stylish.
     People in background glancing at her. Sparkle/glow effect around her.
     Camera: full body medium shot, warm golden lighting.
     Include thought text floating: "스케줄 끝나면 카페 가야지..." """),

    ("jisoo_outfit2_stage.png",
     """OUTFIT: Sparkling black sequin mini dress, high black boots, silver earrings.
     Full stage makeup, hair flowing. Performance look.
     SCENE: 지수 performing on a concert stage, microphone in hand, dynamic pose.
     Stage lights in blue and purple, crowd hands raised in background.
     Camera: low angle dynamic shot, dramatic concert lighting.
     Include speech bubble: "모두 소리 질러!!" """),

    ("jisoo_outfit3_casual.png",
     """OUTFIT: Simple white t-shirt, high-waisted blue jeans, white sneakers, baseball cap.
     Minimal makeup, hair in a low ponytail. Incognito casual look.
     SCENE: 지수 sitting on a park bench, eating ice cream, looking relaxed and happy.
     Trees and sunlight in background. Completely unguarded natural smile.
     Camera: medium shot, bright natural daylight.
     Include speech bubble: "아 이 맛이야~" """),

    ("jisoo_outfit4_cozy.png",
     """OUTFIT: Oversized light pink knit cardigan over white camisole, grey sweatpants.
     Hair down and slightly messy, no makeup. Cozy at-home look.
     SCENE: 지수 lying on a hotel bed, video-calling on her phone, laughing genuinely.
     Phone screen shows 민수's face. Warm bedside lamp lighting.
     Camera: medium close-up, warm intimate lighting.
     Include speech bubble: "ㅋㅋㅋ 진짜? 그래서 어떻게 됐어?" """),
]

for fname, outfit_prompt in jisoo_outfits:
    print(f"[지수] {fname}...")
    try:
        r = client.models.generate_content(
            model=MODEL,
            contents=[
                jisoo_ref,
                f"""Using the character face from the reference image, draw this EXACT same person
in a Korean webtoon panel. Match the face EXACTLY: same eyes, same hair style/color, same facial features.
The CLOTHING is different from the reference — use the outfit described below.

{STYLE}
{FACE_JISOO}
{outfit_prompt}"""
            ],
            config=PANEL_CONFIG,
        )
        save(r, fname)
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n=== V3 Done! Check output/v3/ ===")
