## Skyline Motors Voice Concierge

Minimal V1 of a RAG‑enabled voice agent for a fictional car dealership, Skyline Motors.
The system uses LiveKit Cloud for real‑time voice, a Python backend agent, and a
React frontend client.

### High‑Level Architecture

- **LiveKit Cloud**: media server and room host. The browser client and the Python
  LiveKit Agent join the same room.
- **Backend (Python)**:
  - `backend/agent.py`: LiveKit Agent entrypoint using `livekit-agents` and
    `livekit-plugins-openai` for STT, LLM, and TTS.
  - `backend/rag/handbook_rag.py`: RAG pipeline over `backend/resources/dealer_handbook.pdf`.
  - `backend/tools.py`: single mocked inventory search tool.
  - `backend/config.py`: environment and configuration loading.
- **Frontend (React)**:
  - Simple single‑page UI with Start Call / End Call buttons and a live transcript.
  - Connects to LiveKit, publishes microphone audio, plays agent audio, and
    displays transcript events sent from the backend via LiveKit data messages.

### Backend Setup

1. **Create and activate virtualenv**

```bash
cd /Users/sashank/Downloads/Projects/VoiceAgentRag
python -m venv .venv
source .venv/bin/activate
```

2. **Install backend dependencies**

```bash
pip install -r backend/requirements.txt
```

3. **Configure environment**

Create a `.env` file in the project root with your actual API keys:

```bash
cat > .env << 'EOF'
LIVEKIT_URL=wss://your-livekit-host.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_ROOM_NAME=skyline-showroom
OPENAI_API_KEY=sk-proj-...your_valid_openai_key...
EOF
```

**Important**: Make sure your OpenAI API key is valid and has credits. The system uses:
- `gpt-4o-mini` for LLM reasoning
- `whisper-1` for speech-to-text
- `tts-1` for text-to-speech
- `text-embedding-3-small` for RAG embeddings

4. **Generate the dealer handbook PDF (only needed if you change it)**

The repository includes `backend/resources/make_dealer_handbook.py` which can
regenerate the synthetic handbook:

```bash
python backend/resources/make_dealer_handbook.py
```

This writes `backend/resources/dealer_handbook.pdf`, which the RAG layer indexes.

5. **Run backend services (agent worker + upload helper server)**

For local development you can start both the LiveKit agent worker and the
optional upload helper server from a *single* terminal:

```bash
python scripts/run_backend.py
```

This is equivalent to running:

```bash
python -m backend.agent start
python -m backend.upload_server
```

in two separate terminals. Using the helper script just saves you from managing
multiple shells. If you prefer to run things manually, you still can.

### Frontend Setup (React)

The frontend lives in `frontend/` and is a small React app that connects to the
same LiveKit room as the agent.

1. **Install frontend dependencies**

```bash
cd frontend
npm install
```

2. **Generate a LiveKit access token**

The frontend needs a valid LiveKit JWT token. Generate one using:

```bash
cd /Users/sashank/Downloads/Projects/VoiceAgentRag
source .venv/bin/activate
python scripts/generate_token.py
```

This will print a JWT token. Copy it.

3. **Configure frontend environment**

Create `frontend/.env.local` with your LiveKit URL and the generated token:

```bash
cat > frontend/.env.local << 'EOF'
VITE_LIVEKIT_URL=wss://your-livekit-host.livekit.cloud
VITE_LIVEKIT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
EOF
```

4. **Start the dev server**

```bash
cd frontend
npm run dev
```

Open the printed localhost URL (usually `http://localhost:5173`) in your browser.

### RAG and Inventory Tooling

- **RAG**:
  - Implemented in `backend/rag/handbook_rag.py` using **LangChain**, an in‑process
    **Chroma** vector store, and **OpenAI embeddings**.
  - Helper `retrieve_handbook_context(query, k=3)` returns the most relevant
    chunks from the dealer handbook PDF.
  - `build_handbook_reference(query, k=3)` formats those chunks into a compact
    block injected into the LLM context.
- **Inventory tool**:
  - `backend/tools.py` defines a small in‑memory list of vehicles with
    `model`, `trim`, `body_type`, `price`, `color`, and `in_stock`.
  - `search_inventory(body_type, min_price, max_price)` filters this list and
    is exposed to the LLM as a tool for questions like “sedan between $18k and $28k”.

#### RAG design choices (brief)

- **Why Chroma (in‑process)**: for this V1, an embedded Chroma store keeps
  deployment simple: no extra services or containers, and the index builds
  lazily on first use. The trade‑off is that very large PDFs or many concurrent
  users would benefit from a dedicated vector DB and persistent indexes.
- **Chunking strategy**: the handbook is split into ~800‑character chunks with
  200‑character overlap. This keeps each chunk self‑contained (enough local
  context for a paragraph or two) while avoiding very large prompts; for a
  larger corpus you might tune this up or down based on retrieval quality.
- **Embeddings**: OpenAI embeddings are used for convenience and quality; they
  give good semantic search with minimal configuration. A local embedding model
  would avoid network calls but add infra/CPU complexity.
- **Soft grounding**: the retrieved chunks are injected as an additional
  `system`‑style message rather than hard‑constraining the model. This lets the
  agent answer naturally while being guided by the handbook, at the cost of
  occasional “extra” details from the model’s prior knowledge.

### Running Tests

There is a small integration‑style test suite under `backend/tests` (added later
in the implementation) that exercises the RAG retrieval and inventory search.
After activating the virtualenv:

```bash
pytest backend/tests
```

### Troubleshooting

**Backend errors:**

1. **`401 Unauthorized` from OpenAI**: Your `OPENAI_API_KEY` in `.env` is invalid or expired. Get a new key from https://platform.openai.com/api-keys

2. **`ModuleNotFoundError`**: Make sure you've activated the virtualenv (`source .venv/bin/activate`) and installed dependencies (`pip install -r backend/requirements.txt`)

3. **`FileNotFoundError` for PDF**: Run `python backend/resources/make_dealer_handbook.py` to generate the handbook PDF

4. **`publish_data() got unexpected keyword argument 'data'`**: Fixed in latest code - the first positional argument is the data bytes

5. **`object list can't be used in 'await' expression`**: Fixed - `inventory_search_tool` is now async

**Frontend errors:**

1. **"VITE_LIVEKIT_URL and VITE_LIVEKIT_TOKEN must be set"**: Create `frontend/.env.local` with your LiveKit URL and a valid token (generate with `python scripts/generate_token.py`)

2. **Token expired**: LiveKit tokens expire after 6 hours by default. Regenerate with `python scripts/generate_token.py`

3. **No transcript showing**: Check backend logs for `publish_data` errors. Make sure the backend is running and connected

**Logs:**

The backend now includes extensive emoji-based logging:
- 🚀 Initialization
- 📖 PDF loading
- 🎤 User speech
- 🤖 Agent responses
- 🔍 Tool calls
- 📚 RAG invocations
- 📤 Transcript publishing

Note: tests that touch the RAG pipeline require `OPENAI_API_KEY` to be set.


