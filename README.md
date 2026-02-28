# 🌀 MangstoonAI — AI 망상툰 Generator

> *"나는 딥마인드 해커톤 1등해서 비즈니스석 타고 미국 가서 블랙핑크 지수 만나서 연애함"*
> — Your delusion, now a webtoon.

**Gemini 3 Seoul Hackathon | February 28, 2026 | Entertainment Track**

---

## 💡 What is this?

MangstoonAI turns your wildest fantasies into scroll-style Korean webtoons — instantly.

Upload your selfie, type your delusion, and watch as AI generates a full webtoon where **you** are the main character living your dream scenario. Then chat with the AI to edit any panel in real-time.

---

## 🏗️ Tech Stack

| Component | Technology | Role |
|-----------|-----------|------|
| **Framework** | **Google ADK (Agent Development Kit)** | Agent orchestration, tool management, session state |
| **Orchestrator LLM** | **Gemini 3.1 Pro** | Story decomposition, panel prompt generation, chat-based edit reasoning |
| **Image Generation** | **Gemini 3.1 Flash (Image)** | Webtoon panel image generation (parallel) |
| **Dev & Debug** | **ADK Web UI** (`adk web`) | Built-in browser UI for testing, inspecting events & traces |
| **Language** | Python 3.12+ | ADK Python SDK |

### Why Google ADK?

- **Built for Gemini** — optimized integration with Gemini 3.1 Pro/Flash, no boilerplate
- **Multi-agent orchestration** — SequentialAgent, ParallelAgent built-in for our pipeline
- **`adk web` dev UI** — instant browser-based debug/test interface at `localhost:8000`. Inspect every function call, model response, and trace in real-time. **This IS our rapid prototyping UI during the hackathon**
- **Tool ecosystem** — define Python functions as tools, ADK handles invocation lifecycle
- **Session state** — maintains webtoon state (panels, edits, character info) across chat turns

---

## 🎯 Problem Statement

> *AI-Powered Games: Build never-before-possible interactive experiences using Gemini.*

Webtoons are Korea's biggest cultural export ($5B+ market). AI image generation exists, but nobody has built a **personalized, interactive webtoon experience** where users direct their own story and refine it through conversation.

MangstoonAI is a **delusion-to-webtoon engine** — interactive entertainment where everyone is the protagonist.

---

## 🎮 How It Works

```
┌─────────────────────────────────────────────────────┐
│  1. UPLOAD          Upload your selfie               │
│  2. DELUDE          Type your fantasy scenario        │
│  3. GENERATE        AI creates 6-8 panel webtoon     │
│  4. CHAT & EDIT     Refine any panel via conversation │
└─────────────────────────────────────────────────────┘
```

---

## 🤖 ADK Agent Architecture

```
mangstoon_ai/
├── __init__.py
├── agent.py              # root_agent definition
├── .env                  # GOOGLE_API_KEY
├── tools/
│   ├── story_engine.py   # decompose_story() tool
│   ├── image_gen.py      # generate_panel() tool
│   ├── panel_editor.py   # edit_panel() tool
│   └── character.py      # extract_character() tool
└── prompts/
    └── system.py         # agent instructions
```

### Agent Definition (Simplified)

```python
from google.adk.agents import Agent

# Tools as Python functions — ADK auto-parses docstrings
def decompose_story(user_story: str, character_description: str) -> dict:
    """Break a user's fantasy story into 6-8 webtoon panel descriptions.

    Args:
        user_story: The user's delusion/fantasy scenario in free text.
        character_description: Visual description of the main character.

    Returns:
        dict with 'panels' list, each containing scene, dialogue, and image_prompt.
    """
    ...

def generate_panel(image_prompt: str, panel_number: int) -> dict:
    """Generate a single webtoon panel image using Gemini 3.1 Flash Image.

    Args:
        image_prompt: Detailed prompt for the panel image in Korean webtoon style.
        panel_number: Panel position (1-8) in the webtoon sequence.

    Returns:
        dict with 'image_url' and 'panel_number'.
    """
    ...

def edit_panel(panel_number: int, edit_instruction: str) -> dict:
    """Edit a specific panel based on user's chat instruction.

    Args:
        panel_number: Which panel to edit (1-8).
        edit_instruction: What to change (e.g., "change background to Han River").

    Returns:
        dict with updated 'image_url' and 'panel_number'.
    """
    ...

def extract_character(selfie_description: str) -> dict:
    """Extract visual character traits from a selfie for consistent panel generation.

    Args:
        selfie_description: Description of the uploaded selfie image.

    Returns:
        dict with 'character_prompt' template for consistent character depiction.
    """
    ...

# Root agent — Gemini 3.1 Pro as orchestrator
root_agent = Agent(
    model="gemini-3.1-pro",
    name="mangstoon_director",
    description="AI Webtoon Director that turns user fantasies into Korean webtoons",
    instruction="""You are MangstoonAI, an AI webtoon director.

    When a user provides a story/fantasy:
    1. If they uploaded a selfie, use extract_character to build character template
    2. Use decompose_story to break it into 6-8 panels
    3. Use generate_panel for each panel (call multiple times)
    4. Present the complete webtoon to the user

    When a user wants to edit:
    - Parse which panel number and what change they want
    - Use edit_panel to regenerate only that panel
    - Keep other panels unchanged

    Always maintain character description across all panel generations.
    Respond in Korean. Use webtoon-style narration and dialogue.
    """,
    tools=[decompose_story, generate_panel, edit_panel, extract_character],
)
```

### Dev & Debug with `adk web`

```bash
# Install
pip install google-adk

# Set API key
echo "GOOGLE_API_KEY=your_key" > mangstoon_ai/.env

# Launch — instant debug UI at localhost:8000
adk web

# → Select "mangstoon_director" from dropdown
# → Chat: "나는 해커톤 1등하고 지수 만남"
# → Events tab: inspect each tool call & model response
# → Trace view: see full execution flow
```

**`adk web` = our dev environment + debug tool + demo interface.** No separate UI needed.

---

## 🔄 Pipeline Flow

```
[User Input: Selfie + Story]
        │
        ▼
[extract_character]  →  character_prompt (session state)
        │
        ▼
[decompose_story]  →  6-8 panel descriptions + image prompts
        │                 (Gemini 3.1 Pro reasoning)
        ▼
[generate_panel x 6-8]  →  parallel image generation
        │                     (Gemini 3.1 Flash Image)
        ▼
[Webtoon Output]  →  panels in scroll format
        │
        ▼
[User Chat: "3번 패널 배경을 한강으로"]
        │
        ▼
[edit_panel(3, "한강 배경")]  →  regenerate panel 3 only
        │
        ▼
[Updated Webtoon]
```

---

## 📊 Judging Criteria Strategy

| Criteria | Weight | Our Approach |
|----------|--------|-------------|
| **Demo** | 50% | `adk web` chat → type delusion → panels generate → edit via chat. Pre-gen backup ready. |
| **Impact** | 25% | $5B webtoon market + personalization. TAM = everyone with a phone and a fantasy. |
| **Creativity** | 15% | "망상툰" — culturally Korean, universally relatable. First-ever delusion-to-webtoon. |
| **Pitch** | 10% | Meta: *"If we win this hackathon, this webtoon becomes real."* |

---

## ⏰ 13-Hour Build Plan

| Time | Task | Deliverable |
|------|------|-------------|
| 9:00-9:30 | `pip install google-adk`, scaffold, API keys | `adk web` running with empty agent |
| 9:30-10:30 | `decompose_story` tool | Story → panel prompts working |
| 10:30-12:00 | `generate_panel` tool + Flash Image integration | Single panel gen working |
| 12:00-12:30 | Lunch 🍱 | |
| 12:30-14:00 | Parallel panel gen + session state | Full 6-8 panel webtoon |
| 14:00-15:30 | `edit_panel` tool + chat editing | "3번 패널 바꿔" working |
| 15:30-16:30 | `extract_character` + selfie | Character consistency |
| 16:30-17:30 | Demo polish, pre-generate backup | Stable demo |
| 17:30-18:00 | Optional: minimal scroll UI if needed | Prettier output |
| 18:00-19:00 | Pitch prep | Ready |

### Priority Stack (cut from bottom if behind)

```
P0 — MUST:  decompose_story + generate_panel (text → webtoon)
P1 — SHOULD: edit_panel (chat → panel edit)
P2 — NICE:  extract_character (selfie integration)
P3 — SKIP:  custom frontend (adk web is the demo)
```

---

## 🎤 Demo Script (3 min)

```
[0:00-0:30] "모든 사람에게는 망상이 있습니다.
             제 망상은 이 해커톤 1등 → 비즈니스석 → 지수 만남 → 연애.
             AI가 이 망상을 진지하게 받아들이면?"

[0:30-1:30]  Live in adk web: type story → panels generate
             → scroll through completed webtoon

[1:30-2:30]  Chat: "5번 패널을 한강 야경으로"
             → panel 5 regenerates live

[2:30-3:00]  "MangstoonAI. 당신의 망상, 당신의 웹툰.
             Gemini 3.1 Pro + Flash Image + Google ADK."
```

---

## 🔑 Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Character inconsistency across panels | Detailed character prompt template + webtoon style tolerance |
| Image gen latency | Parallel API calls + progressive loading + pre-gen backup |
| API rate limits | Test morning of. Reduce to 4-6 panels if needed. |
| Celebrity name in prompts | User-typed input, not hardcoded. Demo only. |

---

## 🚀 Why This Wins

1. **Seoul = Webtoon capital.** Judges get it instantly.
2. **망상 = universal.** Everyone has a fantasy → webtoon is magic.
3. **Demo-first.** Visual output that makes people laugh.
4. **Gemini-native.** Pro (reasoning) + Flash Image (generation) = impossible without Gemini.
5. **ADK showcase.** Multi-tool agent + session state = what Google wants developers building.
6. **Meta.** Presenting a webtoon about winning the hackathon, at the hackathon.

---

*Built with ☕ and delusions at Gemini 3 Seoul Hackathon, Feb 28 2026*
*Powered by Google ADK + Gemini 3.1 Pro + Gemini 3.1 Flash Image*
