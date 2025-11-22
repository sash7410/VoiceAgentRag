import { useCallback, useEffect, useRef, useState } from "react";
import {
  RemoteAudioTrack,
  Room,
  RoomEvent,
  Track,
  createLocalAudioTrack
} from "livekit-client";
import type { TranscriptLine } from "./components/Transcript";

interface UseSkylineLiveKitOptions {
  onTranscript: (line: Omit<TranscriptLine, "id">) => void;
}

interface UseSkylineLiveKitResult {
  isConnected: boolean;
  startCall: () => Promise<void>;
  endCall: () => Promise<void>;
}

/**
 * Small React hook that wires a LiveKit Room for the Skyline Motors client.
 *
 * It:
 * - connects to LiveKit using VITE_LIVEKIT_URL and VITE_LIVEKIT_TOKEN
 * - publishes the local microphone
 * - attaches the agent's audio track to a hidden <audio> element
 * - listens for JSON data messages `{ speaker, text }` and forwards them
 *   to the provided `onTranscript` callback.
 */
export function useSkylineLiveKit(
  options: UseSkylineLiveKitOptions
): UseSkylineLiveKitResult {
  const { onTranscript } = options;
  const roomRef = useRef<Room | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  // Lazily create a single audio element for remote agent audio.
  useEffect(() => {
    const audio = new Audio();
    audio.autoplay = true;
    audioRef.current = audio;
    return () => {
      audio.srcObject = null;
      audioRef.current = null;
    };
  }, []);

  const startCall = useCallback(async () => {
    // If there is a lingering room instance for any reason, make sure it is
    // fully disconnected before starting a new call. This helps avoid cases
    // where LiveKit still thinks a participant is present.
    if (roomRef.current) {
      try {
        await roomRef.current.disconnect();
      } catch {
        // Ignore disconnect errors; we'll replace the room instance anyway.
      }
      roomRef.current = null;
      setIsConnected(false);
    }

    const url = import.meta.env.VITE_LIVEKIT_URL as string | undefined;
    const token = import.meta.env.VITE_LIVEKIT_TOKEN as string | undefined;

    if (!url || !token) {
      // Surface error in console; UI shows a hint message.
      console.error("VITE_LIVEKIT_URL and VITE_LIVEKIT_TOKEN must be set for calls.");
      return;
    }

    const room = new Room();

    // When the agent publishes audio, play it through our audio element.
    room.on(RoomEvent.TrackSubscribed, (track, _pub, _participant) => {
      if (track.kind === Track.Kind.Audio && audioRef.current) {
        const mediaStream = new MediaStream();
        // Attach the underlying MediaStreamTrack.
        mediaStream.addTrack((track as RemoteAudioTrack).mediaStreamTrack);
        audioRef.current.srcObject = mediaStream;
      }
    });

    // Listen for transcript updates forwarded by the backend agent.
    room.on(RoomEvent.DataReceived, (data) => {
      try {
        const decoded = JSON.parse(new TextDecoder().decode(data)) as {
          speaker?: "user" | "agent";
          text?: string;
        };
        if (!decoded.text || !decoded.speaker) {
          return;
        }
        onTranscript({
          speaker: decoded.speaker,
          text: decoded.text
        });
      } catch {
        // Ignore malformed messages.
      }
    });

    await room.connect(url, token);

    const micTrack = await createLocalAudioTrack();
    await room.localParticipant.publishTrack(micTrack);

    roomRef.current = room;
    setIsConnected(true);
  }, [onTranscript]);

  const endCall = useCallback(async () => {
    const room = roomRef.current;
    if (!room) return;

    roomRef.current = null;
    setIsConnected(false);

    try {
      await room.disconnect();
    } catch {
      // Swallow disconnect errors; nothing critical here.
    }
  }, []);

  useEffect(() => {
    return () => {
      // On unmount, make sure we clean up the room.
      if (roomRef.current) {
        roomRef.current.disconnect();
        roomRef.current = null;
      }
    };
  }, []);

  return {
    isConnected,
    startCall,
    endCall
  };
}


