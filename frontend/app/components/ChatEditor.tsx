"use client";

import { useState } from "react";
import { Panel } from "../page";

type Props = {
  panels: Panel[];
  onEdit: (panelNumber: number, instruction: string) => void;
};

export default function ChatEditor({ panels, onEdit }: Props) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ role: "user" | "ai"; text: string }[]>([]);

  const handleSend = () => {
    if (!input.trim()) return;

    const msg = input.trim();
    setMessages((prev) => [...prev, { role: "user", text: msg }]);
    setInput("");

    // Parse panel number from message: "3번 패널", "panel 3", "#3", etc.
    const match = msg.match(/(\d+)\s*번?\s*패널|panel\s*(\d+)|#(\d+)/i);
    const panelNumber = match
      ? parseInt(match[1] ?? match[2] ?? match[3])
      : null;

    if (panelNumber && panelNumber >= 1 && panelNumber <= panels.length) {
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: `${panelNumber}번 패널 수정 중...` },
      ]);
      onEdit(panelNumber, msg);
    } else {
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text: `몇 번 패널을 수정할까요? 예: "3번 패널 배경을 한강으로 바꿔줘"`,
        },
      ]);
    }
  };

  return (
    <div className="flex flex-col gap-3 border-t border-white/10 pt-4">
      <p className="text-white/40 text-xs">패널 수정하기 — 예: "3번 패널 배경을 한강 야경으로"</p>

      {/* Message history */}
      {messages.length > 0 && (
        <div className="flex flex-col gap-2 max-h-48 overflow-y-auto">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`text-sm px-3 py-2 rounded-xl w-fit max-w-[85%] ${
                m.role === "user"
                  ? "bg-white text-black self-end"
                  : "bg-white/10 text-white self-start"
              }`}
            >
              {m.text}
            </div>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex gap-2">
        <input
          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-white text-sm placeholder:text-white/30 focus:outline-none focus:border-white/30"
          placeholder="패널 수정 지시..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button
          onClick={handleSend}
          className="bg-white text-black text-sm font-bold px-4 rounded-xl"
        >
          전송
        </button>
      </div>
    </div>
  );
}
