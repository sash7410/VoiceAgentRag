import React, { ChangeEvent, useCallback, useMemo, useState } from "react";
import { CallControls } from "./components/CallControls";
import { Transcript, TranscriptLine } from "./components/Transcript";
import { useSkylineLiveKit } from "./livekitClient";

const App: React.FC = () => {
  const [transcript, setTranscript] = useState<TranscriptLine[]>([]);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

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

  const handlePdfUpload = useCallback(async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadStatus("Uploading handbook PDF...");
    try {
      const formData = new FormData();
      formData.append("pdf", file);

      const response = await fetch("http://localhost:8000/upload-handbook", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const text = await response.text();
        setUploadStatus(
          `Upload failed (${response.status}): ${text || "see backend logs"}`
        );
        return;
      }

      setUploadStatus("Handbook uploaded successfully. New questions will use it.");
    } catch (err) {
      setUploadStatus("Upload failed – is the backend upload server running on :8000?");
    } finally {
      // Reset the input so the same file can be selected again if needed.
      event.target.value = "";
    }
  }, []);

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
          {!isConnected && infoMessage && (
            <p className="hint-text">
              {infoMessage}
            </p>
          )}
          {!isConnected && (
            <div className="upload-section">
              <label className="upload-label">
                <span>Optional: upload a custom dealer handbook PDF</span>
                <input
                  type="file"
                  accept="application/pdf"
                  onChange={handlePdfUpload}
                />
              </label>
              {uploadStatus && <p className="hint-text">{uploadStatus}</p>}
            </div>
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


