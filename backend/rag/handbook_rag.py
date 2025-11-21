"""
Minimal RAG layer over the Skyline Motors dealer handbook PDF.

This module is intentionally simple: on first use it loads the PDF,
chunks it into overlapping sections, builds an in-process vector store,
and exposes a retrieval helper used by the voice agent.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from backend.config import AppConfig, load_config


@dataclass
class HandbookRAG:
    """Small wrapper around a LangChain vector store for the dealer handbook."""

    config: AppConfig
    _vector_store: Chroma

    @classmethod
    def from_config(cls, config: AppConfig) -> "HandbookRAG":
        import logging
        logger = logging.getLogger(__name__)
        
        pdf_path = str(config.rag.dealer_handbook_path)
        logger.info(f"📖 Loading dealer handbook from: {pdf_path}")
        
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        logger.info(f"✅ Loaded {len(documents)} pages from PDF")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=200,
        )
        split_docs = splitter.split_documents(documents)
        logger.info(f"✅ Split into {len(split_docs)} chunks")

        embeddings = OpenAIEmbeddings(openai_api_key=config.openai.api_key)
        logger.info("🔄 Building vector store (this may take a moment)...")

        # Using an in-memory Chroma instance keeps things very simple for a V1.
        vector_store = Chroma.from_documents(split_docs, embedding=embeddings)
        logger.info("✅ Vector store ready!")

        return cls(config=config, _vector_store=vector_store)

    def retrieve(self, query: str, k: int | None = None) -> List[str]:
        """Return the top-k chunk texts for a given query."""
        import logging
        logger = logging.getLogger(__name__)
        
        top_k = k or self.config.rag.top_k_chunks
        logger.debug(f"🔍 RAG query: {query[:100]}... (top_k={top_k})")
        results = self._vector_store.similarity_search(query, k=top_k)
        logger.debug(f"✅ Found {len(results)} chunks")
        return [doc.page_content for doc in results]


@lru_cache(maxsize=1)
def _get_rag() -> HandbookRAG:
    """
    Lazily construct a singleton HandbookRAG instance.

    The vector store can be relatively heavy to build, so we avoid doing
    this work more than once per process.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("🚀 Initializing RAG system (first call only)...")
    
    config = load_config()
    rag = HandbookRAG.from_config(config)
    logger.info("✅ RAG system initialized and cached")
    return rag


def retrieve_handbook_context(query: str, k: int | None = None) -> List[str]:
    """Public helper used by the agent to fetch relevant handbook snippets."""
    rag = _get_rag()
    return rag.retrieve(query, k=k)


def build_handbook_reference(query: str, k: int | None = None) -> str:
    """
    Format retrieved chunks into a compact reference block for the LLM.

    The agent injects this block as an additional system/context message
    before calling the language model.
    """
    chunks = retrieve_handbook_context(query, k=k)
    if not chunks:
        return "Handbook reference: no relevant sections found."

    header = "Handbook reference (Skyline Motors dealer handbook):"
    bullet_lines = []
    for i, chunk in enumerate(chunks, start=1):
        # Keep each chunk reasonably short for the prompt; trimming here is
        # a pragmatic safeguard and not a strict requirement.
        short = chunk.strip().replace("\n", " ")
        if len(short) > 600:
            short = short[:600] + "..."
        bullet_lines.append(f"{i}. {short}")

    return header + "\n" + "\n".join(bullet_lines)



