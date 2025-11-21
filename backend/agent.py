"""
Entry point for the Skyline Motors LiveKit voice concierge agent.

This uses LiveKit Agents with OpenAI for:
- real-time speech recognition
- LLM-based dialogue and reasoning
- text-to-speech voice responses

The agent also:
- consults a RAG layer over the dealer handbook PDF for factual questions
- exposes a single inventory-search tool for price-range vehicle lookup
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List

from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, voice
from livekit.agents.llm import ChatContext, ChatMessage, function_tool
from livekit.plugins import openai as lk_openai

from backend.config import load_config
from backend.rag import build_handbook_reference
from backend.tools import search_inventory


SKYLINE_SYSTEM_PROMPT = """
You are the AI concierge for Skyline Motors, a modern car dealership.
You are the first point of contact for customers arriving on the website or voice line.

Goals:
- Understand what the customer wants.
- Answer questions about vehicles, trims, prices, warranties, financing, and service.
- Guide them toward useful actions such as comparing models, estimating payments,
  or booking a test drive or service visit.

Tone and style:
- Be warm, polite, and professional.
- Use natural spoken language that would sound good as audio.
- Prefer concise answers by default and expand when the customer asks for detail.
- Avoid sounding like a scripted robot.

Knowledge source:
- You have access to an internal Skyline Motors dealer handbook implemented as a RAG
  pipeline over a PDF. Whenever the user asks for a specific fact, specification,
  warranty rule, or financing policy, you silently consult this handbook before
  answering. Prefer to base answers on the handbook and avoid guessing.

Tools:
- You can call a single internal tool: `search_inventory`, which returns available
  vehicles that match a body type and budget range. When the user asks for help
  finding a car in a given price range (for example a sedan between two prices),
  you SHOULD call this tool and then explain the results in plain language.

Behavior and guardrails:
- Do not invent precise prices or promotions beyond what the handbook or tools
  provide. Use ranges and clearly mark them as estimates.
- If the handbook or tools do not contain an answer, say you are not sure and
  suggest speaking to a human representative.
- Ask short clarifying questions when user intent is ambiguous, especially about
  budget, body type, or timing.
- Keep the conversation focused on helping the user progress in their car search,
  but you can handle brief small talk.
""".strip()


def _looks_like_factual_question(text: str) -> bool:
    """Very small heuristic to decide when to invoke RAG."""
    keywords = [
        "warranty",
        "maintenance",
        "service interval",
        "oil change",
        "finance",
        "financing",
        "lease",
        "leasing",
        "apr",
        "interest rate",
        "down payment",
        "trim",
        "horsepower",
        "torque",
        "cargo",
        "mpg",
        "range",
    ]
    lowered = text.lower()
    return any(k in lowered for k in keywords)


@function_tool
async def inventory_search_tool(
    body_type: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
) -> List[Dict[str, Any]]:
    """
    Search Skyline Motors inventory for matching vehicles.

    Parameters:
    - body_type: optional body style such as "sedan", "suv", or "hatchback".
    - min_price: optional minimum price in USD.
    - max_price: optional maximum price in USD.

    Returns:
    - A short list of matching vehicles with fields:
      model, trim, body_type, price, color, in_stock.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 Inventory search: body_type={body_type}, min_price={min_price}, max_price={max_price}")
    
    results = search_inventory(
        body_type=body_type,
        min_price=min_price,
        max_price=max_price,
    )
    
    logger.info(f"✅ Found {len(results)} matching vehicles")
    return results


class SkylineVoiceAgent(voice.Agent):
    """
    Voice agent that injects handbook RAG context before LLM calls.

    We override `on_user_turn_completed` to look at the user's final text,
    and when it appears factual we add a short handbook reference block
    into the chat context just before the LLM is invoked.
    """

    def __init__(self) -> None:
        super().__init__(instructions=SKYLINE_SYSTEM_PROMPT)

    async def on_user_turn_completed(
        self,
        turn_ctx: ChatContext,
        new_message: ChatMessage,
    ) -> None:
        import logging
        logger = logging.getLogger(__name__)
        
        text = new_message.text_content or ""
        if not text or not _looks_like_factual_question(text):
            logger.debug(f"❌ Not a factual question, skipping RAG for: {text[:50] if text else '(empty)'}...")
            return

        logger.info(f"📚 Factual question detected, invoking RAG for: {text[:80]}...")
        handbook_ref = build_handbook_reference(text)
        logger.info(f"✅ Retrieved {len(handbook_ref)} chars of handbook context")
        # Insert as a system-style message so the LLM can cite it silently.
        turn_ctx.add_message(role="system", content=handbook_ref)


async def entrypoint(ctx: JobContext) -> None:
    """
    LiveKit Agents entrypoint.

    This function is called by the worker process whenever a new room
    assignment is created in LiveKit Cloud.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Skyline Motors agent starting...")
    config = load_config()
    logger.info(f"📡 Connecting to room: {ctx.room.name}")

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info("✅ Connected to LiveKit room")

    logger.info(f"🎙️ Initializing STT: {config.openai.stt_model}")
    stt = lk_openai.STT(model=config.openai.stt_model, api_key=config.openai.api_key)
    
    logger.info(f"🔊 Initializing TTS: {config.openai.tts_model}")
    tts = lk_openai.TTS(model=config.openai.tts_model, api_key=config.openai.api_key)
    
    logger.info(f"🧠 Initializing LLM: {config.openai.fast_model}")
    llm = lk_openai.LLM(model=config.openai.fast_model, api_key=config.openai.api_key)

    # Use Silero VAD for voice activity detection (required for non-streaming STT)
    from livekit.plugins import silero
    logger.info("🎯 Loading Silero VAD...")
    vad = silero.VAD.load()
    
    logger.info("🔧 Creating agent session...")
    session = voice.AgentSession(
        stt=stt,
        vad=vad,
        llm=llm,
        tts=tts,
        tools=[inventory_search_tool],
        allow_interruptions=True,
    )

    agent = SkylineVoiceAgent()
    logger.info("✅ Agent initialized, starting session...")

    async def _publish_transcript(payload: Dict[str, str]) -> None:
        import logging
        logger = logging.getLogger(__name__)
        try:
            # Correct API: first positional arg is the data bytes
            await ctx.room.local_participant.publish_data(
                json.dumps(payload).encode("utf-8"),
                reliable=True,
            )
            logger.debug(f"📤 Published transcript: {payload}")
        except Exception as e:
            logger.error(f"❌ Failed to publish transcript: {e}")

    # Forward user and agent text to the room as simple JSON events so the
    # React client can build a live transcript.
    import logging
    logger = logging.getLogger(__name__)
    
    @session.on("user_input_transcribed")
    def _on_user_input(event: voice.UserInputTranscribedEvent) -> None:
        if not event.is_final:
            return

        logger.info(f"🎤 User said: {event.transcript}")
        asyncio.create_task(
            _publish_transcript(
                {
                    "speaker": "user",
                    "text": event.transcript,
                }
            )
        )

    @session.on("conversation_item_added")
    def _on_conversation_item(event: voice.ConversationItemAddedEvent) -> None:
        item = event.item
        if not isinstance(item, ChatMessage):
            return

        if item.role != "assistant":
            return

        text = item.text_content or ""
        if not text.strip():
            return

        logger.info(f"🤖 Agent said: {text}")
        asyncio.create_task(
            _publish_transcript(
                {
                    "speaker": "agent",
                    "text": text,
                }
            )
        )

    await session.start(agent, room=ctx.room)
    logger.info("🎉 Session started! Agent is now live and listening...")


def main() -> None:
    """CLI entry point for manual runs: `python -m backend.agent`."""
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))


if __name__ == "__main__":
    main()
