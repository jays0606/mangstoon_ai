"use client";

import { Panel } from "../page";

type Props = {
  panels: Panel[];
  isGenerating: boolean;
  selectedPanel: number | null;
  onSelectPanel: (n: number | null) => void;
  genProgress: { current: number; total: number };
  styleName: string;
  storyTitle: string;
};

const PANEL_GRADIENTS = [
  "linear-gradient(135deg, #1a1a2e, #16213e)",
  "linear-gradient(135deg, #1a1a2e, #0f3460)",
  "linear-gradient(135deg, #162447, #1f4068)",
  "linear-gradient(135deg, #1b1b2f, #462255)",
  "linear-gradient(135deg, #2d1b69, #11001c)",
  "linear-gradient(135deg, #1a1a2e, #e94560)",
  "linear-gradient(135deg, #0c0c1d, #1a1a3e)",
  "linear-gradient(135deg, #1a0a2e, #3a0a5e)",
  "linear-gradient(135deg, #0a1628, #1a3a5e)",
  "linear-gradient(135deg, #1e0a0a, #3e1a1a)",
  "linear-gradient(135deg, #0a1e0a, #1a3e1a)",
  "linear-gradient(135deg, #1e1e0a, #3e3e1a)",
  "linear-gradient(135deg, #1a1a2e, #2e1a3e)",
  "linear-gradient(135deg, #0a0a1e, #1a1a4e)",
  "linear-gradient(135deg, #1e0a1a, #4e1a3a)",
  "linear-gradient(135deg, #0a1e1e, #1a3e3e)",
  "linear-gradient(135deg, #1a0a0a, #4e1a1a)",
  "linear-gradient(135deg, #0a0a2e, #1a1a5e)",
  "linear-gradient(135deg, #1e1a0a, #4e3a1a)",
  "linear-gradient(135deg, #0a1a0a, #1a4a1a)",
  "linear-gradient(135deg, #1a0a1e, #3a1a4e)",
  "linear-gradient(135deg, #0e0a1e, #2e1a4e)",
  "linear-gradient(135deg, #1a1a0a, #3e3e1a)",
  "linear-gradient(135deg, #0a0e1e, #1a2e4e)",
];

const PANEL_EMOJIS = [
  "💻", "🏆", "✈️", "🎵", "💫", "🌟",
  "🔥", "💎", "🎭", "🌙", "⚡", "🎪",
  "🌊", "🎯", "💝", "🚀", "🎸", "🌈",
  "🦋", "👑", "🎬", "💐", "🏔️", "🎇",
];

function getChapter(panelNumber: number): number {
  return Math.ceil(panelNumber / 6);
}

export default function WebtoonViewer({
  panels,
  isGenerating,
  selectedPanel,
  onSelectPanel,
  genProgress,
  styleName,
  storyTitle,
}: Props) {
  const donePanels = panels.filter((p) => p.status === "done").length;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {/* Header */}
      <div className="panel-grid-header">
        <div>
          <span className="panel-grid-title">
            MANGSTOON · {styleName || "K-WEBTOON"}
          </span>
          {storyTitle && (
            <div className="panel-grid-subtitle">{storyTitle}</div>
          )}
        </div>
        <span className="panel-grid-title">
          {donePanels}/{panels.length} PANELS
        </span>
      </div>

      {/* Panel Grid */}
      <div style={{ flex: 1, overflowY: "auto" }}>
        <div className="panel-grid">
          {panels.map((panel, idx) => {
            const chapter = getChapter(panel.panel_number);
            const prevChapter = idx > 0 ? getChapter(panels[idx - 1].panel_number) : 0;
            const showDivider = chapter !== prevChapter;

            return (
              <div key={panel.panel_number} style={{ display: "contents" }}>
                {showDivider && (
                  <div className="chapter-divider">
                    CH.{chapter}
                  </div>
                )}
                <div
                  className={`panel-card ${
                    panel.status === "done"
                      ? "panel-card-done"
                      : panel.status === "gen"
                      ? "panel-card-gen"
                      : "panel-card-wait"
                  } ${selectedPanel === panel.panel_number ? "selected" : ""}`}
                  style={{
                    background:
                      panel.status === "done" && panel.image_url
                        ? undefined
                        : PANEL_GRADIENTS[idx % PANEL_GRADIENTS.length],
                  }}
                  onClick={() => {
                    if (panel.status === "done") {
                      onSelectPanel(
                        selectedPanel === panel.panel_number ? null : panel.panel_number
                      );
                    }
                  }}
                >
                  {/* Badge */}
                  <div className="panel-badge">{panel.panel_number}</div>

                  {panel.status === "done" && panel.image_url ? (
                    <>
                      <img
                        src={panel.image_url}
                        alt={`Panel ${panel.panel_number}`}
                        style={{
                          width: "100%",
                          height: "100%",
                          objectFit: "cover",
                        }}
                      />
                      {/* Narration overlay */}
                      {panel.narration && (
                        <div className="panel-narration">{panel.narration}</div>
                      )}
                      {/* Dialogue overlay */}
                      {panel.dialogue?.length > 0 && (
                        <div className="panel-dialogue">
                          {panel.dialogue.map((line, i) => (
                            <div key={i} className="speech-bubble">
                              {line}
                            </div>
                          ))}
                        </div>
                      )}
                    </>
                  ) : panel.status === "gen" ? (
                    <div className="panel-gen-content">
                      <div className="panel-gen-icon">🌀</div>
                      <div className="panel-gen-text">GENERATING</div>
                    </div>
                  ) : panel.status === "done" ? (
                    /* Done but no image (placeholder) */
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        height: "100%",
                      }}
                    >
                      <span style={{ fontSize: "32px", opacity: 0.5 }}>
                        {PANEL_EMOJIS[idx % PANEL_EMOJIS.length]}
                      </span>
                    </div>
                  ) : (
                    /* wait state — mostly invisible */
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        height: "100%",
                      }}
                    >
                      <span style={{ fontSize: "20px", opacity: 0.15 }}>
                        {PANEL_EMOJIS[idx % PANEL_EMOJIS.length]}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Generation Progress Bar */}
      {(isGenerating || donePanels < panels.length) && panels.length > 0 && (
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
            {donePanels}/{panels.length} panels complete
          </span>
        </div>
      )}
    </div>
  );
}
