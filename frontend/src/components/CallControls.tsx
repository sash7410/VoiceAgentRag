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
  const handleClick = () => {
    if (isConnected) {
      void onEnd();
    } else {
      void onStart();
    }
  };

  return (
    <div className="call-controls">
      <button
        className="primary-button"
        onClick={handleClick}
      >
        {isConnected ? "End Call" : "Start Call"}
      </button>
    </div>
  );
};


