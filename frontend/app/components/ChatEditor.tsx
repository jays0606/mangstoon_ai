"use client";

import { useState, useRef, useEffect } from "react";
import { Panel } from "../page";

type Props = {
  panels: Panel[];
  onEdit: (panelNumber: number, instruction: string) => void;
};

type Message = {
  role: "user" | "ai";
  text: string;
  time: string;
};

function getTime() {
  return new Date().toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" });
}

export default function ChatEditor({ panels, onEdit }: Props) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "ai",
      text: '패널을 수정하고 싶으면 알려주세요!\n예: "3번 패널 배경을 한강 야경으로 바꿔줘"',
      time: getTime(),
    },
  ]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const msg = input.trim();
    const time = getTime();
    setMessages((prev) => [...prev, { role: "user", text: msg, time }]);
    setInput("");

    const match = msg.match(/(\d+)\s*(?:번|화)?\s*패널|panel\s*(\d+)|#(\d+)|(\d+)\s*번/i);
    const panelNumber = match
      ? parseInt(match[1] ?? match[2] ?? match[3] ?? match[4])
      : null;

    if (panelNumber && panelNumber >= 1 && panelNumber <= panels.length) {
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { role: "ai", text: `${panelNumber}번 패널 수정 중... 잠시 기다려주세요 🖌️`, time: getTime() },
        ]);
      }, 200);
      onEdit(panelNumber, msg);
    } else {
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            role: "ai",
            text: `몇 번 패널을 수정할까요?\n예: "${panels.length}번 패널 표정을 더 극적으로"`,
            time: getTime(),
          },
        ]);
      }, 200);
    }
  };

  return (
    <div
      style={{
        border: "3px solid var(--white)",
        boxShadow: "6px 6px 0px var(--accent)",
        overflow: "hidden",
        background: "var(--ink-light)",
      }}
    >
      {/* Header */}
      <div
        style={{
          background: "var(--ink-mid)",
          borderBottom: "2px solid rgba(255,255,255,0.1)",
          padding: "12px 16px",
          display: "flex",
          alignItems: "center",
          gap: "10px",
        }}
      >
        <div
          style={{
            width: "36px",
            height: "36px",
            background: "var(--accent)",
            border: "2px solid var(--white)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "18px",
            flexShrink: 0,
          }}
        >
          🎬
        </div>
        <div>
          <div
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "13px",
              color: "var(--white)",
              letterSpacing: "0.06em",
            }}
          >
            연출 디렉터
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#00ff88" }} />
            <span style={{ fontSize: "10px", color: "rgba(255,255,255,0.4)", fontFamily: "var(--font-body)" }}>
              온라인
            </span>
          </div>
        </div>
        <div
          style={{
            marginLeft: "auto",
            background: "rgba(255,229,0,0.1)",
            border: "1.5px solid var(--accent)",
            padding: "3px 10px",
          }}
        >
          <span
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "10px",
              color: "var(--accent)",
              letterSpacing: "0.1em",
            }}
          >
            DIRECTOR&apos;S CUT
          </span>
        </div>
      </div>

      {/* Messages */}
      <div
        ref={scrollRef}
        style={{
          padding: "16px",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          maxHeight: "240px",
          overflowY: "auto",
          background: "var(--ink-light)",
        }}
      >
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: m.role === "user" ? "flex-end" : "flex-start",
              gap: "2px",
            }}
          >
            {m.role === "ai" && (
              <span
                style={{
                  fontSize: "10px",
                  color: "var(--accent)",
                  fontFamily: "var(--font-display)",
                  letterSpacing: "0.08em",
                  marginLeft: "4px",
                }}
              >
                디렉터
              </span>
            )}
            <div
              style={{
                maxWidth: "82%",
                padding: "9px 13px",
                fontFamily: "var(--font-body)",
                fontSize: "13px",
                lineHeight: 1.55,
                whiteSpace: "pre-wrap",
                ...(m.role === "user"
                  ? {
                      background: "var(--accent)",
                      color: "var(--ink)",
                      border: "2px solid var(--ink)",
                      borderRadius: "14px 14px 4px 14px",
                      fontWeight: 700,
                      boxShadow: "2px 2px 0 rgba(0,0,0,0.4)",
                    }
                  : {
                      background: "var(--ink-mid)",
                      color: "var(--white)",
                      border: "2px solid rgba(255,255,255,0.15)",
                      borderRadius: "14px 14px 14px 4px",
                      borderLeft: "3px solid var(--accent)",
                    }),
              }}
            >
              {m.text}
            </div>
            <span
              style={{
                fontSize: "10px",
                color: "rgba(255,255,255,0.2)",
                fontFamily: "var(--font-body)",
                margin: m.role === "user" ? "0 2px 0 0" : "0 0 0 2px",
              }}
            >
              {m.time}
            </span>
          </div>
        ))}
      </div>

      {/* Input */}
      <div
        style={{
          borderTop: "2px solid rgba(255,255,255,0.1)",
          padding: "12px",
          display: "flex",
          gap: "8px",
          background: "var(--ink-mid)",
          alignItems: "center",
        }}
      >
        <input
          style={{
            flex: 1,
            background: "rgba(255,255,255,0.05)",
            border: "2px solid rgba(255,255,255,0.15)",
            borderLeft: "3px solid var(--accent)",
            color: "var(--white)",
            fontFamily: "var(--font-body)",
            fontSize: "13px",
            padding: "10px 12px",
          }}
          placeholder='예: "3번 패널 배경을 한강으로"'
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); handleSend(); } }}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim()}
          style={{
            background: input.trim() ? "var(--accent)" : "rgba(255,255,255,0.08)",
            border: "2.5px solid",
            borderColor: input.trim() ? "var(--accent)" : "rgba(255,255,255,0.15)",
            color: input.trim() ? "var(--ink)" : "rgba(255,255,255,0.2)",
            fontFamily: "var(--font-display)",
            fontSize: "13px",
            padding: "10px 16px",
            cursor: input.trim() ? "pointer" : "not-allowed",
            letterSpacing: "0.05em",
            whiteSpace: "nowrap",
          }}
        >
          수정
        </button>
      </div>

      {/* Panel chips */}
      {panels.length > 0 && (
        <div
          style={{
            borderTop: "1.5px solid rgba(255,255,255,0.06)",
            padding: "8px 12px",
            display: "flex",
            gap: "6px",
            background: "var(--ink)",
            flexWrap: "wrap",
          }}
        >
          <span style={{ fontSize: "10px", color: "rgba(255,255,255,0.3)", fontFamily: "var(--font-body)", alignSelf: "center" }}>
            패널:
          </span>
          {panels.map((p) => (
            <button
              key={p.panel_number}
              onClick={() => setInput(`${p.panel_number}번 패널 `)}
              style={{
                background: "rgba(255,229,0,0.08)",
                border: "1.5px solid rgba(255,229,0,0.3)",
                color: "var(--accent)",
                fontFamily: "var(--font-display)",
                fontSize: "11px",
                padding: "3px 8px",
                cursor: "pointer",
                letterSpacing: "0.05em",
              }}
            >
              {p.panel_number}화
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
