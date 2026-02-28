"use client";

import { Panel } from "../page";
import { useState, useEffect, useCallback } from "react";

type Props = {
  panels: Panel[];
  isGenerating: boolean;
  selectedPanels: number[];
  onSelectPanels: (panels: number[]) => void;
  genProgress: { current: number; total: number };
  styleName: string;
  storyTitle: string;
  characterImage?: string;
  userStory?: string;
};

const PANEL_GRADIENTS = [
  "linear-gradient(160deg, #e8e4dc, #ddd8ce)",
  "linear-gradient(160deg, #e4e4ec, #d8d8e8)",
  "linear-gradient(160deg, #ece8e0, #e4dcd0)",
  "linear-gradient(160deg, #e0e8e8, #d4e0e0)",
  "linear-gradient(160deg, #ece4ec, #e4d8e8)",
  "linear-gradient(160deg, #e4e4ec, #dcdce8)",
  "linear-gradient(160deg, #ece4e4, #e8d8d8)",
  "linear-gradient(160deg, #e4ece4, #d8e4d8)",
  "linear-gradient(160deg, #e8e4ec, #dcd4e4)",
  "linear-gradient(160deg, #e4e8ec, #d8dce4)",
  "linear-gradient(160deg, #ece8e0, #e4dcd0)",
  "linear-gradient(160deg, #e4e8ec, #d8dce4)",
];

function getChapter(panelNumber: number): number {
  return Math.ceil(panelNumber / 6);
}

export default function WebtoonViewer({
  panels,
  isGenerating,
  selectedPanels,
  onSelectPanels,
  genProgress,
  styleName,
  storyTitle,
  characterImage,
  userStory,
}: Props) {
  const [viewMode, setViewMode] = useState<"grid" | "scroll">("grid");
  const [zoomedPanel, setZoomedPanel] = useState<Panel | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const _fullView = false; // removed feature

  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }, []);

  useEffect(() => {
    const handler = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", handler);
    return () => document.removeEventListener("fullscreenchange", handler);
  }, []);

  const donePanels = panels.filter((p) => p.status === "done").length;
  const donePanelsList = panels.filter((p) => p.status === "done");

  // Loading step progression
  const [loadingStep, setLoadingStep] = useState(0);
  useEffect(() => {
    if (!isGenerating || panels.length > 0) {
      setLoadingStep(0);
      return;
    }
    const t1 = setTimeout(() => setLoadingStep(1), 3000);
    const t2 = setTimeout(() => setLoadingStep(2), 8000);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [isGenerating, panels.length]);

  // Lightbox navigation
  const zoomedIdx = zoomedPanel
    ? donePanelsList.findIndex((p) => p.panel_number === zoomedPanel.panel_number)
    : -1;

  const goLightboxPrev = useCallback(() => {
    if (zoomedIdx > 0) setZoomedPanel(donePanelsList[zoomedIdx - 1]);
  }, [zoomedIdx, donePanelsList]);

  const goLightboxNext = useCallback(() => {
    if (zoomedIdx < donePanelsList.length - 1) setZoomedPanel(donePanelsList[zoomedIdx + 1]);
  }, [zoomedIdx, donePanelsList]);

  // Keyboard navigation for lightbox + full view
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (zoomedPanel) {
          setZoomedPanel(null);
          if (document.fullscreenElement) document.exitFullscreen();
        }
      }
      if (zoomedPanel) {
        if (e.key === "ArrowLeft") goLightboxPrev();
        if (e.key === "ArrowRight") goLightboxNext();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [zoomedPanel, goLightboxPrev, goLightboxNext]);

  const handlePanelClick = (panelNumber: number, shiftKey: boolean) => {
    if (shiftKey) {
      const isSelected = selectedPanels.includes(panelNumber);
      if (isSelected) {
        onSelectPanels(selectedPanels.filter((n) => n !== panelNumber));
      } else {
        onSelectPanels([...selectedPanels, panelNumber].sort((a, b) => a - b));
      }
    } else {
      if (selectedPanels.length === 1 && selectedPanels[0] === panelNumber) {
        onSelectPanels([]);
      } else {
        onSelectPanels([panelNumber]);
      }
    }
  };

  const handlePanelDoubleClick = (panel: Panel) => {
    if (panel.status === "done" && panel.image_url) {
      setZoomedPanel(panel);
    }
  };

  const renderPanelCard = (panel: Panel, idx: number) => {
    const isSelected = selectedPanels.includes(panel.panel_number);
    return (
      <div
        className={`panel-card ${
          panel.status === "done"
            ? "panel-card-done"
            : panel.status === "gen"
            ? "panel-card-gen"
            : "panel-card-wait"
        } ${isSelected ? "selected" : ""}`}
        style={{
          background:
            panel.status === "done" && panel.image_url
              ? undefined
              : PANEL_GRADIENTS[idx % PANEL_GRADIENTS.length],
          outline: isSelected
            ? selectedPanels.length > 1
              ? "2px solid var(--gold)"
              : "2px solid var(--red)"
            : undefined,
          outlineOffset: isSelected ? "2px" : undefined,
          boxShadow: isSelected
            ? selectedPanels.length > 1
              ? "0 0 14px rgba(255, 214, 10, 0.18)"
              : "0 0 14px rgba(255, 45, 85, 0.2)"
            : undefined,
        }}
        onClick={(e) => {
          if (panel.status === "done") {
            handlePanelClick(panel.panel_number, e.shiftKey);
          }
        }}
        onDoubleClick={() => handlePanelDoubleClick(panel)}
        title={
          panel.status === "done"
            ? `Panel #${panel.panel_number}${panel.narration ? ` · ${panel.narration}` : ""}\nDouble-click to zoom · ${
                selectedPanels.length > 0
                  ? "Shift+click to add to selection"
                  : "Click to select · Shift+click to multi-select"
              }`
            : undefined
        }
      >
        {/* Panel number badge */}
        <div className="panel-badge">{panel.panel_number}</div>

        {panel.status === "done" && panel.image_url ? (
          <>
            <img
              src={panel.image_url}
              alt={`Panel ${panel.panel_number}`}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
              draggable={false}
            />
            {/* Multi-select indicator */}
            {isSelected && selectedPanels.length > 1 && (
              <div
                style={{
                  position: "absolute",
                  top: 5,
                  left: 5,
                  width: 16,
                  height: 16,
                  borderRadius: "50%",
                  background: "var(--gold)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  zIndex: 10,
                  fontSize: 9,
                  fontWeight: 700,
                  color: "#000",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {selectedPanels.indexOf(panel.panel_number) + 1}
              </div>
            )}
            {/* Zoom hint on hover */}
            <div className="panel-zoom-hint">⤢</div>
          </>
        ) : panel.status === "gen" ? (
          <div className="panel-gen-content">
            <div className="panel-gen-icon" />
            <div className="panel-gen-text">Rendering</div>
            {panel.narration && (
              <div style={{
                fontFamily: "var(--font-mono)",
                fontSize: "7px",
                color: "rgba(17,17,17,0.25)",
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                marginTop: 2,
              }}>{panel.narration}</div>
            )}
            {panel.dialogue?.[0] && (
              <div style={{
                fontFamily: "var(--font-body)",
                fontSize: "9px",
                color: "rgba(17,17,17,0.3)",
                textAlign: "center",
                padding: "0 12px",
                lineHeight: 1.4,
                maxWidth: "90%",
                marginTop: 4,
              }}>"{panel.dialogue[0]}"</div>
            )}
          </div>
        ) : (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
            }}
          >
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                color: "rgba(17,17,17,0.15)",
                letterSpacing: "0.06em",
              }}
            >
              {panel.panel_number}
            </span>
          </div>
        )}
      </div>
    );
  };

  const showLoadingState = isGenerating && panels.length === 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {/* Header */}
      <div className="panel-grid-header">
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div className="panel-grid-label">
            Mangstoon · {styleName || "K-Webtoon"}
          </div>
          {panels.length > 0 && (
            <span className="panel-grid-count" style={{ margin: 0 }}>
              {donePanels}/{panels.length}
            </span>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {selectedPanels.length > 0 && (
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "9px",
                color: "var(--red)",
                letterSpacing: "0.06em",
              }}
            >
              {selectedPanels.length === 1
                ? `#${selectedPanels[0]} selected`
                : `${selectedPanels.length} selected`}
            </div>
          )}
          {panels.length > 0 && (
            <div className="view-toggle">
              <button
                className={`view-toggle-btn ${viewMode === "grid" ? "active" : ""}`}
                onClick={() => setViewMode("grid")}
                title="Grid view"
              >
                ⊞
              </button>
              <button
                className={`view-toggle-btn ${viewMode === "scroll" ? "active" : ""}`}
                onClick={() => setViewMode("scroll")}
                title="Scroll view"
              >
                ☰
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Panel content */}
      <div style={{ flex: 1, overflowY: "auto" }}>
        {/* Loading state — crafting storyboard */}
        {showLoadingState && (
          <div className="loading-state fade-in">
            <div className="loading-orb">
              <div className="loading-orb-ring" />
              <div className="loading-orb-ring" />
              <div className="loading-orb-ring" />
              <div className="loading-orb-center" />
            </div>
            {userStory && (
              <div style={{
                fontFamily: "var(--font-body)",
                fontSize: "13px",
                color: "var(--dim)",
                textAlign: "center",
                maxWidth: 320,
                lineHeight: 1.5,
                fontStyle: "italic",
              }}>
                &ldquo;{userStory.length > 80 ? userStory.slice(0, 80).trimEnd() + "..." : userStory}&rdquo;
              </div>
            )}
            <div className="loading-title">Crafting your webtoon</div>
            <div className="loading-subtitle">This takes about 30 seconds</div>
            <div className="loading-steps">
              <div className={`loading-step ${loadingStep === 0 ? "active" : "done"}`}>
                <div className="loading-step-dot" />
                {loadingStep > 0 ? "Story analyzed" : "Analyzing story structure"}
              </div>
              <div className={`loading-step ${loadingStep === 1 ? "active" : loadingStep > 1 ? "done" : ""}`}>
                <div className="loading-step-dot" />
                {loadingStep > 1 ? "Storyboard ready" : "Building 5-act storyboard"}
              </div>
              <div className={`loading-step ${loadingStep === 2 ? "active" : ""}`}>
                <div className="loading-step-dot" />
                Generating panel images
              </div>
            </div>
          </div>
        )}
        {/* Story title */}
        {storyTitle && storyTitle !== "Generating..." && (
          <div style={{
            padding: "16px 20px 4px",
            fontFamily: "var(--font-display)",
            fontSize: "18px",
            color: "var(--text)",
            lineHeight: 1.2,
            textAlign: "center",
          }}>
            {storyTitle}
          </div>
        )}

        {/* Character Reference Sheet */}
        {characterImage && (
          <div style={{
            display: "flex",
            justifyContent: "center",
            padding: "12px 16px 4px",
          }}>
            <div style={{
              position: "relative",
              width: 120,
              height: 120,
              borderRadius: 12,
              overflow: "hidden",
              border: "1px solid var(--border)",
              flexShrink: 0,
            }}>
              <img
                src={characterImage}
                alt="Character reference"
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
                draggable={false}
              />
              <div style={{
                position: "absolute",
                bottom: 0,
                left: 0,
                right: 0,
                padding: "2px 6px",
                background: "rgba(0,0,0,0.65)",
                fontFamily: "var(--font-mono)",
                fontSize: "8px",
                color: "rgba(255,255,255,0.7)",
                letterSpacing: "0.06em",
                textAlign: "center",
              }}>
                CHARACTER REF
              </div>
            </div>
          </div>
        )}

        {/* Grid view */}
        {viewMode === "grid" && (
          <div className="panel-grid">
            {panels.map((panel, idx) => {
              const chapter = getChapter(panel.panel_number);
              const prevChapter = idx > 0 ? getChapter(panels[idx - 1].panel_number) : 0;
              const showDivider = chapter !== prevChapter;

              return (
                <div key={panel.panel_number} style={{ display: "contents" }}>
                  {showDivider && (
                    <div className="chapter-divider">Ch.{chapter}</div>
                  )}
                  {renderPanelCard(panel, idx)}
                </div>
              );
            })}
          </div>
        )}

        {/* Scroll view */}
        {viewMode === "scroll" && (
          <div className="panel-scroll">
            {panels.map((panel, idx) => {
              const chapter = getChapter(panel.panel_number);
              const prevChapter = idx > 0 ? getChapter(panels[idx - 1].panel_number) : 0;
              const showDivider = chapter !== prevChapter;

              return (
                <div key={panel.panel_number}>
                  {showDivider && (
                    <div className="scroll-chapter-divider">Chapter {chapter}</div>
                  )}
                  <div className="panel-scroll-item">
                    {renderPanelCard(panel, idx)}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Multi-select hint */}
        {panels.some((p) => p.status === "done") && (
          <div className="multiselect-hint" style={{ paddingBottom: 16 }}>
            Double-click to zoom · Shift+click to multi-select
          </div>
        )}
      </div>

      {/* Generation Progress Bar */}
      {(isGenerating || (donePanels < panels.length && panels.length > 0)) && (
        <div className="gen-progress-bar">
          <div className="gen-progress-track">
            <div
              className="gen-progress-fill"
              style={{
                width: `${panels.length > 0 ? (donePanels / panels.length) * 100 : 0}%`,
              }}
            />
          </div>
          <span className="gen-progress-text">
            {donePanels}/{panels.length}
          </span>
        </div>
      )}

      {/* Lightbox */}
      {zoomedPanel && (
        <div
          className="lightbox-overlay"
          onClick={() => setZoomedPanel(null)}
        >
          <div className="lightbox-inner" onClick={(e) => e.stopPropagation()}>
            {/* Close */}
            <button className="lightbox-close" onClick={() => setZoomedPanel(null)}>✕</button>
            {/* Fullscreen */}
            <button className="lightbox-fullscreen" onClick={toggleFullscreen} title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}>
              {isFullscreen ? "⊡" : "⛶"}
            </button>

            {/* Panel info */}
            <div className="lightbox-meta">
              <span className="lightbox-num">#{zoomedPanel.panel_number}</span>
              {zoomedPanel.narration && (
                <span className="lightbox-act">{zoomedPanel.narration}</span>
              )}
              <span className="lightbox-counter">
                {zoomedIdx + 1} / {donePanelsList.length}
              </span>
            </div>

            {/* Prev arrow */}
            {zoomedIdx > 0 && (
              <button className="lightbox-nav lightbox-nav-prev" onClick={goLightboxPrev}>
                ‹
              </button>
            )}

            {/* Image */}
            <img
              src={zoomedPanel.image_url}
              alt={`Panel ${zoomedPanel.panel_number}`}
              className="lightbox-image"
              draggable={false}
            />

            {/* Next arrow */}
            {zoomedIdx < donePanelsList.length - 1 && (
              <button className="lightbox-nav lightbox-nav-next" onClick={goLightboxNext}>
                ›
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
