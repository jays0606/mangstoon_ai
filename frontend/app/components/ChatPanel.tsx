"use client";

import { useState, useRef, useEffect, MutableRefObject } from "react";
import { Panel } from "../page";

// ── Storyboard types ──────────────────────────────────────────────────────────
type StoryboardData = {
  title: string;
  characters: Array<{ name: string; role: string }>;
  panels_meta: Array<{
    panel_number: number;
    act: string;
    dialogue: string;
    character_names: string[];
  }>;
  panel_count: number;
};

type Props = {
  panels: Panel[];
  isGenerating: boolean;
  selectedPanels: number[];
  userStory: string;
  genProgress: { current: number; total: number };
  onEdit: (panelNumber: number, instruction: string) => void;
  onSelectPanels: (panels: number[]) => void;
  addMsgRef: MutableRefObject<
    | ((
        text: string,
        type?: "sys" | "progress" | "ai" | "storyboard",
        data?: StoryboardData
      ) => void)
    | null
  >;
};

type Message = {
  id: number;
  role: "user" | "ai" | "sys" | "progress";
  text: string;
  type?: "text" | "edit-examples" | "storyboard-card";
  data?: StoryboardData;
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

// ── Act color palette ─────────────────────────────────────────────────────────
const ACT_COLORS: Record<string, string> = {
  "Setup":          "rgba(99,102,241,0.85)",
  "Rising Action":  "#C8860A",
  "Climax":         "#D4002A",
  "Resolution":     "#1A8C42",
  "Epilogue":       "rgba(139,92,246,0.85)",
};

// ── Storyboard card ───────────────────────────────────────────────────────────
function StoryboardCard({
  data,
  onSelectPanels,
}: {
  data: StoryboardData;
  onSelectPanels: (p: number[]) => void;
}) {
  const [activeAct, setActiveAct] = useState<string | null>(null);

  // Group panels by act, preserving order
  const actGroups = new Map<string, number[]>();
  for (const p of data.panels_meta) {
    if (!actGroups.has(p.act)) actGroups.set(p.act, []);
    actGroups.get(p.act)!.push(p.panel_number);
  }
  const acts = Array.from(actGroups.entries());
  const total = data.panels_meta.length;

  const handleActClick = (act: string, panels: number[]) => {
    const next = activeAct === act ? null : act;
    setActiveAct(next);
    onSelectPanels(next ? panels : []);
  };

  return (
    <div
      style={{
        background: "var(--elevated)",
        border: "1px solid var(--border)",
        borderRadius: 12,
        padding: "16px 18px",
        marginLeft: 42,
        maxWidth: "90%",
        display: "flex",
        flexDirection: "column",
        gap: 13,
      }}
    >
      {/* Title */}
      <div
        style={{
          fontFamily: "var(--font-display)",
          fontSize: "17px",
          color: "var(--text)",
          lineHeight: 1.2,
        }}
      >
        {data.title}
      </div>

      {/* Characters */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
        {data.characters.map((c) => (
          <span
            key={c.name}
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              padding: "3px 10px",
              borderRadius: 20,
              background: "rgba(17,17,17,0.05)",
              border: "1px solid var(--border)",
              color: "var(--dim)",
              letterSpacing: "0.04em",
            }}
          >
            {c.name}
            <span style={{ opacity: 0.45, marginLeft: 4 }}>· {c.role}</span>
          </span>
        ))}
      </div>

      {/* Act arc bar */}
      <div>
        <div
          style={{
            display: "flex",
            borderRadius: 5,
            overflow: "hidden",
            height: 22,
            gap: 2,
          }}
        >
          {acts.map(([act, panels]) => {
            const w = (panels.length / total) * 100;
            const color = ACT_COLORS[act] ?? "rgba(100,100,100,0.6)";
            const isActive = activeAct === act;
            return (
              <div
                key={act}
                title={`${act} · panels ${panels[0]}–${panels[panels.length - 1]} (${panels.length}p)`}
                onClick={() => handleActClick(act, panels)}
                style={{
                  width: `${w}%`,
                  background: color,
                  cursor: "pointer",
                  opacity: activeAct && !isActive ? 0.35 : 1,
                  transition: "opacity 0.15s, transform 0.1s",
                  transform: isActive ? "scaleY(1.12)" : "scaleY(1)",
                  transformOrigin: "bottom",
                  borderRadius: 3,
                }}
              />
            );
          })}
        </div>

        {/* Act labels */}
        <div style={{ display: "flex", marginTop: 6, gap: 2 }}>
          {acts.map(([act, panels]) => {
            const w = (panels.length / total) * 100;
            const isActive = activeAct === act;
            const color = ACT_COLORS[act] ?? "rgba(100,100,100,0.6)";
            return (
              <div
                key={act}
                onClick={() => handleActClick(act, panels)}
                style={{
                  width: `${w}%`,
                  cursor: "pointer",
                  opacity: activeAct && !isActive ? 0.4 : 1,
                  transition: "opacity 0.15s",
                }}
              >
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "9px",
                    color: isActive ? color : "var(--dimmer)",
                    letterSpacing: "0.05em",
                    textTransform: "uppercase",
                    overflow: "hidden",
                    whiteSpace: "nowrap",
                    textOverflow: "ellipsis",
                    fontWeight: isActive ? 700 : 400,
                  }}
                >
                  {act}
                </div>
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "10px",
                    color: "var(--dimmer)",
                  }}
                >
                  {panels.length}p
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Expanded panel dialogue list for active act */}
      {activeAct && (
        <div
          style={{
            borderTop: "1px solid var(--border)",
            paddingTop: 10,
            display: "flex",
            flexDirection: "column",
            gap: 7,
            maxHeight: 180,
            overflowY: "auto",
          }}
        >
          {actGroups.get(activeAct)!.map((pnum) => {
            const p = data.panels_meta.find((x) => x.panel_number === pnum);
            if (!p) return null;
            return (
              <div key={pnum} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "10px",
                    color: "var(--dimmer)",
                    minWidth: 20,
                    paddingTop: 2,
                    flexShrink: 0,
                  }}
                >
                  {pnum}
                </span>
                <span
                  style={{
                    fontFamily: "var(--font-body)",
                    fontSize: "14px",
                    color: p.dialogue ? "var(--text)" : "var(--dimmer)",
                    fontStyle: p.dialogue ? "normal" : "italic",
                    lineHeight: 1.4,
                  }}
                >
                  {p.dialogue ? `"${p.dialogue}"` : "— no dialogue"}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function ChatPanel({
  panels,
  isGenerating,
  selectedPanels,
  userStory,
  genProgress,
  onEdit,
  onSelectPanels,
  addMsgRef,
}: Props) {
  const [messages, setMessages] = useState<Message[]>([
    { id: nid(), role: "sys", text: `[${ts()}] story submitted` },
  ]);
  const [input, setInput] = useState("");
  const [genDone, setGenDone] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);

  // Register addMsg callback with parent
  useEffect(() => {
    addMsgRef.current = (
      text: string,
      type?: "sys" | "progress" | "ai" | "storyboard",
      data?: StoryboardData
    ) => {
      setMessages((prev) => [
        ...prev,
        {
          id: nid(),
          role:
            type === "ai"
              ? "ai"
              : type === "progress"
              ? "progress"
              : type === "storyboard"
              ? "ai"
              : "sys",
          text,
          type:
            type === "storyboard"
              ? "storyboard-card"
              : type === "ai"
              ? "text"
              : undefined,
          data,
        } as Message,
      ]);
    };
    return () => {
      addMsgRef.current = null;
    };
  }, [addMsgRef]);

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isGenerating]);

  // Track panels being edited to detect completion
  const editingPanelsRef = useRef<Set<number>>(new Set());

  // Generation complete
  useEffect(() => {
    if (genDone) return;
    if (genProgress.total > 0 && genProgress.current >= genProgress.total) {
      setGenDone(true);
      setMessages((prev) => [
        ...prev,
        {
          id: nid(),
          role: "sys",
          text: `[${ts()}] complete · ${genProgress.current}/${genProgress.total} panels`,
        },
        {
          id: nid(),
          role: "ai",
          text: `Your webtoon is ready! ${genProgress.current} panels generated.\nClick any panel to select it, then describe your edit below.`,
          type: "text",
        },
        { id: nid(), role: "ai", text: "", type: "edit-examples" },
      ]);
    }
  }, [genProgress.current, genProgress.total, genDone]);

  // Detect edit completions
  const prevPanelStatuses = useRef<Map<number, string>>(new Map());
  useEffect(() => {
    const justFinished: number[] = [];
    for (const p of panels) {
      const prev = prevPanelStatuses.current.get(p.panel_number);
      if (
        prev === "gen" &&
        p.status === "done" &&
        genDone &&
        editingPanelsRef.current.has(p.panel_number)
      ) {
        justFinished.push(p.panel_number);
        editingPanelsRef.current.delete(p.panel_number);
      }
    }
    const newMap = new Map<number, string>();
    for (const p of panels) newMap.set(p.panel_number, p.status ?? "wait");
    prevPanelStatuses.current = newMap;

    if (justFinished.length > 0) {
      const label =
        justFinished.length === 1
          ? `Panel #${justFinished[0]} updated`
          : `${justFinished.length} panels updated (#${justFinished.join(", #")})`;
      setMessages((prev) => [
        ...prev,
        { id: nid(), role: "sys", text: `[${ts()}] ${label}` },
        {
          id: nid(),
          role: "ai",
          text:
            justFinished.length === 1
              ? `Done! Panel #${justFinished[0]} has been regenerated.`
              : `Done! ${justFinished.length} panels regenerated. Select more panels to continue editing.`,
          type: "text",
        },
      ]);
    }
  }, [panels, genDone]);

  const handleEditSend = () => {
    if (!input.trim()) return;
    const msg = input.trim();
    setInput("");

    setMessages((prev) => [...prev, { id: nid(), role: "user", text: msg }]);

    const mentionedMatch = msg.match(
      /(\d+)\s*(?:\uBC88|\uD654)?\s*\uD328\uB110|panel\s*(\d+)|#(\d+)|(\d+)\s*\uBC88/gi
    );
    let panelsToEdit: number[] = [];

    if (mentionedMatch && mentionedMatch.length > 0) {
      panelsToEdit = mentionedMatch
        .map((m) => {
          const numMatch = m.match(/\d+/);
          return numMatch ? parseInt(numMatch[0]) : null;
        })
        .filter((n): n is number => n !== null && n >= 1 && n <= panels.length);
    }

    if (panelsToEdit.length === 0) {
      panelsToEdit = selectedPanels.filter((n) => n >= 1 && n <= panels.length);
    }

    if (panelsToEdit.length > 0) {
      const label =
        panelsToEdit.length === 1
          ? `#${panelsToEdit[0]}`
          : `#${panelsToEdit.slice(0, 3).join(", #")}${
              panelsToEdit.length > 3 ? ` +${panelsToEdit.length - 3}` : ""
            }`;

      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            id: nid(),
            role: "ai",
            text:
              panelsToEdit.length === 1
                ? `Regenerating panel ${label}...`
                : `Regenerating ${panelsToEdit.length} panels (${label})...`,
            type: "text",
          },
        ]);
      }, 150);

      panelsToEdit.forEach((n) => {
        editingPanelsRef.current.add(n);
        onEdit(n, msg);
      });
      onSelectPanels(panelsToEdit);
    } else {
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            id: nid(),
            role: "ai",
            text: `Select panels first (click or Shift+click), then describe your edit.`,
            type: "text",
          },
        ]);
      }, 150);
    }
  };

  const selLabel =
    selectedPanels.length === 0
      ? null
      : selectedPanels.length === 1
      ? `#${selectedPanels[0]}`
      : `${selectedPanels.length} panels`;

  return (
    <div className="chat-panel">
      {/* Phase Bar */}
      <div className="phase-bar">
        {[
          { label: "STYLE", done: true },
          { label: "PLOT", done: true },
          { label: "GEN", done: !isGenerating && genDone },
        ].map((p, i) => (
          <div key={p.label} style={{ display: "flex", alignItems: "center" }}>
            <div
              className={`phase-step ${
                p.done && (i < 2 || genDone) ? "done" : i === 2 ? "active" : "done"
              }`}
            >
              <span>{p.label}</span>
            </div>
            {i < 2 && <span className="phase-arrow">{"›"}</span>}
          </div>
        ))}
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="chat-messages">
        {/* User story at top */}
        <div className="msg msg-user fade-in">
          <div className="msg-bubble msg-bubble-user">{userStory}</div>
        </div>

        {messages.map((m) => {
          if (m.role === "progress") {
            return (
              <div key={m.id} className="msg-progress fade-in">
                <div className="msg-progress-dot" />
                <span className="msg-progress-text">{m.text}</span>
              </div>
            );
          }

          if (m.role === "sys") {
            return (
              <div key={m.id} className="msg-sys-divider fade-in">
                <span className="msg-sys-text">{m.text}</span>
              </div>
            );
          }

          if (m.type === "storyboard-card" && m.data) {
            return (
              <div key={m.id} className="msg-ai-row fade-in">
                <div className="msg-avatar">{"✦"}</div>
                <StoryboardCard data={m.data} onSelectPanels={onSelectPanels} />
              </div>
            );
          }

          if (m.type === "edit-examples") {
            return (
              <div key={m.id} className="edit-examples fade-in">
                {EDIT_EXAMPLES.map((ex) => (
                  <button key={ex} className="edit-chip" onClick={() => setInput(ex)}>
                    {ex}
                  </button>
                ))}
              </div>
            );
          }

          if (m.role === "user") {
            return (
              <div key={m.id} className="msg msg-user fade-in">
                <div className="msg-bubble msg-bubble-user">{m.text}</div>
              </div>
            );
          }

          // ai text
          return (
            <div key={m.id} className="msg-ai-row fade-in">
              <div className="msg-avatar">{"✦"}</div>
              <div className="msg-bubble msg-bubble-ai">{m.text}</div>
            </div>
          );
        })}

        {/* Typing indicator — shown while generating */}
        {isGenerating && (
          <div className="msg-ai-row fade-in">
            <div className="msg-avatar">{"✦"}</div>
            <div className="msg-bubble msg-bubble-ai typing-indicator">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}
      </div>

      {/* Chat Input */}
      <div className={`chat-input-bar ${isGenerating ? "disabled" : ""}`}>
        {selLabel && <span className="selected-panel-badge">{selLabel}</span>}
        <input
          className="chat-input"
          placeholder={
            selectedPanels.length > 0
              ? `Edit ${selLabel}...`
              : "Select panels, then describe your edit"
          }
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
          Send
        </button>
      </div>
    </div>
  );
}
