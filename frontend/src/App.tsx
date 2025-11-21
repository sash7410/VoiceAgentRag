import React, { useCallback, useMemo, useState } from "react";
import { CallControls } from "./components/CallControls";
import { Transcript, TranscriptLine } from "./components/Transcript";
import { useSkylineLiveKit } from "./livekitClient";

const App: React.FC = () => {
  const [transcript, setTranscript] = useState<TranscriptLine[]>([]);

  const appendLine = useCallback((line: Omit<TranscriptLine, "id">) => {
    setTranscript((prev) => [
      ...prev,
      {
        id: `${Date.now()}-${prev.length}`,
        ...line
      }
    ]);
  }, []);

  const { isConnected, startCall, endCall } = useSkylineLiveKit({
    onTranscript: appendLine
  });

  const infoMessage = useMemo(() => {
    if (!import.meta.env.VITE_LIVEKIT_URL || !import.meta.env.VITE_LIVEKIT_TOKEN) {
      return "Set VITE_LIVEKIT_URL and VITE_LIVEKIT_TOKEN in frontend/.env.local before starting a call.";
    }
    return undefined;
  }, []);

  return (
    <div className="app-root">
      <header className="app-header">
        <h1>Skyline Motors Voice Concierge</h1>
        <p className="app-subtitle">
          Talk to a friendly Skyline concierge about models, warranties, and financing.
        </p>
      </header>

      <main className="app-main">
        <section className="card">
          <CallControls
            isConnected={isConnected}
            onStart={startCall}
            onEnd={endCall}
          />
          {infoMessage && (
            <p className="hint-text">
              {infoMessage}
            </p>
          )}
        </section>

        <section className="card transcript-card">
          <h2>Live Transcript</h2>
          <Transcript lines={transcript} />
        </section>
      </main>
    </div>
  );
};

export default App;


