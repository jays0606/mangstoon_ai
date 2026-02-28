"""
Test generation script — MangstoonAI prompt engineering test
Story: 찐따 개발자의 해커톤 우승 → 미국 비즈니스석 → 블랙핑크 지수 만남 → 연애
"""
import os
import sys
from google import genai
from google.genai import types

API_KEY = os.getenv("GOOGLE_API_KEY", "")
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.1-flash-image-preview"
OUTPUT_DIR = "output"

WEBTOON_CONFIG = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    image_config=types.ImageConfig(aspect_ratio="9:16"),
)

PROFILE_CONFIG = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    image_config=types.ImageConfig(aspect_ratio="1:1"),
)

# ── Style base prompt (locked across all panels) ──
STYLE = """Korean webtoon style illustration. Clean digital line art with smooth cel-shading.
Soft gradient coloring with vibrant accents. Large expressive eyes with detailed highlights.
Modern manhwa aesthetic. Single panel illustration, not a comic strip."""

# ── Character descriptions (locked across all panels) ──
CHAR_MC = """CHARACTER "민수": Korean man, mid-20s. Messy black hair falling over forehead,
slightly long. Sharp but tired eyes behind round thin-frame glasses. Slim build.
Wearing a black hoodie, jeans, and white sneakers. Slightly slouched developer posture.
Has dark circles under his eyes but a determined look."""

CHAR_JISOO = """CHARACTER "지수": Korean woman, late-20s. Long straight black hair past shoulders,
elegant and polished. Sharp cat-like eyes, high cheekbones, flawless skin.
Wearing a stylish beige trench coat over a black turtleneck. Confident, graceful posture.
Celebrity aura — effortlessly beautiful."""


def save_image(response, filename):
    """Extract and save image from response."""
    for part in response.parts:
        if part.text is not None:
            print(f"  Model says: {part.text[:100]}...")
        elif part.inline_data is not None:
            img = part.as_image()
            path = os.path.join(OUTPUT_DIR, filename)
            img.save(path)
            print(f"  Saved: {path}")
            return path
    return None


def generate_character_profiles():
    """Step 1: Generate character reference sheets (1:1 square)."""
    print("\n=== STEP 1: Character Profiles ===\n")

    # MC profile
    print("[1/2] Generating 민수 (MC) profile...")
    r = client.models.generate_content(
        model=MODEL,
        contents=f"""{CHAR_MC}

Create a character reference sheet for this Korean webtoon character.
Draw the character facing forward with a neutral expression on a clean white background.
Upper body portrait, centered. Korean webtoon style with clean line art and soft cel-shading.
This is a character reference — prioritize clarity and recognizable features.
Show the round glasses and messy hair clearly.""",
        config=PROFILE_CONFIG,
    )
    save_image(r, "char_minsu.png")

    # Jisoo profile
    print("[2/2] Generating 지수 profile...")
    r = client.models.generate_content(
        model=MODEL,
        contents=f"""{CHAR_JISOO}

Create a character reference sheet for this Korean webtoon character.
Draw the character facing forward with a slight confident smile on a clean white background.
Upper body portrait, centered. Korean webtoon style with clean line art and soft cel-shading.
This is a character reference — prioritize clarity and recognizable features.
Show the long straight black hair and elegant features clearly.""",
        config=PROFILE_CONFIG,
    )
    save_image(r, "char_jisoo.png")


def generate_panels():
    """Step 2: Generate story panels using multi-turn chat for consistency."""
    print("\n=== STEP 2: Story Panels (Multi-Turn Chat) ===\n")

    chat = client.chats.create(model=MODEL, config=WEBTOON_CONFIG)

    panels = [
        # Panel 1: 찐따 개발자 코딩
        {
            "file": "panel_01_coding.png",
            "prompt": f"""{STYLE}

{CHAR_MC}

SCENE: 민수 sits hunched over his laptop at the Google DeepMind Seoul hackathon venue.
The room is dimly lit by laptop screens. Empty energy drink cans and snack wrappers surround him.
His glasses reflect lines of code. He's typing furiously with an intense, desperate expression.
A large countdown timer on the wall behind shows "01:32:00" remaining.
Other hackers visible as silhouettes in the background.

Camera: Medium shot, slightly low angle to make him look determined despite being tired.
Mood: Tense, blue-tinted lighting with warm laptop glow on his face.
Leave empty space at top-right for a speech bubble."""
        },

        # Panel 2: 1등 발표
        {
            "file": "panel_02_winner.png",
            "prompt": f"""{STYLE}

{CHAR_MC}

SCENE: 민수 stands on stage at the hackathon, completely shocked. His mouth is open,
eyes wide behind his glasses. A spotlight shines on him. The big screen behind shows
"1st Place — MangstoonAI" in bold letters. Confetti is falling.
His laptop is still clutched under one arm. The audience is cheering (shown as silhouettes).
He looks like he can't believe this is happening.

Camera: Wide medium shot, dramatic stage lighting from above and sides.
Mood: Euphoric, warm golden stage lights with blue ambient background.
Include a white speech bubble near his mouth with the text: "진짜...요?"
dynamic composition with slight dutch angle for excitement."""
        },

        # Panel 3: 비즈니스석
        {
            "file": "panel_03_airplane.png",
            "prompt": f"""{STYLE}

{CHAR_MC}

SCENE: 민수 sits in a business class airplane seat, looking out the window with a
goofy satisfied grin. He's wearing the same black hoodie but now has a fancy neck pillow.
The seat is spacious and luxurious — wide leather seat, personal screen, champagne glass
on the armrest. Through the window, clouds and blue sky are visible.
He's taking a selfie with his phone, clearly not used to this luxury.

Camera: Medium close-up, warm cabin lighting.
Mood: Comedic happiness, warm amber interior light.
Leave space at bottom for narration box."""
        },

        # Panel 4: 지수 등장
        {
            "file": "panel_04_jisoo_appears.png",
            "prompt": f"""{STYLE}

{CHAR_MC}
{CHAR_JISOO}

SCENE: At the conference venue lobby. 민수 is walking with his backpack, looking at his phone,
when he looks up and freezes. 지수 (the elegant woman) walks past him in the lobby,
surrounded by a soft glow effect. She's on her phone too, looking effortlessly stylish.
민수's jaw has dropped, his glasses slightly askew. A few people in the background
are also glancing at 지수.

Camera: Medium shot, 민수 in foreground (right), 지수 walking past (left center).
Mood: Romantic comedy moment — 민수's side is cooler blue tones, 지수's side has warm golden light.
Cherry blossom petals or sparkle effects around 지수.
Include a small thought bubble near 민수 with "...?!" """
        },

        # Panel 5: 대화
        {
            "file": "panel_05_conversation.png",
            "prompt": f"""{STYLE}

{CHAR_MC}
{CHAR_JISOO}

SCENE: 민수 and 지수 are sitting across from each other at a small café table.
지수 is leaning forward with genuine interest, eyes bright, pointing at 민수's laptop screen.
민수 is explaining something about AI, gesturing with his hands, looking surprised and happy
that she's actually interested. His glasses are pushed up, he's animated.
Coffee cups on the table. The café has warm, cozy lighting.

Camera: Medium shot at table level, both characters visible, slight warm color grading.
Mood: Warm, intimate, surprised connection — soft golden café lighting.
Include a speech bubble from 지수: "AI로 이런 것도 돼요?"
Include a speech bubble from 민수: "네! 이게 진짜 재밌는 게..."
Romance modifier: warm golden-hour feel, dreamy soft background blur."""
        },

        # Panel 6: 연락처 교환
        {
            "file": "panel_06_phone_exchange.png",
            "prompt": f"""{STYLE}

{CHAR_MC}
{CHAR_JISOO}

SCENE: Close-up of two phones being held next to each other — exchanging contact info.
민수's hand (slightly trembling, you can see his hoodie sleeve) holds a phone showing a
chat app contact screen. 지수's hand (elegant, manicured nails) holds her phone.
In the blurred background, we can see them both smiling shyly.

Camera: Extreme close-up on the phones, shallow depth of field, background very blurry.
Mood: Heart-fluttering moment, warm pink and gold tones.
Small heart effect symbols floating around the phones.
Romance modifier: cherry blossom particles, soft lens flare."""
        },

        # Panel 7: 영상통화
        {
            "file": "panel_07_videocall.png",
            "prompt": f"""{STYLE}

{CHAR_MC}
{CHAR_JISOO}

SCENE: Split composition. Left side shows 민수 at his desk at night, messy room,
multiple monitors with code, talking to his phone propped up showing 지수's face on
video call. He's smiling warmly. Right side shows 지수 on a fancy hotel bed, hair
down casually, laughing at something he said, her phone showing 민수's face.
A visual line or gradient divides the two halves.

Camera: Split-screen composition, both shown in medium close-up.
Mood: Late night warmth, his side has blue monitor glow, her side has warm lamp light.
Both genuinely happy. Small floating hearts between the two halves."""
        },

        # Panel 8: 같이 걷는 장면 (ending)
        {
            "file": "panel_08_walking_together.png",
            "prompt": f"""{STYLE}

{CHAR_MC}
{CHAR_JISOO}

SCENE: 민수 and 지수 walking together on a Seoul street at sunset. She's slightly
taller in heels. He's still in his hoodie, she's in her trench coat. They're walking
close, shoulders almost touching, both looking at 민수's phone screen together and laughing.
Cherry blossom trees line the street. Seoul cityscape visible in the warm sunset background.
The scene has a beautiful golden hour glow.

Camera: Wide medium shot from behind, showing them walking away together, backlit by sunset.
Mood: Warm, romantic, hopeful — golden sunset tones, soft lens flare.
This is the final panel — make it feel like a happy ending.
Romance modifier: warm golden-hour backlighting, cherry blossom particles, dreamy atmosphere.
Leave space at bottom for narration text."""
        },
    ]

    for i, panel in enumerate(panels):
        print(f"[{i+1}/{len(panels)}] Generating {panel['file']}...")
        try:
            r = chat.send_message(panel["prompt"])
            save_image(r, panel["file"])
        except Exception as e:
            print(f"  ERROR: {e}")
            # If chat breaks, try standalone
            print("  Retrying as standalone call...")
            try:
                r = client.models.generate_content(
                    model=MODEL,
                    contents=panel["prompt"],
                    config=WEBTOON_CONFIG,
                )
                save_image(r, panel["file"])
            except Exception as e2:
                print(f"  STANDALONE ERROR: {e2}")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if "--panels-only" in sys.argv:
        generate_panels()
    elif "--profiles-only" in sys.argv:
        generate_character_profiles()
    else:
        generate_character_profiles()
        generate_panels()

    print("\n=== Done! Check output/ directory ===")
