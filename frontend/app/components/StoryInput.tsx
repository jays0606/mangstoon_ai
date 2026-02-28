"use client";

import { useState, useRef } from "react";

type Props = {
  onGenerate: (story: string, selfieFile?: File) => void;
  isGenerating: boolean;
};

export default function StoryInput({ onGenerate, isGenerating }: Props) {
  const [story, setStory] = useState("");
  const [selfieFile, setSelfieFile] = useState<File | null>(null);
  const [selfiePreview, setSelfiePreview] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleSelfie = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelfieFile(file);
    setSelfiePreview(URL.createObjectURL(file));
  };

  const handleSubmit = () => {
    if (!story.trim() || isGenerating) return;
    onGenerate(story.trim(), selfieFile ?? undefined);
  };

  return (
    <div className="flex flex-col gap-3">
      {/* Selfie upload */}
      <div
        className="flex items-center gap-3 cursor-pointer"
        onClick={() => fileRef.current?.click()}
      >
        <div className="w-14 h-14 rounded-full border-2 border-dashed border-white/30 flex items-center justify-center overflow-hidden bg-white/5 shrink-0">
          {selfiePreview ? (
            <img src={selfiePreview} alt="selfie" className="w-full h-full object-cover" />
          ) : (
            <span className="text-2xl">📸</span>
          )}
        </div>
        <span className="text-sm text-white/50">
          {selfieFile ? selfieFile.name : "셀카 업로드 (선택)"}
        </span>
        <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleSelfie} />
      </div>

      {/* Story input */}
      <textarea
        className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white placeholder:text-white/30 text-sm resize-none focus:outline-none focus:border-white/30"
        rows={4}
        placeholder={"당신의 망상을 입력하세요...\n예: 나는 이 해커톤 1등하고 비즈니스석 타고 미국 가서 지수 만남"}
        value={story}
        onChange={(e) => setStory(e.target.value)}
      />

      <button
        onClick={handleSubmit}
        disabled={!story.trim() || isGenerating}
        className="w-full bg-white text-black font-bold py-3 rounded-xl disabled:opacity-30 transition-opacity"
      >
        {isGenerating ? "생성 중..." : "🌀 망상툰 만들기"}
      </button>
    </div>
  );
}
