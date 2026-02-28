"use client";

import { useState, useRef, useEffect } from "react";
import ChatPanel from "./components/ChatPanel";
import WebtoonViewer from "./components/WebtoonViewer";

export type Panel = {
  panel_number: number;
  image_url: string;
  dialogue: string[];
  narration: string;
  image_prompt: string;
  scene_description?: string;
  face_description?: string;
  character_name?: string;
  outfit?: string;
  character_expression?: string;
  camera_angle?: string;
  mood?: string;
  session_id?: string;
  loading?: boolean;
  status?: "done" | "gen" | "wait";
};

export type Phase = 0 | 1 | 2;

export type Style = {
  id: string;
  emoji: string;
  title: string;
  desc: string;
};

export const STYLES: Style[] = [
  { id: "k-webtoon", emoji: "\uD83C\uDDF0\uD83C\uDDF7", title: "K-Webtoon", desc: "Korean webtoon style" },
  { id: "anime", emoji: "\uD83C\uDDEF\uD83C\uDDF5", title: "Anime", desc: "Japanese anime style" },
  { id: "comic", emoji: "\uD83C\uDDFA\uD83C\uDDF8", title: "Comic", desc: "American comic style" },
  { id: "cinematic", emoji: "\uD83C\uDFAC", title: "Cinematic", desc: "Cinematic manhwa style" },
];

const STORY_SUGGESTIONS = [
  "I'm a broke developer who wins the Gemini hackathon. Google flies me business class to Mountain View. I give a keynote at Google I/O.",
  "I become an idol trainee at HYBE. I debut in a K-pop group and perform at Coachella.",
  "I get isekai'd into a fantasy world where I'm the chosen hero with overpowered magic.",
  "I travel back to Joseon dynasty Korea and accidentally become a royal advisor to the king.",
];

export default function Home() {
  const [phase, setPhase] = useState<Phase>(0);
  const [selectedStyle, setSelectedStyle] = useState<Style | null>(null);
  const [panels, setPanels] = useState<Panel[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [characterDescription, setCharacterDescription] = useState("");
  const [characterImage, setCharacterImage] = useState("");
  const [selectedPanels, setSelectedPanels] = useState<number[]>([]);
  const [genProgress, setGenProgress] = useState({ current: 0, total: 0 });
  const [storyTitle, setStoryTitle] = useState("");
  const [sessionId, setSessionId] = useState("");

  // Story input state (lifted here so it persists across phases)
  const [story, setStory] = useState("");
  const [selfieFile, setSelfieFile] = useState<File | null>(null);
  const [selfiePreview, setSelfiePreview] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  // Refs to avoid stale closures in handleEdit
  const panelsRef = useRef<Panel[]>([]);
  const sessionIdRef = useRef("");
  useEffect(() => { panelsRef.current = panels; }, [panels]);
  useEffect(() => { sessionIdRef.current = sessionId; }, [sessionId]);

  const handleSelectStyle = (style: Style) => {
    setSelectedStyle(style);
    setPhase(1);
  };

  // addMsg callback ref — ChatPanel registers its addMsg function here
  const addMsgRef = useRef<((text: string, type?: "sys" | "progress" | "ai") => void) | null>(null);

  const handleGenerate = async () => {
    if (!story.trim()) return;
    const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

    setPhase(2);
    setIsGenerating(true);
    setStoryTitle("Generating...");
    setPanels([]);
    setGenProgress({ current: 0, total: 0 });

    const formData = new FormData();
    formData.append("story", story.trim());
    if (selectedStyle) formData.append("style", selectedStyle.id);
    if (selfieFile) formData.append("selfie", selfieFile);

    const addMsg = addMsgRef.current;

    try {
      const res = await fetch(`${BACKEND}/generate/stream`, { method: "POST", body: formData });
      if (!res.body) throw new Error("No response body");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() ?? "";

        for (const chunk of chunks) {
          if (!chunk.startsWith("data: ")) continue;
          const event = JSON.parse(chunk.slice(6));
          if (event.type === "status") {
            addMsg?.(event.message, "sys");
          } else if (event.type === "thought") {
            addMsg?.(`💭 ${event.content}`, "progress");
          } else if (event.type === "text") {
            if (event.content?.trim()) addMsg?.(event.content.trim(), "ai");
          } else if (event.type === "tool_call") {
            addMsg?.(`⚙ ${event.name}()`, "progress");
          } else if (event.type === "tool_result") {
            addMsg?.(`✓ ${event.name} → ${event.status}`, "progress");
          } else if (event.type === "character") {
            setCharacterDescription(event.face_description ?? "");
            setCharacterImage(event.face_ref_image ?? "");
            addMsg?.("Character extracted from selfie", "progress");
          } else if (event.type === "storyboard") {
            setStoryTitle(event.title ?? "");
            setSessionId(event.session_id ?? "");
            if (!characterDescription && event.character_description) {
              setCharacterDescription(event.character_description);
            }
            const count = event.panel_count as number;
            setPanels(Array.from({ length: count }, (_, i) => ({
              panel_number: i + 1,
              image_url: "",
              dialogue: [],
              narration: "",
              image_prompt: "",
              status: "wait" as const,
            })));
            setGenProgress({ current: 0, total: count });
            addMsg?.(`\u2726 "${event.title}" \u00B7 ${count} panels`, "progress");
          } else if (event.type === "panel") {
            const p = event.panel as Panel;
            setPanels((prev) =>
              prev.map((x) =>
                x.panel_number === p.panel_number ? { ...p, status: "done" as const } : x
              )
            );
            setGenProgress((prev) => ({ ...prev, current: prev.current + 1 }));
            addMsg?.(`Panel ${p.panel_number} \u00B7 ${p.narration || "done"}`, "progress");
          } else if (event.type === "error") {
            addMsg?.(event.message ?? "Generation failed", "sys");
            setIsGenerating(false);
          } else if (event.type === "done") {
            setSessionId(event.session_id ?? sessionId);
            setIsGenerating(false);
          }
        }
      }
    } catch {
      // Keep whatever panels we have
    }

    setIsGenerating(false);
  };

  const handleEdit = async (panelNumber: number, instruction: string) => {
    setPanels((prev) =>
      prev.map((p) =>
        p.panel_number === panelNumber ? { ...p, status: "gen" as const, loading: true } : p
      )
    );

    try {
      const panel = panelsRef.current.find((p) => p.panel_number === panelNumber);
      const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
      const res = await fetch(`${BACKEND}/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          panel_number: panelNumber,
          instruction,
          session_id: panel?.session_id ?? sessionIdRef.current,
          scene_description: panel?.scene_description ?? "",
          face_description: panel?.face_description ?? characterDescription,
          outfit: panel?.outfit ?? "",
          character_expression: panel?.character_expression ?? "",
          camera_angle: panel?.camera_angle ?? "",
          mood: panel?.mood ?? "",
          dialogue: panel?.dialogue?.[0] ?? "",
          style: selectedStyle?.id ?? "k-webtoon",
        }),
      });
      const data = await res.json();

      let newUrl = data.image_url || "";
      if (newUrl && !newUrl.startsWith("data:")) {
        newUrl += (newUrl.includes("?") ? "&" : "?") + `t=${Date.now()}`;
      }

      setPanels((prev) =>
        prev.map((p) =>
          p.panel_number === panelNumber
            ? { ...p, image_url: newUrl, loading: false, status: "done" as const }
            : p
        )
      );
    } catch {
      setPanels((prev) =>
        prev.map((p) =>
          p.panel_number === panelNumber ? { ...p, loading: false, status: "done" as const } : p
        )
      );
    }
  };

  const handleReset = () => {
    setPhase(0);
    setSelectedStyle(null);
    setPanels([]);
    setIsGenerating(false);
    setCharacterDescription("");
    setCharacterImage("");
    setSelectedPanels([]);
    setGenProgress({ current: 0, total: 0 });
    setStoryTitle("");
    setSessionId("");
    setStory("");
    setSelfieFile(null);
    setSelfiePreview(null);
  };

  const handleSelfie = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelfieFile(file);
    setSelfiePreview(URL.createObjectURL(file));
  };

  const donePanels = panels.filter((p) => p.status === "done").length;

  return (
    <main style={{ height: "100vh", display: "flex", flexDirection: "column", background: "var(--bg)" }}>
      {/* Top Bar */}
      <div className="topbar">
        <div style={{ display: "flex", alignItems: "baseline" }}>
          <span className="topbar-logo" style={{ cursor: "pointer" }} onClick={handleReset}>
            Mangstoon<span>AI</span>
          </span>
          {phase === 0 && (
            <span className="topbar-sub">AI Webtoon Generator</span>
          )}
        </div>
        <div className="topbar-right">
          {selectedStyle && (
            <span className="badge badge-style">{selectedStyle.title}</span>
          )}
          {panels.length > 0 && genProgress.total > 0 && (
            <span className="badge badge-progress">
              {donePanels}/{genProgress.total}
            </span>
          )}
          {phase > 0 && (
            <button className="btn-reset" onClick={handleReset}>Reset</button>
          )}
        </div>
      </div>

      {/* Phase 0: Hero Landing */}
      {phase === 0 && (
        <div className="hero-page fade-in">
          <div>
            <div className="hero-title">Mangstoon<span>AI</span></div>
            <div className="hero-subtitle">Your fantasy, illustrated.</div>
          </div>
          <div className="hero-styles">
            {STYLES.map((s) => (
              <div
                key={s.id}
                className="hero-style-card"
                onClick={() => handleSelectStyle(s)}
              >
                <span className="hero-style-flag">{s.emoji}</span>
                <span className="hero-style-title">{s.title}</span>
                <span className="hero-style-desc">{s.desc}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Phase 1: Story Input */}
      {phase === 1 && (
        <div className="story-page fade-in">
          <div className="story-container">
            <button className="story-back" onClick={() => { setPhase(0); setSelectedStyle(null); }}>
              &larr; Back to styles
            </button>

            <div className="story-heading">
              What&apos;s your <span>fantasy</span>?
            </div>

            <textarea
              className="story-textarea"
              rows={4}
              placeholder={"Enter your fantasy story...\ne.g. I win the hackathon, fly business class to Google I/O, meet Sundar Pichai"}
              value={story}
              onChange={(e) => setStory(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                  e.preventDefault();
                  handleGenerate();
                }
              }}
              autoFocus
            />

            {/* Story suggestions */}
            <div className="story-suggestions">
              {STORY_SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  className="story-chip"
                  onClick={() => setStory(s)}
                >
                  {s}
                </button>
              ))}
            </div>

            {/* Selfie upload */}
            <div className="selfie-upload">
              <button
                className={`selfie-btn ${selfiePreview ? "has-image" : ""}`}
                onClick={() => fileRef.current?.click()}
              >
                {selfiePreview ? (
                  <img
                    src={selfiePreview}
                    alt="selfie"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                ) : (
                  <span>{"\uD83D\uDCF8"}</span>
                )}
              </button>
              <input
                ref={fileRef}
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={handleSelfie}
              />
              <div>
                <div
                  style={{
                    fontFamily: "var(--font-body)",
                    fontSize: "14px",
                    color: selfieFile ? "var(--green)" : "rgba(17, 17, 17, 0.5)",
                    letterSpacing: "0.01em",
                  }}
                >
                  {selfieFile ? "Character photo set \u2713" : "Upload your photo (optional \u2014 makes you the main character)"}
                </div>
                {selfieFile && (
                  <button
                    onClick={() => { setSelfieFile(null); setSelfiePreview(null); }}
                    style={{
                      background: "none",
                      border: "none",
                      color: "var(--dim)",
                      fontSize: "10px",
                      cursor: "pointer",
                      padding: 0,
                      fontFamily: "var(--font-mono)",
                    }}
                  >
                    {"\u2715"} Remove
                  </button>
                )}
              </div>
            </div>

            {/* Generate button */}
            <button
              className="btn-cta btn-cta-primary"
              disabled={!story.trim()}
              onClick={handleGenerate}
            >
              Generate Webtoon
            </button>
          </div>
        </div>
      )}

      {/* Phase 2+: Split Layout */}
      {phase === 2 && (
        <div className="split-layout fade-in">
          <ChatPanel
            panels={panels}
            isGenerating={isGenerating}
            selectedPanels={selectedPanels}
            userStory={story}
            onEdit={handleEdit}
            onSelectPanels={setSelectedPanels}
            addMsgRef={addMsgRef}
          />

          <div className="preview-panel">
            <WebtoonViewer
              panels={panels}
              isGenerating={isGenerating}
              selectedPanels={selectedPanels}
              onSelectPanels={setSelectedPanels}
              genProgress={genProgress}
              styleName={selectedStyle?.title ?? ""}
              storyTitle={storyTitle}
              characterImage={characterImage}
            />
          </div>
        </div>
      )}
    </main>
  );
}
