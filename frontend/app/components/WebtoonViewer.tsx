"use client";

import { Panel } from "../page";

type Props = {
  panels: Panel[];
  isGenerating: boolean;
};

export default function WebtoonViewer({ panels, isGenerating }: Props) {
  return (
    <div className="flex flex-col gap-0">
      {panels.map((panel) => (
        <div key={panel.panel_number} className="webtoon-panel relative">
          {panel.loading ? (
            <div className="w-full aspect-[9/16] bg-white/5 flex items-center justify-center">
              <span className="text-white/40 text-sm animate-pulse">패널 수정 중...</span>
            </div>
          ) : (
            <img
              src={panel.image_url}
              alt={`Panel ${panel.panel_number}`}
              className="w-full block"
            />
          )}

          {/* Dialogue overlay */}
          {panel.dialogue?.length > 0 && (
            <div className="absolute bottom-4 left-4 right-4 flex flex-col gap-1">
              {panel.dialogue.map((line, i) => (
                <div
                  key={i}
                  className="bg-white text-black text-xs font-medium px-3 py-1.5 rounded-xl shadow-md w-fit max-w-[80%]"
                >
                  {line}
                </div>
              ))}
            </div>
          )}

          {/* Narration */}
          {panel.narration && (
            <div className="bg-black/70 px-3 py-2 text-white/80 text-xs italic">
              {panel.narration}
            </div>
          )}
        </div>
      ))}

      {/* Loading skeleton for panels still generating */}
      {isGenerating && panels.length === 0 && (
        Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="w-full aspect-[9/16] bg-white/5 flex items-center justify-center border-b border-white/5">
            <span className="text-white/20 text-sm animate-pulse">패널 {i + 1} 생성 중...</span>
          </div>
        ))
      )}
    </div>
  );
}
