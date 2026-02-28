# Nano Banana — Gemini Native Image Generation

**Nano Banana** is the name for Gemini's native image generation capabilities. Gemini can generate and process images conversationally with text, images, or a combination of both.

## Models

| Name | Model ID | Description |
|---|---|---|
| **Nano Banana 2** | `gemini-3.1-flash-image-preview` | High-efficiency, high-volume. Supports 512px–4K, Google Image Search grounding, up to 14 reference images. |
| **Nano Banana Pro** | `gemini-3-pro-image-preview` | Professional asset production. Advanced reasoning ("Thinking"), 4K resolution, up to 14 reference images. |
| **Nano Banana** | `gemini-2.5-flash-image` | Speed & efficiency optimized. 1024px resolution, high-volume/low-latency. |

All generated images include a [SynthID watermark](https://ai.google.dev/responsible/docs/safeguards/synthid).

---

## Image Generation (Text-to-Image)

```python
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client()

prompt = "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=[prompt],
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("generated_image.png")
```

```javascript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({});

const response = await ai.models.generateContent({
  model: "gemini-3.1-flash-image-preview",
  contents: "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme",
});

for (const part of response.candidates[0].content.parts) {
  if (part.text) {
    console.log(part.text);
  } else if (part.inlineData) {
    const buffer = Buffer.from(part.inlineData.data, "base64");
    fs.writeFileSync("gemini-native-image.png", buffer);
  }
}
```

---

## Image Editing (Text + Image → Image)

```python
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client()

prompt = "Create a picture of my cat eating a nano-banana in a fancy restaurant under the Gemini constellation"
image = Image.open("/path/to/cat_image.png")

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=[prompt, image],
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("generated_image.png")
```

---

## Multi-Turn Image Editing (Conversational)

```python
from google import genai
from google.genai import types

client = genai.Client()

chat = client.chats.create(
    model="gemini-3.1-flash-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        tools=[{"google_search": {}}]
    )
)

# Turn 1: Generate
response = chat.send_message("Create a vibrant infographic that explains photosynthesis as a recipe for a plant's favorite food.")

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("photosynthesis.png")

# Turn 2: Edit
response2 = chat.send_message(
    "Update this infographic to be in Spanish. Do not change any other elements.",
    config=types.GenerateContentConfig(
        image_config=types.ImageConfig(aspect_ratio="16:9", image_size="2K"),
    )
)
```

> **Note:** Multi-turn editing relies on **Thought Signatures** to preserve visual context. Use the official SDKs and chat feature — signatures are handled automatically.

---

## New with Gemini 3 Image Models

- **High-resolution output**: 512px, 1K, 2K, 4K
- **Advanced text rendering**: Legible stylized text for infographics, menus, diagrams
- **Grounding with Google Search**: Real-time data (weather, stock charts, recent events)
  - Nano Banana 2 adds **Google Image Search Grounding**
- **Thinking mode**: Generates interim "thought images" to refine composition
- **Up to 14 reference images**: Mix objects + characters
- **New aspect ratios** (Nano Banana 2): 1:4, 4:1, 1:8, 8:1

---

## Using Up to 14 Reference Images

| Model | Object fidelity | Character consistency |
|---|---|---|
| Nano Banana 2 (`gemini-3.1-flash-image-preview`) | Up to 10 images | Up to 4 characters |
| Nano Banana Pro (`gemini-3-pro-image-preview`) | Up to 6 images | Up to 5 characters |

```python
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=[
        "An office group photo of these people, they are making funny faces.",
        Image.open('person1.png'),
        Image.open('person2.png'),
        Image.open('person3.png'),
        Image.open('person4.png'),
        Image.open('person5.png'),
    ],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(aspect_ratio="5:4", image_size="2K"),
    )
)
```

---

## Grounding with Google Search

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents="Visualize the current weather forecast for the next 5 days in San Francisco as a clean, modern weather chart.",
    config=types.GenerateContentConfig(
        response_modalities=['Text', 'Image'],
        image_config=types.ImageConfig(aspect_ratio="16:9"),
        tools=[{"google_search": {}}]
    )
)
```

Response includes `groundingMetadata` with:
- `searchEntryPoint`: HTML/CSS to render required search suggestions
- `groundingChunks`: Top 3 web sources used

---

## Grounding with Google Image Search (Nano Banana 2 only)

```python
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents="A detailed painting of a Timareta butterfly resting on a flower",
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        tools=[
            types.Tool(google_search=types.GoogleSearch(
                search_types=types.SearchTypes(
                    web_search=types.WebSearch(),
                    image_search=types.ImageSearch()
                )
            ))
        ]
    )
)
```

**Display requirements for Image Search:**
- Must provide a link to the **webpage** containing the source image (not the image file directly)
- Single-click path from source image to its containing webpage required

---

## Resolution & Aspect Ratios

### Gemini 3.1 Flash Image Preview (Nano Banana 2)

| Aspect Ratio | 512px | 1K | 2K | 4K |
|---|---|---|---|---|
| 1:1 | 512×512 | 1024×1024 | 2048×2048 | 4096×4096 |
| 16:9 | 688×384 | 1376×768 | 2752×1536 | 5504×3072 |
| 9:16 | 384×688 | 768×1376 | 1536×2752 | 3072×5504 |
| 4:3 | 600×448 | 1200×896 | 2400×1792 | 4800×3584 |
| 3:4 | 448×600 | 896×1200 | 1792×2400 | 3584×4800 |
| 21:9 | 792×168 | 1584×672 | 3168×1344 | 6336×2688 |

*Also supports: 1:4, 4:1, 1:8, 8:1, 2:3, 3:2, 4:5, 5:4*

### Gemini 3 Pro Image Preview (Nano Banana Pro)

| Aspect Ratio | 1K | 2K | 4K |
|---|---|---|---|
| 1:1 | 1024×1024 | 2048×2048 | 4096×4096 |
| 16:9 | 1376×768 | 2752×1536 | 5504×3072 |
| 9:16 | 768×1376 | 1536×2752 | 3072×5504 |

*Supports: 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 21:9*

> **Note:** Use uppercase 'K' (e.g., `1K`, `2K`, `4K`). Lowercase will be rejected.

---

## Thinking Process & Thinking Levels

Gemini 3 image models use a thinking process by default (cannot be disabled).

For **Nano Banana 2** (`gemini-3.1-flash-image-preview`), you can control thinking:

```python
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents="A futuristic city built inside a giant glass bottle floating in space",
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        thinking_config=types.ThinkingConfig(
            thinking_level="High",  # "minimal" or "high"
            include_thoughts=True
        ),
    )
)

for part in response.parts:
    if part.thought:  # Skip thought images
        continue
    elif image := part.as_image():
        image.show()
```

> Thinking tokens are billed regardless of `include_thoughts` setting.

---

## Thought Signatures for Image Generation

All response `inline_data` image parts should have a `thought_signature`. The **first text part** (before any image) also gets a signature.

**Rule:** If you receive a thought signature, pass it back exactly as received in the next turn.

If using official SDKs with chat feature → handled automatically.

```json
{
  "text": "Here is a step-by-step guide...",
  "thought_signature": "<Signature_A>"  // First non-thought part
},
{
  "inlineData": { "data": "...", "mime_type": "image/png" },
  "thought_signature": "<Signature_B>"  // All image parts
}
```

---

## Optional Configuration

### Output Types

```python
# Images only (no text)
config=types.GenerateContentConfig(
    response_modalities=['Image']
)

# Default: text + image
config=types.GenerateContentConfig(
    response_modalities=['TEXT', 'IMAGE']
)
```

### Aspect Ratio & Image Size

```python
# Gemini 3 models
config=types.GenerateContentConfig(
    image_config=types.ImageConfig(
        aspect_ratio="16:9",
        image_size="2K",  # "512px", "1K", "2K", "4K"
    )
)

# Gemini 2.5 Flash Image (no image_size parameter)
config=types.GenerateContentConfig(
    image_config=types.ImageConfig(
        aspect_ratio="16:9",
    )
)
```

---

## Prompting Guide

### Core Principle
> **Describe the scene, don't just list keywords.** A narrative, descriptive paragraph will almost always produce a better result than a list of disconnected words.

### Generation Strategies

1. **Photorealistic scenes** — Use photography terms: camera angle, lens type, lighting, mood
   ```
   A photorealistic close-up portrait of an elderly Japanese ceramicist...
   Captured with an 85mm portrait lens, resulting in soft bokeh.
   ```

2. **Stylized illustrations & stickers** — Specify style + transparent background
   ```
   A kawaii-style sticker of a happy red panda... bold, clean outlines,
   simple cel-shading. The background must be white.
   ```

3. **Accurate text in images** — Be clear about text, font style, design
   ```
   Create a modern, minimalist logo for 'The Daily Grind'
   in a clean, bold, sans-serif font. Black and white. Circular.
   ```

4. **Product mockups** — Use photography/lighting terminology
   ```
   A high-resolution, studio-lit product photograph... three-point softbox
   setup... slightly elevated 45-degree shot...
   ```

5. **Minimalist & negative space** — For backgrounds where text will be overlaid
   ```
   A single delicate red maple leaf, bottom-right of frame.
   Vast empty off-white canvas. Significant negative space.
   ```

6. **Sequential art / Comics** — Specify style and panel count
   ```
   Make a 3 panel comic in a gritty, noir art style with
   high-contrast black and white inks.
   ```

7. **Grounding with Google Search** — Use for time-sensitive/real-world data
   ```
   Make a simple but stylish graphic of last night's Arsenal game
   in the Champion's League
   ```

### Editing Strategies

1. **Add/remove elements** — "Using the provided image, please add/remove..."
2. **Inpainting** — "Change only the [element] to [new]. Keep everything else exactly the same."
3. **Style transfer** — "Transform into the artistic style of Van Gogh's Starry Night..."
4. **Composition** — Combine multiple input images into a new scene
5. **High-fidelity detail preservation** — Describe features you want preserved in detail
6. **Bring sketches to life** — "Turn this rough sketch into a polished photo..."
7. **Character consistency (360 view)** — Include previously generated images in subsequent prompts

### Best Practices

- **Be hyper-specific:** "ornate elven plate armor, etched with silver leaf patterns, with pauldrons shaped like falcon wings" > "fantasy armor"
- **Provide context and intent:** Explain the *purpose* (brand target, use case)
- **Iterate conversationally:** "Keep everything the same, but change the expression to be more serious"
- **Step-by-step for complex scenes:** Break down into background → midground → foreground
- **Use semantic negative prompts:** "an empty, deserted street" > "no cars"
- **Control the camera:** `wide-angle shot`, `macro shot`, `low-angle perspective`

---

## Limitations

- Best languages: EN, ar-EG, de-DE, es-MX, fr-FR, hi-IN, id-ID, it-IT, ja-JP, ko-KR, pt-BR, ru-RU, ua-UA, vi-VN, zh-CN
- No audio or video inputs for image generation
- Model won't always follow exact number of output images requested
- `gemini-2.5-flash-image`: best with up to 3 input images
- `gemini-3-pro-image-preview`: 5 images high-fidelity, up to 14 total
- `gemini-3.1-flash-image-preview`: 4 character resemblance, 10 object fidelity
- For best text-in-image results: generate the text first, then request an image containing it

---

## Model Selection Guide

| Use Case | Recommended Model |
|---|---|
| General image generation | `gemini-3.1-flash-image-preview` (Nano Banana 2) |
| Professional asset production, complex instructions | `gemini-3-pro-image-preview` (Nano Banana Pro) |
| High-volume, low-latency, cost-sensitive | `gemini-2.5-flash-image` (Nano Banana) |
| Specialized image generation | Imagen 4 (via Gemini API) |

---

## Batch API

For high-volume image generation, use the [Batch API](https://ai.google.dev/gemini-api/docs/batch-api) — higher rate limits in exchange for up to 24-hour turnaround.
