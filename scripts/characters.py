"""
Canonical character definitions for MangstoonAI.
Face refs stored in output/v3/face_*.png
"""

# ── Face-only descriptions (NO clothing — used in every panel prompt) ──

FACE_MINSU = """FACE "민수": Korean man, mid-20s. Messy black hair falling over forehead, slightly long.
Sharp but tired eyes behind round thin-frame glasses. Slim face with slight jaw.
Dark circles under eyes. Small mole near right ear. Gentle but awkward expression."""

FACE_JISOO = """FACE "지수": A breathtakingly beautiful Korean woman in her late 20s with the kind of face
that makes people stop and stare. Her long jet-black hair cascades past her shoulders
like silk, center-parted, each strand catching the light with a subtle blue-black sheen.
Her eyes are her most captivating feature — large, bright, slightly upturned at the
outer corners, framed by naturally long dark lashes. They have a warm depth to them
with multiple light reflections that make them sparkle. Her face is a perfect oval
with refined cheekbones, a small nose, and softly full lips curved in an almost-smile.
Her skin has a luminous, dewy quality — the kind that looks lit from within.
She radiates the effortless elegance of a Korean drama lead actress."""

# ── Face ref generation prompts ──

FACE_REF_PROMPT_MINSU = """Character face reference sheet for Korean webtoon.

{face_desc}

Draw HEAD AND NECK ONLY on a clean white background.
Two views side by side: front-facing (left) and three-quarter angle (right).
NO clothing visible — cut off at base of neck.
Focus on: messy hair, round glasses, tired eyes, dark circles.
Korean webtoon style, clean line art, soft cel-shading.
This is a face reference — prioritize clarity and recognizable features."""

FACE_REF_PROMPT_JISOO = """Character face reference sheet for Korean webtoon romance heroine.

{face_desc}

Draw HEAD AND NECK ONLY on clean white background.
Two views: front (left) and three-quarter angle looking slightly over shoulder (right).
NO clothing below collarbone.
Korean webtoon style. Clean line art, soft cel-shading.
Draw her as genuinely beautiful — big detailed eyes with sparkle, soft skin glow, elegant hair.
This is a character reference — prioritize clarity and beauty."""

# ── Style base (locked across ALL panels) ──

STYLE_WEBTOON = """Korean webtoon style illustration. Clean digital line art with smooth cel-shading.
Soft gradient coloring with vibrant accents. Large expressive eyes with detailed highlights.
Modern manhwa aesthetic. Single panel illustration.
The illustration must fill the ENTIRE frame edge-to-edge. No white borders or margins."""

# ── Test story ──

STORY_KR = """나는 찐따 개발자인데 딥마인드 서울에서 열린 해커톤 1등해서 미국 비즈니스석 타고 가서 발표함.
근데 블랙핑크 지수가 같은곳에 가서 공연을 함. 만나서 얘기하다가 생각보다 지수가 AI에 관심이 많아서
연락 주고받다가 연애를 하게 됨."""

# ── Ref image paths ──

FACE_REF_PATHS = {
    "minsu": "output/v3/face_minsu.png",
    "jisoo": "output/v3/face_jisoo.png",  # v2b — idol-level visual
}
