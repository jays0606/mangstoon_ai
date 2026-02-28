# MangstoonAI — CLAUDE.md

AI 망상툰 generator. Gemini 3 Seoul Hackathon, Feb 28 2026.

---

## Project Structure

```
gemini-hackathon/
├── CLAUDE.md
├── README.md
├── .gitignore                        # .env, output/, node_modules/ all ignored
├── docs/
│   ├── hackathon-info.md             # Schedule, rules, judging, prizes
│   ├── gemini-3.md                   # Gemini 3.1 Pro/Flash API reference
│   ├── nano-banana-image-generation.md  # Image gen API + prompting
│   ├── adk-llms.txt                  # ADK Python SDK reference
│   └── prompt-design.md              # Gemini prompting best practices
├── backend/                          # FastAPI + ADK agent (Python, uv)
│   ├── .env                          # GOOGLE_API_KEY — gitignored, never commit
│   ├── main.py                       # FastAPI app (POST /generate, POST /edit, GET /health)
│   ├── pyproject.toml                # uv managed dependencies
│   ├── run.sh                        # ./run.sh [--reload] — starts FastAPI on :8000
│   ├── output/panels/                # Generated PNG files — gitignored
│   └── mangstoon_ai/                 # ADK agent package
│       ├── __init__.py
│       ├── agent.py                  # root_agent — LlmAgent with 3 tools + system prompt
│       ├── tools/
│       │   ├── story_engine.py       # decompose_story() — Flash → 22-panel JSON storyboard
│       │   ├── image_gen.py          # generate_panel() — 2-step: Flash optimize → Flash Image
│       │   ├── panel_editor.py       # edit_panel() — 2-step: Flash edit prompt → Flash Image
│       │   └── character.py          # extract_character() — selfie → character description
│       └── prompts/
│           └── system.py             # MANGSTOON_DIRECTOR_INSTRUCTION — 3-phase director
└── frontend/                         # Next.js 14 app (deploy to Vercel)
    ├── app/
    │   ├── layout.tsx                # Black Han Sans + Noto Sans KR, title metadata
    │   ├── globals.css               # CSS variables, animations, split layout classes
    │   ├── page.tsx                  # Root: Phase state machine (0=style, 1=input, 2=viewer)
    │   └── components/
    │       ├── ChatPanel.tsx         # Left panel: StoryInput + ChatEditor
    │       ├── StoryInput.tsx        # Story textarea + selfie upload
    │       ├── WebtoonViewer.tsx     # Right panel: 22 panels, speech bubbles, loading skeletons
    │       └── ChatEditor.tsx        # KakaoTalk-style edit chat
    └── app/api/
        ├── generate/route.ts         # Proxy → backend:8000/generate
        └── edit/route.ts             # Proxy → backend:8000/edit
```

---

## API Keys & Environment

```bash
# backend/.env  (gitignored — never commit)
GOOGLE_API_KEY=your_key_here
```

The server loads `backend/.env` on startup via `load_dotenv(Path(__file__).parent / ".env")`.
Frontend has no secrets — it proxies to the backend via Next.js API routes.

---

## Models

| Step | Model | Thinking | Purpose |
|------|-------|----------|---------|
| Orchestrator | `gemini-3.1-pro-preview` | low | Directs 3-phase flow, calls tools, chats |
| `decompose_story` | `gemini-3-flash-preview` | low | 22-panel JSON storyboard from user story |
| `generate_panel` step 1 | `gemini-3-flash-preview` | minimal | Optimizes image prompt from panel metadata |
| `generate_panel` step 2 | `gemini-3.1-flash-image-preview` | — | Generates 9:16 panel image |
| `edit_panel` step 1 | `gemini-3-flash-preview` | minimal | Creates updated prompt with edit applied |
| `edit_panel` step 2 | `gemini-3.1-flash-image-preview` | — | Regenerates edited panel |
| `extract_character` | `gemini-3.1-pro-preview` | low | Selfie → character description |

**Do NOT use** `gemini-3-pro-preview` — deprecated, shuts down March 9.

---

## Running Locally

```bash
# ADK dev UI — run from backend/ (mandatory hackathon demo)
cd backend
uv run --project .. adk web --port 8080
# → http://localhost:8080/dev-ui/  →  select mangstoon_ai

# FastAPI backend
cd backend
./run.sh              # port 8000
./run.sh --reload     # with hot reload

# Next.js frontend
cd frontend
npm run dev           # port 3000
```

---

## Agent Architecture (3-Phase Pipeline)

### ADK path (adk web — hackathon demo)
```
User message
  → root_agent (gemini-3.1-pro-preview + MANGSTOON_DIRECTOR_INSTRUCTION)
      Phase 1: calls decompose_story() → presents storyboard → asks for approval
      Phase 2: (after user confirms) calls generate_panel() per panel, one at a time
               each panel requires confirmation click in ADK dev UI
      Phase 3: calls edit_panel() on user edit request
```

### FastAPI path (FE → backend)
```
POST /generate
  1. selfie → extract_character() [direct call, no agent]
  2. InMemoryRunner(root_agent) decomposes story → captures decompose_story result
     (agent applies creative fiction policy, 5-act structure, 22 panels)
  3. asyncio.gather() → generate_panel() × 22 in parallel [all fire at once]
  4. returns all panels as base64 image_url + rich storyboard fields

POST /edit
  → edit_panel() [direct call, no agent overhead]
    (FE sends back scene_description + character_info + character_state)
```

The key insight: agent runs for story decomposition (to get the system prompt's creative direction), then we break out of the event stream and do image gen in parallel ourselves.

---

## API Shapes

### POST /generate (multipart/form-data)
Input: `story: str`, `selfie?: File`

Output:
```json
{
  "character_description": "...",
  "storyboard_title": "...",
  "panels": [{
    "panel_number": 1,
    "image_url": "data:image/png;base64,...",
    "dialogue": ["..."],
    "narration": "setup",
    "image_prompt": "optimized prompt used",
    "scene_description": "...",
    "character_info": "...",
    "character_state": "...",
    "camera_angle": "wide shot",
    "mood": "warm"
  }]
}
```

### POST /edit (application/json)
Input:
```json
{
  "panel_number": 3,
  "instruction": "배경을 한강 야경으로 바꿔줘",
  "scene_description": "...",
  "character_info": "...",
  "character_state": "..."
}
```
Output: `{ "panel_number": 3, "image_url": "data:image/png;base64,...", "status": "success" }`

---

## Tool Signatures

### decompose_story(user_story, num_panels=22) → dict
Returns: `{"status", "storyboard": {"title", "characters": [{"name", "appearance", "role"}], "panels": [{"panel_number", "act", "scene_description", "character_state", "dialogue", "camera_angle", "mood"}]}, "panel_count"}`

### generate_panel(panel_number, scene_description, character_info, character_state, camera_angle, mood, dialogue, tool_context=None) → dict
Returns: `{"status", "panel_number", "image_path", "artifact", "optimized_prompt"}`
- `tool_context` optional: when present (adk web) saves ADK artifact; always saves to disk

### edit_panel(panel_number, edit_instruction, scene_description, character_info, character_state, tool_context=None) → dict
Returns: `{"status", "panel_number", "image_path", "artifact", "edit_applied"}`

### extract_character(image_path) → dict
Returns: `{"character_prompt": "...", "description": "..."}`

---

## Frontend State Machine

```
phase=0  → StyleSelector (pick k-webtoon / manga / comic / cinematic)
phase=1  → StoryInput (textarea + selfie upload)
phase=2  → WebtoonViewer (22 panels) + ChatEditor (edit chat)
```

Panel status: `"wait"` → `"gen"` → `"done"` (drives skeleton/spinner/image display)

Panel type carries full storyboard context: `scene_description`, `character_info`, `character_state`, `camera_angle`, `mood` — used when sending edit requests.

---

## Key Technical Notes

### ToolContext dual-mode pattern
Both `generate_panel` and `edit_panel` have `tool_context=None`:
- adk web: ADK auto-injects real ToolContext → saves artifact to ADK store
- FastAPI: called directly without ToolContext → saves to disk only (`output/panels/`)

### Parallel image gen
`asyncio.gather(*[gen_one(p) for p in panels_meta])` — all 22 fire simultaneously.
Each panel wrapped in `asyncio.to_thread()` because the Gemini SDK is sync.

### Breaking the agent event stream early
`_run_agent_capture_tool()` captures the first `function_response` for a specific tool name, then breaks out. This lets us use the agent's creative decomposition without waiting for it to sequentially generate all 22 images.

### Image format
`response_modalities=["IMAGE"]`, `aspect_ratio="9:16"`, `image_size="1K"` (uppercase K required).
`part.as_image()` then `.save()` to disk. Base64-encoded in response.

---

## Hackathon Constraints

- **Submission deadline**: 5:00 PM Feb 28 2026
- **Demo**: must show features built during hackathon (DQ otherwise)
- **No**: Streamlit, basic RAG, simple chatbots
- **Judging**: 50% Demo, 25% Impact, 15% Creativity, 10% Pitch
- **ADK dev UI mandatory** for demo — run `adk web` from `backend/`
