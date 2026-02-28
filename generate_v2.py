"""
V2 — Fixed: no white borders, speech bubbles on ALL panels
"""
import os
from google import genai
from google.genai import types

API_KEY = os.getenv("GOOGLE_API_KEY", "")
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.1-flash-image-preview"
OUTPUT = "output/v2"
os.makedirs(OUTPUT, exist_ok=True)

CONFIG = types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE'],
    image_config=types.ImageConfig(aspect_ratio="9:16"),
)

# ── Locked style prefix — same on every panel ──
STYLE = """Korean webtoon style illustration. Clean digital line art with smooth cel-shading.
Soft gradient coloring with vibrant accents. Large expressive eyes with detailed highlights.
Modern manhwa aesthetic. Single panel illustration.
IMPORTANT: The illustration must fill the ENTIRE frame edge-to-edge with NO white borders,
NO white margins, NO blank bars at top or bottom. The art extends to all edges of the image."""

CHAR_MC = """CHARACTER "민수": Korean man, mid-20s. Messy black hair falling over forehead.
Sharp tired eyes behind round thin-frame glasses. Slim build. Black hoodie, jeans, white sneakers.
Dark circles under eyes."""

CHAR_JISOO = """CHARACTER "지수": Korean woman, late-20s. Long straight black hair past shoulders.
Sharp cat-like eyes, high cheekbones. Beige trench coat over black turtleneck. Confident posture."""


def save(response, filename):
    for part in response.parts:
        if part.text:
            print(f"  Text: {part.text[:80]}...")
        elif part.inline_data:
            img = part.as_image()
            path = os.path.join(OUTPUT, filename)
            img.save(path)
            print(f"  Saved: {path}")
            return path
    return None


print("=== Generating V2 panels (multi-turn chat) ===\n")
chat = client.chats.create(model=MODEL, config=CONFIG)

panels = [
    # 1: 해커톤 코딩
    ("panel_01.png", f"""{STYLE}
{CHAR_MC}

SCENE: 민수 hunched over laptop at the DeepMind Seoul hackathon. Dark room lit by screens.
Empty energy drinks and wrappers around him. Glasses reflecting code. Typing furiously.
Countdown timer on wall: "01:32:00". Other hackers as silhouettes behind.
Camera: medium shot, slightly low angle. Blue-tinted lighting, warm laptop glow on face.

Include a white rounded speech bubble with black outline near 민수's mouth containing: "제발 돌아가라..."
Include a small thought bubble above his head containing: "남은 시간 1시간 반..." """),

    # 2: 1등 수상
    ("panel_02.png", f"""{STYLE}
{CHAR_MC}

SCENE: 민수 on stage, completely shocked. Mouth open, eyes wide behind glasses.
Spotlight on him. Screen behind: "1st Place — MangstoonAI". Confetti falling.
Laptop under one arm. Cheering crowd silhouettes. He can't believe it.
Camera: wide medium shot, dramatic stage lighting. Golden lights, blue ambient.
Dynamic slight dutch angle.

Include a speech bubble near 민수's mouth with: "진짜...요?"
Include a small narration box at very top with dark background and white text: "그렇게 인생이 바뀌었다." """),

    # 3: 비즈니스석
    ("panel_03.png", f"""{STYLE}
{CHAR_MC}

SCENE: 민수 in business class airplane seat with a goofy satisfied grin.
Same black hoodie with fancy neck pillow. Spacious leather seat, personal screen,
champagne glass on armrest. Clouds and blue sky through window.
Taking selfie with phone — clearly not used to luxury.
Camera: medium close-up, warm amber cabin lighting. Comedic happy mood.

Include a speech bubble near 민수's mouth containing: "엄마 나 비즈니스석ㅋㅋㅋ"
Include a small thought bubble: "이게 현실이야?" """),

    # 4: 지수 등장
    ("panel_04.png", f"""{STYLE}
{CHAR_MC}
{CHAR_JISOO}

SCENE: Conference venue lobby. 민수 walking with backpack, looks up and freezes.
지수 walks past him, surrounded by a soft glow. She's on her phone, effortlessly stylish.
민수's jaw dropped, glasses slightly askew. People in background glancing at 지수.
Camera: medium shot, 민수 right foreground, 지수 left center.
민수's side cooler blue, 지수's side warm golden. Sparkle effects around 지수.

Include a thought bubble near 민수 with: "...저 사람 혹시...?!"
Include floating text effect near 지수: "✨" """),

    # 5: 카페 대화
    ("panel_05.png", f"""{STYLE}
{CHAR_MC}
{CHAR_JISOO}

SCENE: 민수 and 지수 sitting across each other at a small café table.
지수 leaning forward with genuine interest, pointing at 민수's laptop screen.
민수 explaining about AI, gesturing, surprised and happy she's interested.
Coffee cups on table. Warm cozy café lighting.
Camera: medium shot at table level, both visible, warm color grading.

Include a speech bubble from 지수 (on left): "AI로 이런 것도 돼요?!"
Include a speech bubble from 민수 (on right): "네! 이게 진짜 재밌는 게..." """),

    # 6: 연락처 교환
    ("panel_06.png", f"""{STYLE}
{CHAR_MC}
{CHAR_JISOO}

SCENE: Close-up of two phones held next to each other, exchanging contacts.
민수's hand (trembling, hoodie sleeve visible) and 지수's hand (elegant, manicured).
Blurred background shows them both smiling shyly. Hearts floating around phones.
Camera: close-up on phones, shallow DOF, very blurry background.
Pink and gold tones, cherry blossom particles, soft lens flare.

Include a speech bubble from 민수 (nervous): "저... 혹시 연락처..."
Include a speech bubble from 지수 (smiling): "카톡 ID 알려줄게요 ㅎㅎ" """),

    # 7: 영상통화
    ("panel_07.png", f"""{STYLE}
{CHAR_MC}
{CHAR_JISOO}

SCENE: Split-screen composition divided by a diagonal line.
LEFT: 민수 at his desk at night, messy room, monitors with code, smiling warmly
at phone propped up showing 지수 on video call.
RIGHT: 지수 on hotel bed, hair down casually, laughing, phone showing 민수's face.
Blue monitor glow on his side, warm lamp on her side. Hearts between halves.

Include a speech bubble on 민수's side: "오늘 공연 어땠어?"
Include a speech bubble on 지수's side: "완전 좋았어! 근데 너 밥은 먹었어?" """),

    # 8: 같이 걷기 (엔딩)
    ("panel_08.png", f"""{STYLE}
{CHAR_MC}
{CHAR_JISOO}

SCENE: 민수 and 지수 walking together on a Seoul street at sunset.
Walking close, shoulders touching, both looking at 민수's phone and laughing.
Cherry blossom trees lining the street. Seoul skyline in warm sunset background.
Beautiful golden hour glow. They look happy together.
Camera: medium shot from slightly in front, showing both faces, backlit by sunset.
Warm romantic golden tones, cherry blossoms floating, dreamy atmosphere.

Include a speech bubble from 지수: "오빠 이거 봐 ㅋㅋㅋ"
Include a speech bubble from 민수: "뭐야 ㅋㅋㅋㅋ"
Include a narration box at very bottom with semi-transparent dark background: "그렇게, 망상이 현실이 되었다." """),
]

for i, (fname, prompt) in enumerate(panels):
    print(f"[{i+1}/{len(panels)}] {fname}...")
    try:
        r = chat.send_message(prompt)
        save(r, fname)
    except Exception as e:
        print(f"  ERROR: {e}")
        print("  Retrying standalone...")
        try:
            r = client.models.generate_content(model=MODEL, contents=prompt, config=CONFIG)
            save(r, fname)
        except Exception as e2:
            print(f"  FAIL: {e2}")

print("\n=== V2 Done! ===")
