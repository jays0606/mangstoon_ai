import asyncio
import base64
import json
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types
from pydantic import BaseModel

# Load .env before importing agent (needs GOOGLE_API_KEY)
load_dotenv(Path(__file__).parent / ".env", override=False)
load_dotenv(override=False)

# Import agent AFTER env is loaded
from mangstoon_ai.agent import root_agent
from mangstoon_ai.tools.character import extract_character
from mangstoon_ai.tools.image_gen import generate_panel
from mangstoon_ai.tools.panel_editor import edit_panel

# ---------------------------------------------------------------------------
# ADK runner — single instance, shared across all requests
# ---------------------------------------------------------------------------
_runner: InMemoryRunner | None = None


def get_runner() -> InMemoryRunner:
    global _runner
    if _runner is None:
        _runner = InMemoryRunner(agent=root_agent, app_name="mangstoon_ai")
    return _runner


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="MangstoonAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = Path(__file__).parent / "output" / "panels"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/output",
    StaticFiles(directory=str(Path(__file__).parent / "output")),
    name="output",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _panel_to_base64(image_path: str) -> str:
    path = Path(image_path)
    if not path.exists():
        return ""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{data}"


def _make_user_message(text: str) -> genai_types.Content:
    return genai_types.Content(role="user", parts=[genai_types.Part(text=text)])


async def _run_agent_capture_tool(
    runner: InMemoryRunner,
    session_id: str,
    user_id: str,
    message: str,
    tool_name: str,
) -> dict:
    """
    Run the agent and capture the first FunctionResponse for `tool_name`.
    Breaks out of the event stream as soon as we have the result so the
    agent doesn't try to call downstream tools (we orchestrate those ourselves).
    """
    msg = _make_user_message(message)
    captured: dict = {}

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=msg,
    ):
        if not event.content or not event.content.parts:
            continue
        for part in event.content.parts:
            fr = getattr(part, "function_response", None)
            if fr and fr.name == tool_name:
                captured = dict(fr.response) if fr.response else {}
                break
        if captured:
            break  # stop consuming — we have what we need

    return captured


# ---------------------------------------------------------------------------
# POST /generate
# ---------------------------------------------------------------------------
@app.post("/generate")
async def generate(
    story: str = Form(...),
    selfie: UploadFile | None = File(default=None),
):
    runner = get_runner()
    character_description = ""

    # 1. Extract character from selfie (direct tool call — no agent needed here)
    if selfie and selfie.filename:
        suffix = Path(selfie.filename).suffix or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await selfie.read())
            tmp_path = tmp.name
        try:
            char_result = await asyncio.to_thread(extract_character, tmp_path)
            character_description = char_result.get("character_prompt", "")
        finally:
            os.unlink(tmp_path)

    # 2. Create a fresh session for this generation
    #    Store character_description in session state so the agent can access it
    session = await runner.session_service.create_session(
        app_name="mangstoon_ai",
        user_id="user",
        state={"character_description": character_description},
    )

    # 3. Ask the agent (with MANGSTOON_DIRECTOR_INSTRUCTION system prompt) to
    #    decompose the story — it calls decompose_story tool internally
    agent_prompt = f"이야기를 웹툰으로 만들어주세요.\n\n이야기: {story}"
    if character_description:
        agent_prompt += f"\n\n주인공 외모: {character_description}"

    story_result = await _run_agent_capture_tool(
        runner=runner,
        session_id=session.id,
        user_id="user",
        message=agent_prompt,
        tool_name="decompose_story",
    )

    # decompose_story returns {"status", "storyboard": {"title", "characters", "panels"}, "panel_count"}
    storyboard = story_result.get("storyboard", {})
    panels_meta = storyboard.get("panels", [])
    if not panels_meta:
        raise HTTPException(status_code=500, detail="Agent failed to decompose story")

    # character_info comes from storyboard characters — richer than the selfie description
    characters = storyboard.get("characters", [])
    character_info = characters[0].get("appearance", "") if characters else character_description

    # 4. Generate all panel images in parallel
    async def gen_one(panel_meta: dict):
        result = await asyncio.to_thread(
            generate_panel,
            panel_meta["panel_number"],
            panel_meta.get("scene_description", ""),
            character_info,
            panel_meta.get("character_state", ""),
            panel_meta.get("camera_angle", "wide shot"),
            panel_meta.get("mood", "warm"),
            panel_meta.get("dialogue", ""),
            # no tool_context — defaults to None, saves to disk instead of ADK artifact
        )
        return result, panel_meta

    results = await asyncio.gather(*[gen_one(p) for p in panels_meta])

    # 5. Assemble response — include rich storyboard fields so FE can send them back on edit
    response_panels = []
    for gen_result, meta in results:
        image_url = _panel_to_base64(gen_result.get("image_path", ""))
        dialogue = meta.get("dialogue", "")
        response_panels.append({
            "panel_number": meta["panel_number"],
            "image_url": image_url,
            "dialogue": [dialogue] if isinstance(dialogue, str) and dialogue else dialogue if isinstance(dialogue, list) else [],
            "narration": meta.get("act", ""),
            "image_prompt": gen_result.get("optimized_prompt", ""),
            # Rich fields sent back for edit context
            "scene_description": meta.get("scene_description", ""),
            "character_info": character_info,
            "character_state": meta.get("character_state", ""),
            "camera_angle": meta.get("camera_angle", ""),
            "mood": meta.get("mood", ""),
        })

    response_panels.sort(key=lambda p: p["panel_number"])

    return {
        "character_description": character_description,
        "storyboard_title": storyboard.get("title", ""),
        "panels": response_panels,
    }


# ---------------------------------------------------------------------------
# POST /generate/stream  (SSE)
# ---------------------------------------------------------------------------
@app.post("/generate/stream")
async def generate_stream(
    story: str = Form(...),
    selfie: UploadFile | None = File(default=None),
):
    async def event_gen():
        runner = get_runner()
        character_description = ""

        # 1. Extract character from selfie
        if selfie and selfie.filename:
            suffix = Path(selfie.filename).suffix or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await selfie.read())
                tmp_path = tmp.name
            try:
                char_result = await asyncio.to_thread(extract_character, tmp_path)
                character_description = char_result.get("character_prompt", "")
            finally:
                os.unlink(tmp_path)

        # 2. Fresh session for this generation
        session = await runner.session_service.create_session(
            app_name="mangstoon_ai",
            user_id="user",
            state={"character_description": character_description},
        )

        # 3. Decompose story via agent
        agent_prompt = f"이야기를 웹툰으로 만들어주세요.\n\n이야기: {story}"
        if character_description:
            agent_prompt += f"\n\n주인공 외모: {character_description}"

        story_result = await _run_agent_capture_tool(
            runner=runner,
            session_id=session.id,
            user_id="user",
            message=agent_prompt,
            tool_name="decompose_story",
        )

        storyboard = story_result.get("storyboard", {})
        panels_meta = storyboard.get("panels", [])
        if not panels_meta:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to decompose story'})}\n\n"
            return

        characters = storyboard.get("characters", [])
        character_info = characters[0].get("appearance", "") if characters else character_description

        # 4. Send storyboard event first
        yield f"data: {json.dumps({'type': 'storyboard', 'title': storyboard.get('title', ''), 'character_description': character_description, 'panel_count': len(panels_meta)})}\n\n"

        # 5. Fire all panels in parallel, stream each as it completes
        queue: asyncio.Queue = asyncio.Queue()

        async def gen_one_queued(panel_meta: dict):
            result = await asyncio.to_thread(
                generate_panel,
                panel_meta["panel_number"],
                panel_meta.get("scene_description", ""),
                character_info,
                panel_meta.get("character_state", ""),
                panel_meta.get("camera_angle", "wide shot"),
                panel_meta.get("mood", "warm"),
                panel_meta.get("dialogue", ""),
            )
            await queue.put((result, panel_meta))

        tasks = [asyncio.create_task(gen_one_queued(p)) for p in panels_meta]

        for _ in range(len(panels_meta)):
            gen_result, meta = await queue.get()
            image_url = _panel_to_base64(gen_result.get("image_path", ""))
            dialogue = meta.get("dialogue", "")
            panel_data = {
                "panel_number": meta["panel_number"],
                "image_url": image_url,
                "dialogue": [dialogue] if isinstance(dialogue, str) and dialogue else (dialogue if isinstance(dialogue, list) else []),
                "narration": meta.get("act", ""),
                "image_prompt": gen_result.get("optimized_prompt", ""),
                "scene_description": meta.get("scene_description", ""),
                "character_info": character_info,
                "character_state": meta.get("character_state", ""),
                "camera_angle": meta.get("camera_angle", ""),
                "mood": meta.get("mood", ""),
            }
            yield f"data: {json.dumps({'type': 'panel', 'panel': panel_data})}\n\n"

        await asyncio.gather(*tasks)
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# POST /edit
# ---------------------------------------------------------------------------
class EditRequest(BaseModel):
    panel_number: int
    instruction: str
    scene_description: str = ""
    character_info: str = ""
    character_state: str = ""


@app.post("/edit")
async def edit(req: EditRequest):
    # Call edit_panel directly — all structured context comes from the frontend.
    # No need to route through the agent for edit; it's a pure tool call.
    result = await asyncio.to_thread(
        edit_panel,
        req.panel_number,
        req.instruction,
        req.scene_description,
        req.character_info,
        req.character_state,
        # no tool_context — saves to disk
    )

    image_url = _panel_to_base64(result.get("image_path", ""))
    return {
        "panel_number": req.panel_number,
        "image_url": image_url,
        "status": result.get("status", "unknown"),
    }


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}
