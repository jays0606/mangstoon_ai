"use client";

import { useState, useRef, useEffect } from "react";
import { Panel, Phase, Style, STYLES } from "../page";

type Props = {
  phase: Phase;
  selectedStyle: Style | null;
  panels: Panel[];
  isGenerating: boolean;
  selectedPanel: number | null;
  onSelectStyle: (style: Style) => void;
  onGenerate: (story: string, selfieFile?: File, addMsg?: (text: string) => void) => void;
  onEdit: (panelNumber: number, instruction: string) => void;
  onSelectPanel: (n: number | null) => void;
};

type Message = {
  id: number;
  role: "user" | "ai" | "sys";
  text: string;
  type?: "text" | "style-cards" | "story-input" | "generate-cta" | "edit-examples";
};

let _id = 0;
const nid = () => ++_id;
const ts = () =>
  new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });

const EDIT_EXAMPLES = [
  "Change background to Han River night",
  "Make expression more dramatic",
  "Update the dialogue bubble",
  "Make character larger",
  "Brighten the mood",
];

export default function ChatPanel({
  phase,
  selectedStyle,
  panels,
  isGenerating,
  selectedPanel,
  onSelectStyle,
  onGenerate,
  onEdit,
  onSelectPanel,
}: Props) {
  const [messages, setMessages] = useState<Message[]>([
    { id: nid(), role: "sys", text: `[${ts()}] MangstoonAI v0.1 initialized` },
    { id: nid(), role: "ai", text: "Choose your webtoon style.", type: "text" },
    { id: nid(), role: "ai", text: "", type: "style-cards" },
  ]);
  const [input, setInput] = useState("");
  const [story, setStory] = useState("");
  const [selfieFile, setSelfieFile] = useState<File | null>(null);
  const [selfiePreview, setSelfiePreview] = useState<string | null>(null);
  const [storyConfirmed, setStoryConfirmed] = useState(false);
  const [genDone, setGenDone] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, phase, storyConfirmed]);

  // Phase transitions: add messages when style is selected
  const prevPhase = useRef(phase);
  useEffect(() => {
    if (prevPhase.current === 0 && phase === 1 && selectedStyle) {
      setMessages((prev) => [
        ...prev,
        { id: nid(), role: "sys", text: `[${ts()}] style: ${selectedStyle.id}` },
        { id: nid(), role: "ai", text: `${selectedStyle.title} style selected!\nUpload a selfie (optional) and enter your story.`, type: "text" },
        { id: nid(), role: "ai", text: "", type: "story-input" },
      ]);
    }
    prevPhase.current = phase;
  }, [phase, selectedStyle]);

  // When generation finishes
  const prevGen = useRef(isGenerating);
  useEffect(() => {
    if (prevGen.current && !isGenerating && panels.length > 0 && !genDone) {
      setGenDone(true);
      setMessages((prev) => [
        ...prev,
        { id: nid(), role: "sys", text: `[${ts()}] generation complete · ${panels.length} panels` },
        {
          id: nid(),
          role: "ai",
          text: `Done! ${panels.length} panels generated.\nClick any panel to edit it.`,
          type: "text",
        },
        { id: nid(), role: "ai", text: "", type: "edit-examples" },
      ]);
    }
    prevGen.current = isGenerating;
  }, [isGenerating, panels.length, genDone]);

  const handleSelfie = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelfieFile(file);
    setSelfiePreview(URL.createObjectURL(file));
  };

  const handleStoryAnalyze = () => {
    if (!story.trim()) return;
    setStoryConfirmed(true);
    setMessages((prev) => [
      ...prev,
      { id: nid(), role: "user", text: story.trim() },
      { id: nid(), role: "sys", text: `[${ts()}] story received · ${story.trim().split(" ").length} words` },
      { id: nid(), role: "ai", text: `Story locked in!\nClick Generate when ready.`, type: "text" },
      { id: nid(), role: "ai", text: "", type: "generate-cta" },
    ]);
  };

  const handleStartGenerate = () => {
    setMessages((prev) => [
      ...prev,
      { id: nid(), role: "sys", text: `[${ts()}] starting generation...` },
      { id: nid(), role: "ai", text: "Decomposing story with Gemini 3.1 Pro...", type: "text" },
    ]);

    const addMsg = (text: string) =>
      setMessages((prev) => [...prev, { id: nid(), role: "sys", text }]);

    onGenerate(story.trim(), selfieFile ?? undefined, addMsg);
  };

  const handleEditSend = () => {
    if (!input.trim()) return;
    const msg = input.trim();
    setInput("");

    setMessages((prev) => [...prev, { id: nid(), role: "user", text: msg }]);

    const match = msg.match(/(\d+)\s*(?:번|화)?\s*패널|panel\s*(\d+)|#(\d+)|(\d+)\s*번/i);
    let panelNum = match
      ? parseInt(match[1] ?? match[2] ?? match[3] ?? match[4])
      : selectedPanel;

    if (panelNum && panelNum >= 1 && panelNum <= panels.length) {
      onSelectPanel(panelNum);
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { id: nid(), role: "sys", text: `[${ts()}] editing panel #${panelNum}` },
          { id: nid(), role: "ai", text: `Regenerating panel #${panelNum}...`, type: "text" },
        ]);
      }, 150);
      onEdit(panelNum, msg);
    } else {
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            id: nid(),
            role: "ai",
            text: `Select a panel first or include a number.\nExample: "panel 3 change background to night"`,
            type: "text",
          },
        ]);
      }, 150);
    }
  };

  const handleEditChipClick = (example: string) => {
    if (selectedPanel) {
      setInput(`${selectedPanel}번 패널 ${example}`);
    } else {
      setInput(example);
    }
  };

  const phases = [
    { emoji: "🎨", label: "STYLE" },
    { emoji: "📝", label: "PLOT" },
    { emoji: "🌀", label: "GENERATE" },
  ];

  return (
    <div className="chat-panel">
      {/* Phase Progress Bar */}
      <div className="phase-bar">
        {phases.map((p, i) => (
          <div key={p.label} style={{ display: "flex", alignItems: "center" }}>
            <div
              className={`phase-step ${
                i < phase ? "done" : i === phase ? "active" : "future"
              }`}
            >
              <span>{p.emoji}</span>
              <span>{p.label}</span>
            </div>
            {i < 2 && <span className="phase-arrow">→</span>}
          </div>
        ))}
      </div>

      {/* Chat Messages */}
      <div ref={scrollRef} className="chat-messages">
        {messages.map((m) => {
          // System messages
          if (m.role === "sys") {
            return (
              <div key={m.id} className="msg msg-ai fade-in">
                <div className="msg-bubble msg-bubble-sys">{m.text}</div>
              </div>
            );
          }

          // Style cards inline
          if (m.type === "style-cards") {
            return (
              <div key={m.id} className="style-grid fade-in">
                {STYLES.map((s) => (
                  <div
                    key={s.id}
                    className={`style-card ${selectedStyle?.id === s.id ? "selected" : ""}`}
                    onClick={() => phase === 0 && onSelectStyle(s)}
                  >
                    <div className="style-card-emoji">{s.emoji}</div>
                    <div className="style-card-title">{s.title}</div>
                    <div className="style-card-desc">{s.desc}</div>
                  </div>
                ))}
              </div>
            );
          }

          // Story input inline
          if (m.type === "story-input" && !storyConfirmed) {
            return (
              <div key={m.id} className="fade-in" style={{ display: "flex", flexDirection: "column", gap: "10px", margin: "6px 0" }}>
                {/* Selfie */}
                <div className="selfie-upload">
                  <button
                    className={`selfie-btn ${selfiePreview ? "has-image" : ""}`}
                    onClick={() => fileRef.current?.click()}
                  >
                    {selfiePreview ? (
                      <img src={selfiePreview} alt="selfie" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                    ) : (
                      <span>📸</span>
                    )}
                  </button>
                  <input ref={fileRef} type="file" accept="image/*" style={{ display: "none" }} onChange={handleSelfie} />
                  <div>
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: selfieFile ? "var(--green)" : "var(--dim)", letterSpacing: "0.06em" }}>
                      {selfieFile ? "Character photo set ✓" : "Your photo (optional — makes it you)"}
                    </div>
                    {selfieFile && (
                      <button
                        onClick={() => { setSelfieFile(null); setSelfiePreview(null); }}
                        style={{ background: "none", border: "none", color: "var(--dim)", fontSize: "10px", cursor: "pointer", padding: 0, fontFamily: "var(--font-mono)" }}
                      >
                        ✕ Remove
                      </button>
                    )}
                  </div>
                </div>

                {/* Story textarea */}
                <textarea
                  className="story-textarea"
                  rows={3}
                  placeholder="Enter your fantasy story...&#10;e.g. I win the hackathon, fly business class to Google I/O, give a keynote"
                  value={story}
                  onChange={(e) => setStory(e.target.value)}
                />

                {/* Analyze button */}
                <button
                  className="btn-cta btn-cta-pink"
                  disabled={!story.trim()}
                  onClick={handleStoryAnalyze}
                >
                  📝 Analyze Story
                </button>
              </div>
            );
          }

          // Generate CTA
          if (m.type === "generate-cta") {
            return (
              <div key={m.id} className="fade-in" style={{ margin: "6px 0" }}>
                <button
                  className="btn-cta btn-cta-pink"
                  onClick={handleStartGenerate}
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                      <span style={{ display: "inline-block", width: "14px", height: "14px", border: "2px solid #fff", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
                      Generating...
                    </span>
                  ) : (
                    `🌀 Generate 22 Panels`
                  )}
                </button>
              </div>
            );
          }

          // Edit examples
          if (m.type === "edit-examples") {
            return (
              <div key={m.id} className="edit-examples fade-in">
                {EDIT_EXAMPLES.map((ex) => (
                  <button
                    key={ex}
                    className="edit-chip"
                    onClick={() => handleEditChipClick(ex)}
                  >
                    {ex}
                  </button>
                ))}
              </div>
            );
          }

          // Skip rendered story-input after confirmation
          if (m.type === "story-input" && storyConfirmed) {
            return null;
          }

          // Regular messages
          return (
            <div
              key={m.id}
              className={`msg ${m.role === "user" ? "msg-user" : "msg-ai"} fade-in`}
            >
              {m.role === "ai" && (
                <span className="msg-label msg-label-director">DIRECTOR</span>
              )}
              <div className={`msg-bubble ${m.role === "user" ? "msg-bubble-user" : "msg-bubble-ai"}`}>
                {m.text}
              </div>
            </div>
          );
        })}
      </div>

      {/* Chat Input */}
      <div className={`chat-input-bar ${phase < 2 || isGenerating ? "disabled" : ""}`}>
        {selectedPanel && (
          <span className="selected-panel-badge">#{selectedPanel}</span>
        )}
        <input
          className="chat-input"
          placeholder={selectedPanel ? `#${selectedPanel} · edit instruction...` : "Select a panel, then type an edit instruction"}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              handleEditSend();
            }
          }}
        />
        <button
          className={`btn-send ${input.trim() ? "btn-send-active" : "btn-send-disabled"}`}
          onClick={handleEditSend}
          disabled={!input.trim()}
        >
          SEND
        </button>
      </div>
    </div>
  );
}
