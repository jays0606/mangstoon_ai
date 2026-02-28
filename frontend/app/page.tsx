"use client";

import { useState } from "react";
import ChatPanel from "./components/ChatPanel";
import WebtoonViewer from "./components/WebtoonViewer";

export type Panel = {
  panel_number: number;
  image_url: string;
  dialogue: string[];
  narration: string;
  image_prompt: string;
  // Rich storyboard fields — stored for edit context
  scene_description?: string;
  character_info?: string;
  character_state?: string;
  camera_angle?: string;
  mood?: string;
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
  { id: "k-webtoon", emoji: "🇰🇷", title: "K-Webtoon", desc: "Korean webtoon style" },
  { id: "manga", emoji: "🇯🇵", title: "Manga", desc: "Japanese manga style" },
  { id: "comic", emoji: "🇺🇸", title: "Comic", desc: "American comic style" },
  { id: "cinematic", emoji: "🎬", title: "Cinematic", desc: "Film-like direction" },
];

export default function Home() {
  const [phase, setPhase] = useState<Phase>(0);
  const [selectedStyle, setSelectedStyle] = useState<Style | null>(null);
  const [panels, setPanels] = useState<Panel[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [characterDescription, setCharacterDescription] = useState("");
  const [selectedPanel, setSelectedPanel] = useState<number | null>(null);
  const [genProgress, setGenProgress] = useState({ current: 0, total: 0 });
  const [storyTitle, setStoryTitle] = useState("");

  const handleSelectStyle = (style: Style) => {
    setSelectedStyle(style);
    setPhase(1);
  };

  const handleGenerate = async (story: string, selfieFile?: File, addMsg?: (text: string) => void) => {
    const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

    setPhase(2);
    setIsGenerating(true);
    setStoryTitle("Generating...");

    // Init 22 wait placeholders immediately
    setPanels(
      Array.from({ length: 22 }, (_, i) => ({
        panel_number: i + 1,
        image_url: "",
        dialogue: [],
        narration: "",
        image_prompt: "",
        status: "wait" as const,
      }))
    );
    setGenProgress({ current: 0, total: 22 });

    const formData = new FormData();
    formData.append("story", story);
    if (selfieFile) formData.append("selfie", selfieFile);

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
          if (event.type === "storyboard") {
            setStoryTitle(event.title ?? "");
            setCharacterDescription(event.character_description ?? "");
            setGenProgress({ current: 0, total: event.panel_count });
            addMsg?.(`✅ Storyboard: "${event.title}" · ${event.panel_count} panels queued`);
          } else if (event.type === "panel") {
            const p = event.panel as Panel;
            setPanels((prev) =>
              prev.map((x) =>
                x.panel_number === p.panel_number ? { ...p, status: "done" as const } : x
              )
            );
            setGenProgress((prev) => ({ ...prev, current: prev.current + 1 }));
            addMsg?.(`🖼 Panel #${p.panel_number} · ${p.narration || "done"}`);
          } else if (event.type === "done") {
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
      const panel = panels.find((p) => p.panel_number === panelNumber);
      const res = await fetch("/api/edit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          panel_number: panelNumber,
          instruction,
          scene_description: panel?.scene_description ?? "",
          character_info: panel?.character_info ?? characterDescription,
          character_state: panel?.character_state ?? "",
        }),
      });
      const data = await res.json();

      setPanels((prev) =>
        prev.map((p) =>
          p.panel_number === panelNumber
            ? { ...p, image_url: data.image_url, loading: false, status: "done" as const }
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
    setSelectedPanel(null);
    setGenProgress({ current: 0, total: 0 });
    setStoryTitle("");
  };

  const donePanels = panels.filter((p) => p.status === "done").length;

  return (
    <main style={{ height: "100vh", display: "flex", flexDirection: "column", background: "var(--bg)" }}>
      {/* Top Bar */}
      <div className="topbar">
        <div style={{ display: "flex", alignItems: "center" }}>
          <span className="topbar-logo">
            Mangstoon<span>AI</span>
          </span>
          <span className="topbar-model">Gemini 3.1 Pro + Flash · ADK</span>
        </div>
        <div className="topbar-right">
          {selectedStyle && (
            <span className="badge badge-style">{selectedStyle.title}</span>
          )}
          {panels.length > 0 && (
            <span className="badge badge-progress">
              {donePanels}/{panels.length}
            </span>
          )}
          <button className="btn-reset" onClick={handleReset}>RESET</button>
        </div>
      </div>

      {/* Split layout */}
      <div className="split-layout">
        <ChatPanel
          phase={phase}
          selectedStyle={selectedStyle}
          panels={panels}
          isGenerating={isGenerating}
          selectedPanel={selectedPanel}
          onSelectStyle={handleSelectStyle}
          onGenerate={handleGenerate}
          onEdit={handleEdit}
          onSelectPanel={setSelectedPanel}
        />

        <div className="preview-panel">
          {phase < 2 ? (
            <div className="empty-state">
              <span className="empty-state-icon">🌀</span>
              <span className="empty-state-text">
                {phase === 0 ? "스타일 선택 →" : "스토리 입력 후 생성 →"}
              </span>
            </div>
          ) : (
            <WebtoonViewer
              panels={panels}
              isGenerating={isGenerating}
              selectedPanel={selectedPanel}
              onSelectPanel={setSelectedPanel}
              genProgress={genProgress}
              styleName={selectedStyle?.title ?? ""}
              storyTitle={storyTitle}
            />
          )}
        </div>
      </div>
    </main>
  );
}
