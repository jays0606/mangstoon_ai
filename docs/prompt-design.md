# Prompt Design Guide — Gemini API

Prompt design is the process of creating natural language requests that elicit accurate, high quality responses from a language model.

> **Note:** Prompt engineering is iterative. These guidelines are starting points — experiment and refine based on your specific use cases.

---

## Clear and Specific Instructions

### Input Types

| Input type | Example prompt | Notes |
|---|---|---|
| **Question** | "What's a good name for a flower shop that specializes in dried flowers? Give 5 options." | Direct question |
| **Task** | "Give me a simple list of 5 items I must bring camping." | Action to perform |
| **Entity** | "Classify as [large, small]: Elephant, Mouse, Snail" | Operate on data |
| **Completion** | Provide partial input, let model complete | Auto-completion style |

### Partial Input Completion (Completion Strategy)

Give the model a pattern to continue:

```
Valid fields are cheeseburger, hamburger, fries, and drink.
Order: Give me a cheeseburger and fries
Output: ```{ "cheeseburger": 1, "fries": 1 }```

Order: I want two burgers, a drink, and fries.
Output:
```

The model continues the pattern rather than interpreting instructions loosely.

### Constraints

Explicitly tell the model what to do AND what not to do:

```
Summarize this text in one sentence:
Text: [long text...]
```

### Response Format

Specify the format you want:

```
# System instruction
All questions should be answered comprehensively with details,
unless the user requests a concise response specifically.
```

---

## Zero-Shot vs Few-Shot Prompts

**Few-shot prompts** include examples showing the model what correct output looks like.
**Zero-shot prompts** provide no examples.

> **Recommendation:** Always include few-shot examples. Prompts without examples are typically less effective. Clear examples can replace written instructions entirely.

### Few-Shot Example

```
Below are some examples:

Question: Why is the sky blue?
Explanation1: [long explanation]
Explanation2: Due to Rayleigh scattering effect.
Answer: Explanation2

Question: What is the cause of earthquakes?
Explanation1: Sudden release of energy in the Earth's crust.
Explanation2: [long explanation]
Answer: Explanation1

Now answer:
Question: How is snow formed?
Explanation1: Snow is formed when water vapor freezes into ice crystals...
Explanation2: Water vapor freezes into ice crystals forming snow.
Answer:
```

### Tips for Examples

- **Optimal count:** Experiment — too few lacks pattern, too many risks overfitting
- **Positive patterns over anti-patterns:**
  - ❌ "Don't end haikus with a question: [bad example]"
  - ✅ "Always end haikus with an assertion: [good example]"
- **Consistent formatting:** Same structure, XML tags, whitespace, newlines across all examples

---

## Adding Context

Include information the model needs rather than assuming it has it.

Without context:
```
What should I do to fix my disconnected wifi?
The light on my Google Wifi router is yellow and blinking slowly.
```
→ Generic troubleshooting advice

With context:
```
Answer the question using the text below. Respond with only the text provided.
Question: What should I do to fix my disconnected wifi? The light is yellow and blinking slowly.
Text: Color: Slowly pulsing yellow
What it means: There is a network error.
What to do: Check that the Ethernet cable is connected...
```
→ Specific, accurate answer

---

## Prefixes

Add prefixes to signal semantic meaning:

- **Input prefix:** `English:` / `French:` — demarcates different inputs
- **Output prefix:** `JSON:` — signals desired output format
- **Example prefix:** Labels in few-shot prompts

```
Classify as one of: large / small

Text: Rhino
The answer is: large

Text: Mouse
The answer is: small

Text: Elephant
The answer is:
```

---

## Breaking Down Complex Prompts

1. **One instruction per prompt** — Route to the right prompt based on user input
2. **Chain prompts** — Output of one prompt becomes input of the next
3. **Aggregate responses** — Run parallel tasks on different data portions, combine results

---

## Model Parameters

| Parameter | Description | Notes |
|---|---|---|
| **Max output tokens** | Max tokens in response | ~4 chars/token, ~60-80 words/100 tokens |
| **Temperature** | Randomness in token selection | 0 = deterministic, higher = more creative |
| **topK** | Token selection pool size | topK=1 = greedy decoding |
| **topP** | Probability mass for token selection | Default 0.95 |
| **stop_sequences** | Strings that stop generation | Avoid sequences that appear in normal output |

> **Gemini 3 Note:** Keep temperature at default `1.0`. Setting below 1.0 may cause looping or degraded performance on complex tasks.

---

## Prompt Iteration Strategies

1. **Rephrase:** Different wording yields different results
   ```
   Version 1: How do I bake a pie?
   Version 2: Suggest a recipe for a pie.
   Version 3: What's a good pie recipe?
   ```

2. **Switch to analogous task:** If instructions aren't followed, try a different framing
   - "Which category does this belong to: thriller, sci-fi, mythology, biography?"
   - → Better: "Multiple choice: Which option describes this book? A) thriller B) sci-fi C) mythology D) biography"

3. **Change content order:**
   ```
   Version 1: [examples] [context] [input]
   Version 2: [input] [examples] [context]
   Version 3: [examples] [input] [context]
   ```

---

## Fallback Responses

If the model returns "I'm not able to help with that..." try **increasing the temperature**.

---

## Things to Avoid

- Don't rely on models for factual information without grounding/search tools
- Use with care for math and logic problems

---

## Gemini 3 Prompting

Gemini 3 responds best to direct, well-structured, clearly constrained prompts.

### Core Principles

- **Be precise and direct:** Avoid unnecessary or persuasive language
- **Use consistent structure:** XML tags (`<context>`, `<task>`) or Markdown headings — pick one and stick with it
- **Define parameters:** Explicitly explain ambiguous terms
- **Control verbosity:** Default is direct/efficient. Add "Explain as a friendly, talkative assistant" if you need more
- **Prioritize critical instructions:** System instruction or beginning of user prompt
- **Structure for long contexts:** Data first, instructions/questions last
- **Anchor context:** After large data blocks, use "Based on the information above..."

### Gemini 3 Flash Specific Tips

**Current date accuracy:**
```
For time-sensitive user queries that require up-to-date information, you
MUST follow the provided current time (date and year) when formulating
search queries in tool calls. Remember it is 2025 this year.
```

**Knowledge cutoff accuracy:**
```
Your knowledge cutoff date is January 2025.
```

**Grounding performance:**
```
You are a strictly grounded assistant limited to the information provided in
the User Context. In your answers, rely **only** on the facts that are
directly mentioned in that context. You must **not** access or utilize your
own knowledge or common sense to answer...
If the exact answer is not explicitly written in the context, you must state
that the information is not available.
```

### Enhancing Reasoning and Planning

Prompt for explicit planning before response:

```
Before providing the final answer, please:
1. Parse the stated goal into distinct sub-tasks.
2. Check if the input information is complete.
3. Create a structured outline to achieve the goal.
```

Prompt for self-critique:

```
Before returning your final response, review your output against the original constraints:
1. Did I answer the user's *intent*, not just their literal words?
2. Is the tone authentic to the requested persona?
```

### Structured Prompting Templates

**XML style:**
```xml
<role>
You are a helpful assistant.
</role>

<constraints>
1. Be objective.
2. Cite sources.
</constraints>

<context>
[User data / documents here]
</context>

<task>
[Specific user request here]
</task>
```

**Markdown style:**
```markdown
# Identity
You are a senior solution architect.

# Constraints
- No external libraries allowed.
- Python 3.11+ syntax only.

# Output format
Return a single code block.
```

### Full Template (Gemini 3 Best Practices)

**System Instruction:**
```
<role>
You are Gemini 3, a specialized assistant for [Domain].
You are precise, analytical, and persistent.
</role>

<instructions>
1. **Plan**: Analyze the task and create a step-by-step plan.
2. **Execute**: Carry out the plan.
3. **Validate**: Review your output against the user's task.
4. **Format**: Present the final answer in the requested structure.
</instructions>

<constraints>
- Verbosity: [Low/Medium/High]
- Tone: [Formal/Casual/Technical]
</constraints>

<output_format>
1. **Executive Summary**: [Short overview]
2. **Detailed Response**: [Main content]
</output_format>
```

**User Prompt:**
```
<context>
[Documents, code snippets, background info]
</context>

<task>
[Specific user request]
</task>

<final_instruction>
Remember to think step-by-step before answering.
</final_instruction>
```

---

## Agentic Workflows

For complex agents, configure behavior across these dimensions:

### Reasoning & Strategy
- **Logical decomposition:** How thoroughly to analyze constraints and order of operations
- **Problem diagnosis:** Depth of root cause analysis; abductive reasoning
- **Information exhaustiveness:** Analyze all sources vs. prioritize speed

### Execution & Reliability
- **Adaptability:** Strictly follow initial plan vs. pivot when observations contradict assumptions
- **Persistence & Recovery:** How many self-correction attempts before stopping
- **Risk Assessment:** Read (low risk) vs. write/state-change (high risk) distinction

### Interaction & Output
- **Ambiguity handling:** When to assume vs. when to ask user for clarification
- **Verbosity:** Explain actions vs. silent execution
- **Precision:** Solve all edge cases vs. ballpark estimates acceptable

### Agentic System Instruction Template

```
You are a very strong reasoner and planner. Before taking any action, you must
proactively, methodically, and independently plan and reason about:

1) Logical dependencies and constraints: Analyze against:
   1.1) Policy-based rules, mandatory prerequisites, constraints
   1.2) Order of operations (user may give steps out of order)
   1.3) Other prerequisites (information and/or actions needed)
   1.4) Explicit user constraints or preferences

2) Risk assessment: Consequences of the action? Will new state cause future issues?
   2.1) For exploratory tasks (searches), missing optional params = LOW risk.
        Prefer calling tool with available info over asking user.

3) Abductive reasoning: Identify most logical reason for any problem.
   3.1) Look beyond obvious causes — may require deeper inference
   3.2) May require multiple steps to test a hypothesis
   3.3) Prioritize hypotheses by likelihood but don't discard low-probability ones

4) Outcome evaluation: Does previous observation require plan changes?
   4.1) If initial hypotheses disproven, generate new ones from gathered info

5) Information availability: Use all sources:
   5.1) Available tools and their capabilities
   5.2) All policies, rules, checklists, constraints
   5.3) Previous observations and conversation history
   5.4) Information only available by asking the user

6) Precision: Verify claims by quoting exact applicable information.

7) Completeness: Exhaustively incorporate all requirements.
   7.1) Resolve conflicts using priority order from #1
   7.2) Avoid premature conclusions — check multiple options

8) Persistence: Do not give up unless all reasoning exhausted.
   8.1) On transient errors (e.g., "please try again"): retry UNLESS retry limit hit
   8.2) On other errors: change strategy/arguments, do NOT repeat failed call

9) Inhibit response: Only act after all above reasoning is completed.
```

---

## How Generative Models Work (Under the Hood)

Gemini generates text in two stages:

1. **Stage 1 (Deterministic):** Process input → generate probability distribution over next tokens
   ```
   "The dog jumped over the ..." →
   [("fence", 0.77), ("ledge", 0.12), ("blanket", 0.03), ...]
   ```

2. **Stage 2 (Stochastic):** Decode distribution → actual text via sampling

**Temperature** controls randomness in stage 2:
- `temperature = 0` → Always pick highest probability token (deterministic)
- High temperature → More random, surprising, diverse outputs
- **Gemini 3 recommendation:** Use default `1.0` to avoid unexpected looping/degradation

---

## Related Guides

- [Prompting with media files](https://ai.google.dev/gemini-api/docs/files#prompt-guide)
- [Nano Banana image generation prompts](./nano-banana-image-generation.md)
- [Imagen prompt guide](https://ai.google.dev/gemini-api/docs/imagen#imagen-prompt-guide)
- [Video generation prompts](https://ai.google.dev/gemini-api/docs/video#prompt-guide)
- [Prompt gallery](https://ai.google.dev/gemini-api/prompts)
