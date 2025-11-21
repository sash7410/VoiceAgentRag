## Skyline Motors Frontend (React + Vite)

Minimal React client for the Skyline Motors voice concierge. It:

- Connects to LiveKit Cloud with a pre-generated token.
- Publishes microphone audio to the room.
- Plays the agent's audio.
- Shows a live transcript of user and agent messages.

### Setup

1. **Install Node dependencies**

From the project root:

```bash
cd frontend
npm install
```

2. **Configure LiveKit connection**

Create a `frontend/.env.local` file:

```bash
VITE_LIVEKIT_URL=wss://your-livekit-host
VITE_LIVEKIT_TOKEN=your_development_access_token
```

The token should join the same room (for example `skyline-showroom`) that the
Python agent worker listens to, with permissions to publish audio and subscribe
to audio/data.

3. **Run the dev server**

```bash
npm run dev
```

Then open the printed `http://localhost:5173` URL in your browser.

### Using the App

- Click **Start Call** to join the room and start streaming microphone audio.
- Speak to the agent; you should hear responses and see transcript lines appear,
  labeled as **You** (user) and **Agent**.
- Click **End Call** to disconnect cleanly.


