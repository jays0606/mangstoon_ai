"use client";

import { useState } from "react";
import StoryInput from "./components/StoryInput";
import WebtoonViewer from "./components/WebtoonViewer";
import ChatEditor from "./components/ChatEditor";

export type Panel = {
  panel_number: number;
  image_url: string;
  dialogue: string[];
  narration: string;
  image_prompt: string;
  loading?: boolean;
};

export default function Home() {
  const [panels, setPanels] = useState<Panel[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [characterDescription, setCharacterDescription] = useState("");

  const handleGenerate = async (story: string, selfieFile?: File) => {
    setIsGenerating(true);
    setPanels([]);

    const formData = new FormData();
    formData.append("story", story);
    if (selfieFile) formData.append("selfie", selfieFile);

    const res = await fetch("/api/generate", { method: "POST", body: formData });
    const data = await res.json();

    setCharacterDescription(data.character_description ?? "");
    setPanels(data.panels ?? []);
    setIsGenerating(false);
  };

  const handleEdit = async (panelNumber: number, instruction: string) => {
    setPanels((prev) =>
      prev.map((p) => (p.panel_number === panelNumber ? { ...p, loading: true } : p))
    );

    const res = await fetch("/api/edit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        panel_number: panelNumber,
        instruction,
        character_description: characterDescription,
        original_image_prompt:
          panels.find((p) => p.panel_number === panelNumber)?.image_prompt ?? "",
      }),
    });
    const data = await res.json();

    setPanels((prev) =>
      prev.map((p) =>
        p.panel_number === panelNumber
          ? { ...p, image_url: data.image_url, loading: false }
          : p
      )
    );
  };

  return (
    <main className="min-h-screen bg-[#0f0f0f]">
      <div className="sticky top-0 z-10 bg-[#0f0f0f]/90 backdrop-blur border-b border-white/10 px-4 py-3">
        <h1 className="text-xl font-bold text-center text-white">🌀 망상툰AI</h1>
      </div>

      <div className="max-w-md mx-auto px-4 py-6 flex flex-col gap-6">
        <StoryInput onGenerate={handleGenerate} isGenerating={isGenerating} />

        {(panels.length > 0 || isGenerating) && (
          <WebtoonViewer panels={panels} isGenerating={isGenerating} />
        )}

        {panels.length > 0 && (
          <ChatEditor panels={panels} onEdit={handleEdit} />
        )}
      </div>
    </main>
  );
}
