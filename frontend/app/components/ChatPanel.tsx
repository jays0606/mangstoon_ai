"use client";

import { useState, useRef, useEffect, MutableRefObject } from "react";
import { Panel } from "../page";

type Props = {
  panels: Panel[];
  isGenerating: boolean;
  selectedPanels: number[];
  userStory: string;
  onEdit: (panelNumber: number, instruction: string) => void;
  onSelectPanels: (panels: number[]) => void;
  addMsgRef: MutableRefObject<((text: string, type?: "sys" | "progress" | "ai") => void) | null>;
};

type Message = {
  id: number;
  role: "user" | "ai" | "sys" | "progress";
  text: string;
  type?: "text" | "edit-examples";
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
  panels,
  isGenerating,
  selectedPanels,
  userStory,
  onEdit,
  onSelectPanels,
  addMsgRef,
}: Props) {
  const [messages, setMessages] = useState<Message[]>([
    { id: nid(), role: "ai", text: "Generating your webtoon...", type: "text" },
    { id: nid(), role: "sys", text: `[${ts()}] story submitted` },
  ]);
  const [input, setInput] = useState("");
  const [genDone, setGenDone] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);

  // Register addMsg callback with parent
  useEffect(() => {
    addMsgRef.current = (text: string, type?: "sys" | "progress" | "ai") => {
      setMessages((prev) => [
        ...prev,
        {
          id: nid(),
          role: (type === "ai" ? "ai" : type === "progress" ? "progress" : "sys") as Message["role"],
          text,
          type: type === "ai" ? "text" : undefined,
        },
      ]);
    };
    return () => { addMsgRef.current = null; };
  }, [addMsgRef]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Generation complete
  const prevGen = useRef(isGenerating);
  useEffect(() => {
    if (prevGen.current && !isGenerating && panels.length > 0 && !genDone) {
      setGenDone(true);
      setMessages((prev) => [
        ...prev,
        { id: nid(), role: "sys", text: `[${ts()}] complete \u00B7 ${panels.length} panels` },
        {
          id: nid(),
          role: "ai",
          text: `All ${panels.length} panels ready.\nClick panels to select, then type an edit.`,
          type: "text",
        },
        { id: nid(), role: "ai", text: "", type: "edit-examples" },
      ]);
    }
    prevGen.current = isGenerating;
  }, [isGenerating, panels.length, genDone]);

  const handleEditSend = () => {
    if (!input.trim()) return;
    const msg = input.trim();
    setInput("");

    setMessages((prev) => [...prev, { id: nid(), role: "user", text: msg }]);

    // Parse panel numbers from message
    const mentionedMatch = msg.match(/(\d+)\s*(?:\uBC88|\uD654)?\s*\uD328\uB110|panel\s*(\d+)|#(\d+)|(\d+)\s*\uBC88/gi);
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
          : `#${panelsToEdit.slice(0, 3).join(", #")}${panelsToEdit.length > 3 ? ` +${panelsToEdit.length - 3}` : ""}`;

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

      panelsToEdit.forEach((n) => onEdit(n, msg));
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
            {i < 2 && <span className="phase-arrow">{"\u203A"}</span>}
          </div>
        ))}
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="chat-messages">
        {/* Show user's story at top */}
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

          return (
            <div key={m.id} className="msg-ai-row fade-in">
              <div className="msg-avatar">{"\u2726"}</div>
              <div className="msg-bubble msg-bubble-ai">{m.text}</div>
            </div>
          );
        })}
      </div>

      {/* Chat Input */}
      <div className={`chat-input-bar ${isGenerating ? "disabled" : ""}`}>
        {selLabel && (
          <span className="selected-panel-badge">{selLabel}</span>
        )}
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
