# MangstoonAI — CLAUDE.md

AI 망상툰 generator. Gemini 3 Seoul Hackathon, Feb 28 2026.

---

## Project Structure

```
gemini-hackathon/
├── CLAUDE.md
├── README.md
├── docs/
│   ├── hackathon-info.md         # Schedule, rules, judging, prizes
│   ├── gemini-3.md               # Gemini 3.1 Pro/Flash API reference
│   ├── nano-banana-image-generation.md  # Image gen API + prompting
│   ├── adk-llms.txt              # ADK Python SDK reference
│   └── prompt-design.md          # Gemini prompting best practices
├── backend/
│   ├── .env                      # GOOGLE_API_KEY
│   ├── main.py                   # FastAPI app
│   ├── requirements.txt
│   └── mangstoon_ai/             # ADK agent package
│       ├── __init__.py
│       ├── agent.py              # root_agent definition
│       ├── tools/
│       │   ├── story_engine.py   # decompose_story()
│       │   ├── image_gen.py      # generate_panel()
│       │   ├── panel_editor.py   # edit_panel()
│       │   └── character.py      # extract_character()
│       └── prompts/
│           └── system.py
└── frontend/                     # Next.js app (deploy to Vercel)
    ├── app/
    │   ├── page.tsx
    │   ├── components/
    │   │   ├── StoryInput.tsx
    │   │   ├── WebtoonViewer.tsx
    │   │   └── ChatEditor.tsx
    │   └── api/
    │       ├── generate/route.ts  # → backend:8000/generate
    │       └── edit/route.ts      # → backend:8000/edit
    └── .env.local                 # BACKEND_URL=http://localhost:8000
```

---

## API Keys & Environment

```bash
# backend/.env
GOOGLE_API_KEY=AIzaSyDyLmhnzR1swTwq7zczzkRzL7_1VtMctVI
```

ADK reads `.env` from the directory you run `adk web` from — run it from `backend/`.

---

## Models

| Purpose | Model ID |
|---------|----------|
| Story engine / orchestrator | `gemini-3.1-pro-preview` |
| Panel image generation | `gemini-3.1-flash-image-preview` |

**Do NOT use** `gemini-3-pro-preview` — deprecated, shuts down March 9.

---

## Tech Stack

- **Framework**: Google ADK (`pip install google-adk`)
- **Language**: Python 3.12+
- **Image Gen**: Gemini 3.1 Flash Image (`gemini-3.1-flash-image-preview`)
- **Orchestrator**: Gemini 3.1 Pro (`gemini-3.1-pro-preview`)
- **Dev UI**: `adk web` at `localhost:8000` — **mandatory for hackathon demo**
- **Frontend**: Custom React/Next.js or plain HTML — **separate from adk web**

---

## Running Locally

```bash
# Install
pip install google-adk fastapi uvicorn pillow

# ADK dev UI (mandatory demo) — run from backend/
cd backend
adk web
# → localhost:8000, select "mangstoon_director"

# FastAPI backend
cd backend
uvicorn main:app --reload --port 8000

# Next.js frontend
cd frontend
npm run dev
# → localhost:3000
```

---

## Task Division

### AI (do first — P0)
- ADK agent scaffold (`backend/mangstoon_ai/agent.py`)
- `decompose_story()` tool — text → 6-8 panel descriptions
- `generate_panel()` tool — Gemini Flash Image integration
- `edit_panel()` tool — targeted panel regeneration
- `extract_character()` tool — selfie → character prompt template
- Session state: panels + character_description across turns

### BE (glue layer)
- Parallel `generate_panel` calls (fire all simultaneously)
- Panel state management (store generated images)
- API serving for FE (FastAPI or simple endpoints)

### FE (custom UI — separate from adk web)
- Vertical scroll webtoon viewer
- Speech bubble overlays on panels
- Selfie upload + story input form
- Chat interface for panel editing
- Progressive panel loading (panels appear as they generate)
- Mobile-first

---

## Priority Stack

```
P0 — MUST:   decompose_story + generate_panel (text → webtoon works)
P1 — SHOULD: edit_panel (chat → panel edit)
P2 — NICE:   extract_character (selfie integration)
P3 — NICE:   custom FE (adk web is fallback demo)
```

If behind schedule → cut from bottom. P0 is all that matters for demo.

---

## Key Technical Notes

### Gemini 3 Gotchas (read docs/gemini-3.md)
- Keep temperature at default `1.0` — do NOT set below 1.0
- Use `thinking_level` not `thinking_budget` — don't use both
- Thought Signatures: use official SDK + chat feature → handled automatically
- `gemini-3.1-pro-preview-customtools` variant if model ignores custom tools

### Image Generation (read docs/nano-banana-image-generation.md)
- Use `response_modalities=['TEXT', 'IMAGE']` or `['IMAGE']` only
- Image size: use uppercase `"1K"`, `"2K"`, `"4K"` — lowercase rejected
- Webtoon panels: aspect ratio `9:16` (vertical scroll)
- Character consistency: pass selfie as reference image (up to 4 characters)
- Multi-turn editing relies on Thought Signatures — use chat feature

### ADK Patterns (read docs/adk-llms.txt)
- Tools = Python functions with docstrings — ADK auto-parses
- Session state persists across turns in `adk web`
- Sub-agents via `sub_agents=[]` on parent agent
- Parallel generation: use `ParallelAgent` or fire async calls

### Prompting (read docs/prompt-design.md)
- Describe scenes as narrative paragraphs, not keyword lists
- For webtoon panels: specify "Korean webtoon style, clean line art, speech bubble space"
- Character consistency prompt template used across ALL panel calls

---

## Hackathon Constraints

- **Submission deadline**: 5:00 PM
- **Demo**: must show features built during hackathon (DQ otherwise)
- **No**: Streamlit apps, basic RAG, chatbots (see docs/hackathon-info.md for full banned list)
- **Judging**: 50% Demo, 25% Impact, 15% Creativity, 10% Pitch

---

## Reference Docs

| Doc | What's in it |
|-----|-------------|
| `docs/hackathon-info.md` | Schedule, rules, judging criteria, prizes, WiFi |
| `docs/gemini-3.md` | Model IDs, thinking_level, media_resolution, Thought Signatures |
| `docs/nano-banana-image-generation.md` | Image gen API, reference images, aspect ratios, prompting |
| `docs/adk-llms.txt` | ADK Python SDK, agent definition, multi-agent, tools |
| `docs/prompt-design.md` | Gemini 3 prompting best practices, templates |
