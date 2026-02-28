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
    <div
      style={{
        background: "var(--ink-light)",
        border: "3px solid var(--white)",
        boxShadow: "6px 6px 0px var(--accent)",
        padding: "24px 20px",
        display: "flex",
        flexDirection: "column",
        gap: "20px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Corner label */}
      <div
        style={{
          position: "absolute",
          top: 0,
          right: 0,
          background: "var(--accent)",
          color: "var(--ink)",
          fontFamily: "var(--font-display)",
          fontSize: "10px",
          letterSpacing: "0.15em",
          padding: "4px 10px",
          fontWeight: 900,
        }}
      >
        CREATE
      </div>

      {/* Title */}
      <div>
        <h2
          style={{
            fontFamily: "var(--font-display)",
            fontSize: "28px",
            color: "var(--white)",
            lineHeight: 1,
            margin: 0,
            letterSpacing: "-0.02em",
          }}
        >
          망상 입력
        </h2>
        <p
          style={{
            color: "var(--text-dim)",
            fontSize: "11px",
            marginTop: "4px",
            fontFamily: "var(--font-body)",
            letterSpacing: "0.05em",
          }}
        >
          당신의 망상을 웹툰으로 만들어드립니다
        </p>
      </div>

      {/* Selfie upload */}
      <div
        style={{ display: "flex", alignItems: "center", gap: "14px" }}
      >
        <button
          onClick={() => fileRef.current?.click()}
          style={{
            width: "72px",
            height: "72px",
            borderRadius: "50%",
            border: selfiePreview ? "3px solid var(--accent)" : "3px dashed rgba(255,255,255,0.3)",
            background: selfiePreview ? "transparent" : "rgba(255,255,255,0.04)",
            overflow: "hidden",
            cursor: "pointer",
            flexShrink: 0,
            padding: 0,
            position: "relative",
            transition: "border-color 0.2s, box-shadow 0.2s",
            boxShadow: selfiePreview ? "0 0 0 3px var(--ink), 0 0 0 6px var(--accent)" : "none",
          }}
          aria-label="셀카 업로드"
        >
          {selfiePreview ? (
            <img
              src={selfiePreview}
              alt="selfie"
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
                gap: "2px",
              }}
            >
              <span style={{ fontSize: "22px" }}>📸</span>
            </div>
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
              fontFamily: "var(--font-display)",
              fontSize: "13px",
              color: selfieFile ? "var(--accent)" : "rgba(255,255,255,0.5)",
              letterSpacing: "0.08em",
            }}
          >
            {selfieFile ? "주인공 등록됨" : "주인공 사진 (선택)"}
          </div>
          {!selfieFile && (
            <button
              onClick={() => fileRef.current?.click()}
              style={{
                marginTop: "4px",
                background: "none",
                border: "1.5px solid rgba(255,255,255,0.2)",
                color: "rgba(255,255,255,0.5)",
                fontSize: "11px",
                padding: "3px 10px",
                cursor: "pointer",
                fontFamily: "var(--font-body)",
                letterSpacing: "0.05em",
                transition: "all 0.15s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "var(--accent)";
                e.currentTarget.style.color = "var(--accent)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "rgba(255,255,255,0.2)";
                e.currentTarget.style.color = "rgba(255,255,255,0.5)";
              }}
            >
              업로드
            </button>
          )}
          {selfieFile && (
            <button
              onClick={() => { setSelfieFile(null); setSelfiePreview(null); }}
              style={{
                marginTop: "4px",
                background: "none",
                border: "none",
                color: "rgba(255,255,255,0.3)",
                fontSize: "11px",
                cursor: "pointer",
                padding: 0,
                fontFamily: "var(--font-body)",
              }}
            >
              ✕ 삭제
            </button>
          )}
        </div>
      </div>

      {/* Story textarea */}
      <div style={{ position: "relative" }}>
        <div
          style={{
            position: "absolute",
            top: "-10px",
            left: "12px",
            background: "var(--ink-light)",
            padding: "0 6px",
            fontFamily: "var(--font-display)",
            fontSize: "10px",
            color: "var(--accent)",
            letterSpacing: "0.12em",
            zIndex: 1,
          }}
        >
          STORY
        </div>
        <textarea
          style={{
            width: "100%",
            background: "rgba(255,255,255,0.03)",
            border: "2px solid rgba(255,255,255,0.2)",
            borderLeft: "4px solid var(--accent)",
            color: "var(--white)",
            fontFamily: "var(--font-body)",
            fontSize: "14px",
            lineHeight: "1.7",
            padding: "16px 14px",
            resize: "none",
            minHeight: "110px",
            transition: "border-color 0.2s",
          }}
          rows={4}
          placeholder={"당신의 망상을 입력하세요...\n예: 나는 해커톤 1등하고 비즈니스석 타고 미국 가서 지수 만남"}
          value={story}
          onChange={(e) => setStory(e.target.value)}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = "rgba(255,255,255,0.4)";
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = "rgba(255,255,255,0.2)";
          }}
        />
      </div>

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={!story.trim() || isGenerating}
        style={{
          width: "100%",
          background: isGenerating
            ? "rgba(255, 229, 0, 0.2)"
            : story.trim()
            ? "var(--accent)"
            : "rgba(255,255,255,0.08)",
          border: "3px solid",
          borderColor: isGenerating
            ? "var(--accent)"
            : story.trim()
            ? "var(--accent)"
            : "rgba(255,255,255,0.15)",
          color: isGenerating
            ? "var(--accent)"
            : story.trim()
            ? "var(--ink)"
            : "rgba(255,255,255,0.2)",
          fontFamily: "var(--font-display)",
          fontSize: "18px",
          letterSpacing: "0.05em",
          padding: "16px 0",
          cursor: story.trim() && !isGenerating ? "pointer" : "not-allowed",
          transition: "all 0.2s",
          position: "relative",
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "8px",
        }}
        onMouseEnter={(e) => {
          if (story.trim() && !isGenerating) {
            e.currentTarget.style.boxShadow = "4px 4px 0 rgba(0,0,0,0.6)";
            e.currentTarget.style.transform = "translate(-2px, -2px)";
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.boxShadow = "none";
          e.currentTarget.style.transform = "translate(0, 0)";
        }}
      >
        {isGenerating ? (
          <>
            <span
              style={{
                display: "inline-block",
                width: "16px",
                height: "16px",
                border: "2px solid var(--accent)",
                borderTopColor: "transparent",
                borderRadius: "50%",
                animation: "spin 0.7s linear infinite",
              }}
            />
            생성 중...
          </>
        ) : (
          <>
            🌀 망상툰 만들기
          </>
        )}
      </button>
    </div>
  );
}
