# MangstoonAI — AI 망상툰 Generator

> *"나는 딥마인드 해커톤 1등해서 비즈니스석 타고 미국 가서 블랙핑크 지수 만나서 연애함"*
> — Your delusion, now a webtoon.

**Gemini 3 Seoul Hackathon | February 28, 2026 | Entertainment Track**

---

## What is this?

MangstoonAI turns your wildest fantasies into scroll-style Korean webtoons — instantly.

Type your delusion, and watch as AI generates a full 20+ panel webtoon where **you** are the main character. Then chat with the AI to edit any panel in real-time.

---

## Tech Stack

| Component | Technology | Role |
|-----------|-----------|------|
| **Framework** | **Google ADK** | Agent orchestration, tool management, session state |
| **Orchestrator** | **Gemini 3.1 Pro** (low thinking) | Directs flow, calls tools, chats with user |
| **Storyboard** | **Gemini 3.1 Pro** (medium thinking) | Structured JSON storyboard from user fantasy |
| **Prompt Optimizer** | **Gemini 3 Flash** (minimal thinking) | Crafts optimized image prompts from panel metadata |
| **Image Generation** | **Gemini 3.1 Flash Image** | Webtoon panel image generation (9:16 vertical) |
| **Dev UI** | **ADK Web** (`adk web`) | Browser UI for testing + demo |
| **Backend Hosting** | **Cloud Run** (Seoul) | FastAPI server, auto-deploys on push to main |
| **Image Storage** | **GCS** (`mangstoon-panels`) | Public URLs, Seoul region CDN |
| **CI/CD** | **GitHub Actions** + WIF | Push to main → Cloud Run deploy (backend) |
| **Frontend Hosting** | **Vercel** | Next.js, auto-deploys on push to main |
| **Language** | Python 3.12+ | |

---

## Architecture

```
[User Input: Story Text]
        │
        ▼
[decompose_story]  →  22-panel storyboard (JSON)
        │                characters with face_description (permanent)
        │                panels with scene, outfit (varies), dialogue, camera, mood
        ▼
[User approves storyboard]
        │
        ▼
[generate_panel × 22]  →  for each panel:
        │                    1. Flash optimizes image prompt (face + outfit + scene → narrative paragraph)
        │                    2. Flash Image generates panel (9:16, edge-to-edge, speech bubbles)
        ▼
[Webtoon Output]  →  22 panels in scroll format
        │
        ▼
[User: "5번 패널 배경을 한강으로"]
        │
        ▼
[edit_panel(5, "한강 배경")]  →  regenerate panel 5 only
```

---

## Image Prompt Engineering

The core innovation is a **2-step prompt pipeline** for each panel:

### Step 1: Prompt Optimizer (Flash, minimal thinking)

Takes structured metadata → crafts a narrative image prompt following proven rules:

- **Narrative paragraphs** not keyword lists
- **Face/outfit separation** — face is permanent identity, outfit varies per scene
- **Edge-to-edge rendering** — explicit instruction prevents white bar artifacts
- **Korean speech bubbles** — rendered directly in image, under 15 words
- **Camera terminology** — close-up, medium shot, dutch angle, bird's eye
- **Beauty descriptors** for attractive characters — "idol-level visual", "luminous skin with dewy glow"

### Step 2: Image Generator (Flash Image)

```python
config = types.GenerateContentConfig(
    response_modalities=["TEXT", "IMAGE"],
    image_config=types.ImageConfig(aspect_ratio="9:16"),
)
```

### Character Consistency

The hardest problem in sequential art generation. Our approach:

1. **Face-only reference sheets** (1:1 square, head+neck, no clothing)
2. **Face description text** anchored in every panel prompt (same text, every call)
3. **Outfit described separately** per scene — prevents "same clothes for 22 panels"
4. **Multi-turn chat** with Thought Signatures for tightest consistency (sequential panels)

### 4 Art Styles

Style definitions live in `backend/mangstoon_ai/styles.py` (single source of truth). The `style` parameter is threaded through all tools and API endpoints.

| Style ID | Name | Aspect Ratio | Best For |
|----------|------|-------------|----------|
| `k-webtoon` (default) | Korean Webtoon | 9:16 | Romance, slice-of-life, comedy |
| `anime` | Japanese Anime | 3:4 | Anime, action, shōnen/shōjo |
| `comic` | American Comic | 2:3 | Superhero, sci-fi, noir |
| `cinematic` | Cinematic Manhwa | 9:16 | Fantasy, power-fantasy, thriller |

Full prompting reference: `.claude/skills/gemini-panel-art.md`

---

## ADK Agent Structure

```
mangstoon_ai/
├── agent.py              # root_agent (Gemini 3.1 Pro, 4 tools)
├── tools/
│   ├── story_engine.py   # decompose_story() — text → 22-panel JSON storyboard
│   ├── image_gen.py      # generate_panel() — 2-step: optimize prompt → gen image
│   ├── panel_editor.py   # edit_panel() — 2-step: edit prompt → regen image
│   └── character.py      # extract_character() — selfie description → face template
└── prompts/
    └── system.py         # 3-phase director: Brainstorm → Generate → Edit
```

### 3-Phase Director Flow

1. **BRAINSTORM** — `decompose_story()` generates storyboard, user reviews/edits
2. **GENERATE** — `generate_panel()` for each panel after user approves
3. **EDIT** — `edit_panel()` for targeted panel edits via chat

---

## Quick Start

```bash
# Install
pip install google-adk

# Set API key
echo "GOOGLE_API_KEY=your_key" > backend/.env

# ADK dev UI (hackathon demo)
cd backend && uv run --project .. adk web --port 8080
# → http://localhost:8080/dev-ui/  →  select mangstoon_ai

# FastAPI backend
cd backend && ./run.sh

# Frontend
cd frontend && npm run dev
```

### Production

```
Backend:  https://mangstoon-backend-qlxchgmpvq-du.a.run.app
Images:   https://storage.googleapis.com/mangstoon-panels/{session}/panel_01.png
```

CI/CD: push to `main` → GitHub Actions → Cloud Run (backend) + Vercel (frontend) auto-deploy.

---

## Judging Strategy

| Criteria | Weight | Our Approach |
|----------|--------|-------------|
| **Demo** | 50% | `adk web` chat → type delusion → storyboard → panels generate → edit via chat |
| **Impact** | 25% | $5B webtoon market + personalization. Everyone with a phone and a fantasy. |
| **Creativity** | 15% | "망상툰" — culturally Korean, universally relatable. First delusion-to-webtoon. |
| **Pitch** | 10% | Meta: *"If we win this hackathon, this webtoon becomes real."* |

---

## Why This Wins

1. **Seoul = Webtoon capital.** Judges get it instantly.
2. **망상 = universal.** Everyone has a fantasy → webtoon is magic.
3. **Demo-first.** Visual output that makes people laugh.
4. **Gemini-native.** Pro (reasoning) + Flash Image (generation) = impossible without Gemini.
5. **ADK showcase.** Multi-tool agent + session state = what Google wants developers building.
6. **Meta.** Presenting a webtoon about winning the hackathon, at the hackathon.

---

*Built with delusions at Gemini 3 Seoul Hackathon, Feb 28 2026*
*Powered by Google ADK + Gemini 3.1 Pro + Gemini 3.1 Flash Image*
