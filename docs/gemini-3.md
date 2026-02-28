# Gemini 3 API Documentation

> **Warning:** Gemini 3 Pro Preview is deprecated and will be shut down March 9, 2026. Migrate to Gemini 3.1 Pro Preview to avoid service disruption.

Gemini 3 is Google's most intelligent model family to date, built on a foundation of state-of-the-art reasoning. Designed for agentic workflows, autonomous coding, and complex multimodal tasks.

## Model IDs & Pricing

| Model ID | Context Window (In / Out) | Knowledge Cutoff | Pricing (Input / Output) |
|---|---|---|---|
| **gemini-3.1-flash-image-preview** | 128k / 32k | Jan 2025 | $0.25 (Text Input) / $0.067 (Image Output) |
| **gemini-3.1-pro-preview** | 1M / 64k | Jan 2025 | $2 / $12 (<200k tokens), $4 / $18 (>200k tokens) |
| **gemini-3-flash-preview** | 1M / 64k | Jan 2025 | $0.50 / $3 |
| **gemini-3-pro-image-preview** | 65k / 32k | Jan 2025 | $2 (Text Input) / $0.134 (Image Output) |
| ~~gemini-3-pro-preview~~ | 1M / 64k | Jan 2025 | Deprecated |

## Quick Start

```python
from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents="Find the race condition in this multi-threaded C++ snippet: [code here]",
)

print(response.text)
```

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

const response = await ai.models.generateContent({
  model: "gemini-3.1-pro-preview",
  contents: "Find the race condition in this multi-threaded C++ snippet: [code here]",
});

console.log(response.text);
```

---

## New API Features in Gemini 3

### Thinking Level

Gemini 3 uses dynamic thinking by default. Control depth with `thinking_level` parameter.

> **Important:** Cannot use both `thinking_level` and legacy `thinking_budget` in the same request (returns 400 error).

| Thinking Level | Gemini 3.1 Pro | Gemini 3 Flash | Description |
|---|---|---|---|
| **`minimal`** | Not supported | Supported | Minimizes latency for chat/high throughput. Does NOT guarantee thinking is off. |
| **`low`** | Supported | Supported | Minimizes latency and cost. Best for simple tasks. |
| **`medium`** | Supported | Supported | Balanced thinking for most tasks. |
| **`high`** | Supported (Default) | Supported (Default) | Maximizes reasoning depth. |

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents="How does AI work?",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="low")
    ),
)

print(response.text)
```

```javascript
const response = await ai.models.generateContent({
    model: "gemini-3.1-pro-preview",
    contents: "How does AI work?",
    config: {
      thinkingConfig: {
        thinkingLevel: "low",
      }
    },
  });
```

---

### Media Resolution

Control multimodal vision processing via `media_resolution` parameter.

| Media Type | Recommended Setting | Max Tokens | Usage Guidance |
|---|---|---|---|
| **Images** | `media_resolution_high` | 1120 | Recommended for most image analysis |
| **PDFs** | `media_resolution_medium` | 560 | Optimal for document understanding |
| **Video** (General) | `media_resolution_low` | 70 (per frame) | Sufficient for most action recognition |
| **Video** (Text-heavy) | `media_resolution_high` | 280 (per frame) | Required for dense text/OCR in video |

> **Note:** `media_resolution` is currently only available in the `v1alpha` API version.

```python
from google import genai
from google.genai import types
import base64

client = genai.Client(http_options={'api_version': 'v1alpha'})

response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents=[
        types.Content(
            parts=[
                types.Part(text="What is in this image?"),
                types.Part(
                    inline_data=types.Blob(
                        mime_type="image/jpeg",
                        data=base64.b64decode("..."),
                    ),
                    media_resolution={"level": "media_resolution_high"}
                )
            ]
        )
    ]
)
```

---

### Temperature

**Strongly recommended:** Keep temperature at default `1.0` for all Gemini 3 models.

Setting temperature below 1.0 may cause looping or degraded performance, especially on complex reasoning tasks.

---

### Thought Signatures

Gemini 3 uses **Thought Signatures** — encrypted representations of internal reasoning — to maintain context across API calls.

**Rules:**
- **Function Calling (Strict):** Missing signatures → 400 error
- **Text/Chat:** Validation not enforced, but omitting degrades quality
- **Image generation/editing (Strict):** Missing signatures → 400 error

> **Tip:** If you use the official SDKs (Python, Node, Java) with standard chat history, Thought Signatures are handled **automatically**.

**Migrating from other models:** Use dummy string `"thoughtSignature": "context_engineering_is_the_way_to_go"` to bypass strict validation when injecting conversations from other models.

#### Sequential Function Calling Example

```java
// Step 1: Model returns signature <Sig_A>
{ "role": "model", "parts": [
    { "functionCall": { "name": "check_flight", "args": {...} }, "thoughtSignature": "<Sig_A>" }
]}

// Step 2: Must return <Sig_A> back
// Step 3: Model returns new <Sig_B>
// Step 4: Must return BOTH <Sig_A> AND <Sig_B>
```

#### Parallel Function Calling

Only the **first** `functionCall` part in parallel calls contains the signature.

---

### Structured Outputs with Tools

Gemini 3 supports combining Structured Outputs with built-in tools (Google Search, URL Context, Code Execution, Function Calling).

```python
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List

class MatchResult(BaseModel):
    winner: str = Field(description="The name of the winner.")
    final_match_score: str = Field(description="The final match score.")
    scorers: List[str] = Field(description="The name of the scorer.")

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents="Search for all details for the latest Euro.",
    config={
        "tools": [
            {"google_search": {}},
            {"url_context": {}}
        ],
        "response_mime_type": "application/json",
        "response_json_schema": MatchResult.model_json_schema(),
    },
)

result = MatchResult.model_validate_json(response.text)
print(result)
```

---

### Image Generation (Gemini 3 Image Models)

See `nano-banana-image-generation.md` for full image generation docs.

- **Nano Banana Pro** (`gemini-3-pro-image-preview`): Professional asset production, advanced reasoning, 4K resolution
- **Nano Banana 2** (`gemini-3.1-flash-image-preview`): High-efficiency, high-volume, up to 4K

---

### Code Execution with Images

Gemini 3 Flash can treat vision as active investigation — writes and executes Python code to zoom, crop, annotate, or manipulate images.

```python
from google import genai
from google.genai import types
import requests

image_path = "https://goo.gle/instrument-img"
image_bytes = requests.get(image_path).content
image = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[
        image,
        "Zoom into the expression pedals and tell me how many pedals are there?"
    ],
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution)]
    ),
)
```

---

## Tool Support

| Tool | Supported |
|---|---|
| Google Search | ✅ |
| File Search | ✅ |
| Code Execution | ✅ |
| URL Context | ✅ |
| Function Calling | ✅ |
| Grounding with Google Maps | ❌ Not yet supported |
| Built-in tools + Function Calling combined | ❌ Not yet supported |

---

## Migrating from Gemini 2.5

- **Thinking:** Replace chain-of-thought prompt engineering with `thinking_level: "high"` + simplified prompts
- **Temperature:** Remove explicit temperature settings, use default `1.0`
- **PDFs:** Test `media_resolution_high` for dense document parsing
- **Token consumption:** May increase for PDFs, decrease for video
- **Image segmentation:** NOT supported in Gemini 3 Pro/Flash — stay on Gemini 2.5 Flash (thinking off) for segmentation workloads
- **Computer Use:** Supported in Gemini 3 Pro/Flash (no separate model needed, unlike 2.5 series)

---

## OpenAI Compatibility

OpenAI's `reasoning_effort` parameter is automatically mapped to Gemini's `thinking_level` equivalents via the compatibility layer.

---

## Prompting Best Practices

- **Precise instructions:** Be concise and direct. Gemini 3 may over-analyze verbose prompt engineering from older models.
- **Output verbosity:** Defaults to less verbose/direct answers. Add "Explain this as a friendly, talkative assistant" if needed.
- **Context management:** Place specific instructions/questions **after** large data context. Start with "Based on the information above..."

---

## FAQ

1. **Knowledge cutoff?** January 2025. Use Search Grounding for recent info.
2. **Context window?** 1M token input, up to 64k output.
3. **Free tier?** `gemini-3-flash-preview` has free tier. No free API tier for `gemini-3.1-pro-preview`.
4. **`thinking_budget` still works?** Yes, but migrate to `thinking_level`. Don't use both.
5. **Batch API?** Yes, supported.
6. **Context Caching?** Yes, supported.
7. **`gemini-3.1-pro-preview-customtools`?** Use if model ignores custom tools in favor of bash commands.
