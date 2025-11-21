import React from "react";

interface CallControlsProps {
  isConnected: boolean;
  onStart: () => Promise<void> | void;
  onEnd: () => Promise<void> | void;
}

export const CallControls: React.FC<CallControlsProps> = ({
  isConnected,
  onStart,
  onEnd
}) => {
  return (
    <div className="call-controls">
      <button
        className="primary-button"
        onClick={() => onStart()}
        disabled={isConnected}
      >
        Start Call
      </button>
      <button
        className="secondary-button"
        onClick={() => onEnd()}
        disabled={!isConnected}
      >
        End Call
      </button>
    </div>
  );
};


