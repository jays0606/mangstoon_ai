# MangstoonAI — Demo Prep & Submission Guide

## Links

| What | URL |
|------|-----|
| **Live App** | *(removed for now)* |
| **Backend (Cloud Run)** | `<your-cloud-run-url>` |
| **GitHub Repo** | https://github.com/jays0606/mangstoon_ai |
| **Submit** | https://cerebralvalley.ai/e/gemini-3-seoul-hackathon/hackathon/submit |
| **Pitch Deck** | `pitch-deck/MangstoonAI-Pitch.pptx` |

---

## Submission Form (fill at 4:45 PM)

| Field | Value |
|-------|-------|
| Team Name | MangstoonAI |
| Team Members | Jaeho Shin (@jays0606) |
| Project Description | See below |
| Public GitHub Repository | https://github.com/jays0606/mangstoon_ai |
| Demo Video | [YouTube unlisted link — upload after recording] |

### Project Description (copy-paste):

```
MangstoonAI turns any story into a full webtoon in under 1 minute.

Users type a short fantasy (망상), upload a selfie, and pick an art style. Gemini 3.1 Pro acts as a creative director — extracting the character from the selfie and decomposing the story into a 5-act, 20-panel storyboard with scene descriptions, camera angles, mood, and dialogue. Gemini Flash Image then generates all 20 panels in parallel. Users can multi-select panels and edit them with natural language ("make the final scenes more romantic").

Built with Google ADK agent framework, Gemini 3.1 Pro, Gemini 3 Flash, and Gemini 3.1 Flash Image. Deployed on Cloud Run + Vercel.

Entertainment Track — democratizing webtoon creation for the $10B+ webtoon market.
```

### Before submitting:
- [ ] Make GitHub repo public: `gh repo edit jays0606/mangstoon_ai --visibility public`
- [ ] Confirm .env is gitignored (it is)
- [ ] Upload 1-min video to YouTube (unlisted)

---

## Timeline (Feb 28 — from 2:15 PM)

| Time | Task | Status |
|------|------|--------|
| 2:15 - 2:30 | Dry run — full flow in production (removed for now) | ⬜ |
| 2:30 - 2:45 | Screen record with QuickTime (record the dry run) | ⬜ |
| 2:45 - 3:15 | CapCut — trim to 1 min, add text overlays, export | ⬜ |
| 3:15 - 3:30 | Upload video to YouTube (unlisted) | ⬜ |
| 3:30 - 3:45 | Drop screenshots into pitch deck, save | ⬜ |
| 3:45 - 4:30 | Rehearse 3-min pitch out loud × 5, time it | ⬜ |
| 4:30 - 4:45 | Make repo public, final dry run | ⬜ |
| 4:45 - 5:00 | Submit at cerebralvalley.ai | ⬜ |
| 5:00 - 5:15 | Servers up, backup video on phone, deep breath | ⬜ |
| 5:15 PM | PITCH (Round 1 — all teams) | ⬜ |

---

## Demo Story (pre-copy, CMD+V during demo)

```
I'm a broke developer who wins the Gemini hackathon in Seoul. Google flies me business class to Mountain View. I give a keynote at Google I/O. Backstage, I bump into Jisoo from BLACKPINK — turns out she's super into AI. We exchange numbers. We start dating. My mom finally stops asking when I'll get a real job.
```

---

## 3-Min Pitch Flow

```
SLIDES 1-5                    [~50 sec]
  1. Title
  2. What is 망상?
  3. Entertainment Track + Market ($10B → $60B)
  4. The Problem (12K artists, $60K, 100+ hrs)
  5. The Solution (Before/After)

CMD+TAB → browser             [~80 sec]
  - Click Comic style
  - CMD+V paste story
  - Upload selfie
  - Hit generate
  - Talk about tech while panels load (~20-30s)
  - Scroll through finished webtoon
  - Multi-select → edit → show regenerated panels

CMD+TAB → slides 7-12         [~50 sec]
  7. Architecture (3-phase pipeline)
  8. What the AI Creates (5-act + metadata)
  9. Powered by Gemini (model stack)
  10. Why This Is Different
  11. Impact: Democratization
  12. Close — "PERSONAL WEBTOONS"
```

---

## 1-Min Video (screen recording)

```
[0:00 - 0:03]  Text overlay: "MangstoonAI — Your 망상, Your Webtoon"
[0:03 - 0:07]  Select Comic style
[0:07 - 0:15]  Paste story + upload selfie + hit generate
[0:15 - 0:18]  Text overlay: "20 panels generated in parallel with Gemini"
[0:18 - 0:40]  Panels loading in real time — scroll as they appear
[0:40 - 0:50]  Scroll through finished webtoon, pause on best panels
[0:50 - 0:57]  Multi-select panels → send edit → show regenerated panels
[0:57 - 1:00]  Text overlay: "Built with Gemini 3.1 + Google ADK"
```

Record: QuickTime → File → New Screen Recording
Edit: CapCut → trim, text overlays, export 1080p
Upload: YouTube → unlisted

---

## Q&A Cheat Sheet

| Question | Answer |
|----------|--------|
| Character consistency? | Selfie → Gemini Pro extracts character description → injected into every panel prompt |
| Why 20 panels? | Standard webtoon episode. Scales to 30+ — all in parallel |
| How long to generate? | All panels in parallel — under 1 minute |
| What models? | Gemini 3.1 Pro (orchestration), Flash (storyboard), Flash Image (generation). All via ADK |
| Different from single image gen? | Narrative AI — decomposes into acts, scenes, camera angles, mood. Coherent 20-panel story, not random images |
| Business model? | Personal webtoons are the wedge. Next: WEBTOON Canvas creator tools, branded content, IP licensing |
| How does editing work? | Multi-select panels, type natural language instruction, AI regenerates just those panels with context |

---

## Impact Numbers (for pitch + Q&A)

- Webtoon market: **$10B+ (2025)**, projected **$60B by 2031** (33% CAGR)
- Only **12,000 professional webtoon artists** in South Korea
- Pilot episode cost: **$60K** mid-tier, **$200K** flagship
- **100+ hours** per episode, creators earning **$11/hr**
- WEBTOON Canvas: **$27M+ paid** to creators since 2020
- **170M monthly active users** across 150 countries
- **40+ Netflix K-dramas** adapted from webtoons
- AI creative tools market: **$142B by 2034** (26.5% CAGR)
- Gartner: **90% of digital content AI-generated by 2026**

---

## Judging

| Criteria | Weight |
|----------|--------|
| Demo | 50% |
| Impact | 25% |
| Creativity | 15% |
| Pitch | 10% |

Round 1: ALL teams, 3 min + 1-2 min Q&A (5:15 - 6:45 PM)
Round 2: Top 6 on stage, 3 min + 2-3 min Q&A (7:00 - 8:00 PM)
Winners: 8:15 PM

---

## Prizes

| Place | Prize |
|-------|-------|
| 1st | $50,000 Gemini API Credits + 1-on-1 with Google AIFF Founders |
| 2nd | $30,000 Gemini API Credits |
| 3rd | $20,000 Gemini API Credits |
