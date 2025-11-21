import React, { useEffect, useRef } from "react";

export interface TranscriptLine {
  id: string;
  speaker: "user" | "agent";
  text: string;
}

interface TranscriptProps {
  lines: TranscriptLine[];
}

export const Transcript: React.FC<TranscriptProps> = ({ lines }) => {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [lines]);

  return (
    <div className="transcript-container" ref={containerRef}>
      {lines.length === 0 && (
        <p className="hint-text">Transcript will appear here once the conversation starts.</p>
      )}
      {lines.map((line) => (
        <div
          key={line.id}
          className={`transcript-line transcript-${line.speaker}`}
        >
          <span className="transcript-speaker">
            {line.speaker === "user" ? "You" : "Agent"}:
          </span>
          <span className="transcript-text">{line.text}</span>
        </div>
      ))}
    </div>
  );
};


