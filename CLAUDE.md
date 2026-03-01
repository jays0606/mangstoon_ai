# MangstoonAI — CLAUDE.md

AI 망상툰 generator. **3rd Place — Gemini 3 Seoul Hackathon, Feb 28 2026 — $20,000 Credits**

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
├── cloudbuild.yaml                   # Cloud Build config (alternative to GitHub Actions)
├── .github/workflows/
│   └── deploy-backend.yml            # CI/CD: push to main → Cloud Run deploy
├── backend/                          # FastAPI + ADK agent (Python, uv)
│   ├── .env                          # GOOGLE_API_KEY — gitignored, never commit
│   ├── Dockerfile                    # Python 3.12-slim + pip install
│   ├── .dockerignore                 # Excludes .env, output/, __pycache__/
│   ├── main.py                       # FastAPI app (POST /generate, POST /edit, GET /health)
│   ├── pyproject.toml                # uv managed dependencies
│   ├── requirements.txt              # pip deps for Docker (mirrors pyproject.toml)
│   ├── run.sh                        # ./run.sh [--reload] — starts FastAPI on :8000
│   ├── output/panels/                # Generated PNG files — gitignored
│   └── mangstoon_ai/                 # ADK agent package
│       ├── __init__.py
│       ├── agent.py                  # root_agent — LlmAgent with 3 tools + system prompt
│       ├── gcs.py                    # upload_panel() → GCS public URL
│       ├── styles.py                 # 4 art style definitions (prompts, configs, names)
│       ├── tools/
│       │   ├── story_engine.py       # decompose_story() — Flash → 22-panel JSON storyboard
│       │   ├── image_gen.py          # generate_panel() — 2-step: Flash optimize → Flash Image + GCS
│       │   ├── panel_editor.py       # edit_panel() — 2-step: Flash edit prompt → Flash Image + GCS
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

### Production (Cloud Run)
`GOOGLE_API_KEY` is stored in **Secret Manager** and mounted as env var via `--set-secrets`.
GCS auth uses the Cloud Run service account (`mangstoon-deployer@...`) — no extra config needed.

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
  4. each panel uploaded to GCS → returns public URL + rich storyboard fields

POST /edit
  → edit_panel() [direct call, no agent overhead]
    (FE sends back scene_description + character_info + character_state)
  → edited panel uploaded to GCS → returns public URL
```

The key insight: agent runs for story decomposition (to get the system prompt's creative direction), then we break out of the event stream and do image gen in parallel ourselves.

---

## API Shapes

### POST /generate (multipart/form-data)
Input: `story: str`, `style?: str` (default `"k-webtoon"`), `selfie?: File`

Output:
```json
{
  "character_description": "...",
  "storyboard_title": "...",
  "panels": [{
    "panel_number": 1,
    "image_url": "https://storage.googleapis.com/mangstoon-panels/{session}/panel_01.png",
    "dialogue": ["..."],
    "narration": "setup",
    "image_prompt": "optimized prompt used",
    "scene_description": "...",
    "face_description": "...",
    "character_name": "...",
    "outfit": "...",
    "character_expression": "...",
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
  "character_state": "...",
  "style": "k-webtoon"
}
```
Output: `{ "panel_number": 3, "image_url": "https://storage.googleapis.com/mangstoon-panels/...", "status": "success" }`

---

## Tool Signatures

### decompose_story(user_story, num_panels=22, style="k-webtoon") → dict
Returns: `{"status", "storyboard": {"title", "characters": [{"name", "appearance", "role"}], "panels": [{"panel_number", "act", "scene_description", "character_state", "dialogue", "camera_angle", "mood"}]}, "panel_count"}`

### generate_panel(panel_number, scene_description, character_info, character_state, camera_angle, mood, dialogue, style="k-webtoon", session_id=None, tool_context=None) → dict
Returns: `{"status", "panel_number", "image_path", "image_url", "artifact", "optimized_prompt"}`
- `tool_context` optional: when present (adk web) saves ADK artifact; always saves to disk
- `style`: art style ID — one of `k-webtoon`, `anime`, `comic`, `cinematic`

### edit_panel(panel_number, edit_instruction, session_id, scene_description, face_description, outfit, style="k-webtoon", tool_context=None) → dict
Returns: `{"status", "panel_number", "image_path", "image_url", "artifact", "edit_applied"}`

### extract_character(selfie_description, style="k-webtoon") → dict
Returns: `{"face_description": "...", "face_ref_prompt": "..."}`

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

## Deployment

### Backend — Cloud Run (asia-northeast3 / Seoul)
```
URL: <your-cloud-run-url>
Region: asia-northeast3
SA: <your-service-account>@<your-project-id>.iam.gserviceaccount.com
Config: 2 CPU, 2Gi RAM, 300s timeout, max 3 instances
Secret: GOOGLE_API_KEY via Secret Manager
```

### CI/CD — GitHub Actions
Push to `main` (changes in `backend/`) triggers `.github/workflows/deploy-backend.yml`:
- Auth via Workload Identity Federation (no key files)
- `gcloud run deploy --source backend/`
- GitHub secrets: `WIF_PROVIDER`, `WIF_SERVICE_ACCOUNT`, `GCP_PROJECT_ID`, `CLOUD_RUN_SERVICE_ACCOUNT`

### Image Storage — GCS
```
Bucket: gs://mangstoon-panels (asia-northeast3, public read)
URL pattern: https://storage.googleapis.com/mangstoon-panels/{session_id}/panel_{NN}.png
Module: backend/mangstoon_ai/gcs.py → upload_panel(session_id, filename, bytes)
```
Both `generate_panel` and `edit_panel` upload to GCS after saving locally.
Falls back to base64 if GCS upload fails.

### Frontend — Vercel
Auto-deploys on push to `main` via Vercel Git integration.
Set `NEXT_PUBLIC_BACKEND_URL` env var in Vercel project settings to the Cloud Run URL.

---

## Key Technical Notes

### ToolContext dual-mode pattern
Both `generate_panel` and `edit_panel` have `tool_context=None`:
- adk web: ADK auto-injects real ToolContext → saves artifact to ADK store
- FastAPI: called directly without ToolContext → saves to disk + uploads to GCS

### Parallel image gen
`asyncio.gather(*[gen_one(p) for p in panels_meta])` — all 22 fire simultaneously.
Each panel wrapped in `asyncio.to_thread()` because the Gemini SDK is sync.

### Breaking the agent event stream early
`_run_agent_capture_tool()` captures the first `function_response` for a specific tool name, then breaks out. This lets us use the agent's creative decomposition without waiting for it to sequentially generate all 22 images.

### Image format
`response_modalities=["IMAGE"]`, `aspect_ratio="9:16"`.
Images saved to disk + uploaded to GCS. API returns public GCS URLs (falls back to base64).

---

## Hackathon Constraints

- **Submission deadline**: 5:00 PM Feb 28 2026
- **Demo**: must show features built during hackathon (DQ otherwise)
- **No**: Streamlit, basic RAG, simple chatbots
- **Judging**: 50% Demo, 25% Impact, 15% Creativity, 10% Pitch
- **ADK dev UI mandatory** for demo — run `adk web` from `backend/`

---

## Demo Prep & Pitch

### Judging
| Criteria | Weight | What judges look for |
|----------|--------|----------------------|
| **Demo** | 50% | Does it work? How well implemented? |
| **Impact** | 25% | Long-term potential, usefulness, fit to problem statement |
| **Creativity** | 15% | Innovative concept, unique demo |
| **Pitch** | 10% | How effectively presented |

Round 1: all teams, ~3 min pitch + 1-2 min Q&A → Top 6 advance
Round 2: on stage, ~3 min pitch + 2-3 min Q&A → Winners

### Submission (by 5:00 PM)
- Submit at https://cerebralvalley.ai/e/gemini-3-seoul-hackathon/hackathon/submit
- Must include **1-minute demo video** (YouTube unlisted or Loom)

### Demo Story
```
I'm a broke developer who wins the Gemini hackathon in Seoul.
Google flies me business class to Mountain View.
I give a keynote at Google I/O.
Backstage, I bump into Jisoo from BLACKPINK — she's super into AI.
We exchange numbers. We start dating.
My mom finally stops asking when I'll get a real job.
```
Pre-copy this. Paste during demo. Do NOT type live.

### 3-Minute Pitch Script

```
[0:00 - 0:20] HOOK — The 망상 moment

"Everyone has a 망상.
In Korean, 망상 means your wildest, most embarrassing fantasy —
the one you replay in your head but would never tell anyone.
What if you could turn that into a webtoon — starring yourself?"


[0:20 - 0:45] PROBLEM

"The webtoon market is worth 10 billion dollars.
Korea invented this format. But there are only 12,000
professional webtoon artists in the entire country.
A single pilot episode costs 60,000 dollars.
Weekly production burns artists out.
Millions of people have stories trapped in their heads
with no way to make them visual.
WEBTOON Canvas proved people want to create.
The only barrier left is: you have to know how to draw."


[0:45 - 0:50] TRANSITION

"MangstoonAI removes that barrier. Let me show you."
→ Switch to app (already open, style selector visible)


[0:50 - 0:55] STYLE SELECT

"First, I pick a style — Comic."
→ Click comic


[0:55 - 1:10] INPUT

"I type my 망상..."
→ Paste the pre-typed story
"...and upload a selfie. That's me — I'm the main character."
→ Upload selfie


[1:10 - 1:15] GENERATE

"Hit generate."
→ Click generate


[1:15 - 1:50] PANELS LOADING (talk while waiting ~20-30s)

"What's happening: Gemini Flash decomposes my story into a
20-panel storyboard — 5-act structure, camera angles, dialogue,
mood — all from a few sentences.
Then Gemini Flash Image generates all 20 panels in parallel.
Not one by one. All at once. Full ADK agent pipeline."
→ Panels start appearing. Scroll slowly.


[1:50 - 2:05] SHOW RESULTS

"Here's my webtoon. 20 panels. Speech bubbles. Consistent character.
This is my 망상 — visualized in under a minute."
→ Scroll through highlights. Pause on Jisoo panel / Google I/O panel.


[2:05 - 2:25] EDIT DEMO

"But what if I don't like some panels? I don't start over."
→ Shift-click to multi-select 3-5 panels
"I select the panels I want to change, and just chat with it:
'Make the final scenes more romantic.'"
→ Send edit. Show panels regenerating.
"It regenerates just those panels. Real-time creative control."


[2:25 - 2:45] TECH + IMPACT

"Under the hood: Gemini 3.1 Pro as creative director.
Flash for story decomposition. Flash Image for all panels in parallel.
Google ADK agent framework — not a wrapper, a real pipeline.
The webtoon market hits 60 billion by 2031.
We're not replacing artists.
We're creating a new category: personal webtoons."


[2:45 - 3:00] CLOSE

"Your 망상. Your face. Your story. Under a minute.
MangstoonAI turns every person into a webtoon creator.
Thank you."
```

### 1-Minute Demo Video (screen recording)

```
[0:00 - 0:03]  Title card: "MangstoonAI — Your 망상, Your Webtoon"
[0:03 - 0:07]  App opens. Click "Comic" style.
[0:07 - 0:15]  Paste story. Upload selfie. Hit generate.
[0:15 - 0:18]  Text overlay: "Gemini decomposes story → 20-panel storyboard"
[0:18 - 0:40]  Panels loading in. Scroll as they appear.
               Text overlay: "20 panels generated in parallel"
[0:40 - 0:50]  Scroll finished webtoon. Pause on 2-3 best panels.
[0:50 - 0:57]  Multi-select panels → send edit → show regenerated panels.
               Text overlay: "Edit any panel with natural language"
[0:57 - 1:00]  End card: "Built with Gemini 3.1 + Google ADK"
```

Record: QuickTime → File → New Screen Recording. Add text overlays in iMovie/Kapwing.

### Q&A Prep

| Likely question | Answer |
|-----------------|--------|
| Character consistency? | "Selfie → Gemini Pro extracts character description → injected into every panel prompt" |
| Why 20 panels? | "Standard webtoon episode. But it scales — 30, 40+ panels, all in parallel" |
| How long to generate? | "All panels fire in parallel — under a minute total" |
| What models? | "Gemini 3.1 Pro orchestration, Flash storyboarding, Flash Image generation. All via ADK" |
| How different from single image gen? | "Single image gen has no narrative. We decompose into acts, scenes, camera angles, mood — coherent 20-panel sequence" |
| Business model? | "Personal webtoons are the wedge. Next: creator tools for WEBTOON Canvas, branded content, IP licensing" |

### Impact Numbers (for pitch + Q&A)

- Webtoon market: **$10B+ (2025)**, projected **$60B by 2031** (33% CAGR)
- Only **12,000 professional webtoon artists** in South Korea
- Pilot episode cost: **$60K** mid-tier, **$200K** flagship
- WEBTOON Canvas (UGC) proves demand — millions want to create, drawing is the barrier
- We don't replace artists — we create **personal webtoons**, a new category
- "Every person becomes a webtoon creator"

### Timeline (Feb 28)

| When | What |
|------|------|
| Now → 3:30 PM | Full dry run. Fix any bugs. Time the generation. |
| 3:30 → 4:15 PM | Screen-record 1-min video. Add overlays. Upload YouTube (unlisted). |
| 4:15 → 4:45 PM | Rehearse 3-min pitch OUT LOUD × 3. Time it. |
| 4:45 → 5:00 PM | Submit at cerebralvalley.ai. |
| 5:00 → 5:15 PM | Final dry run. Servers up. Backup video ready. |
| 5:15 PM | Pitch. |
