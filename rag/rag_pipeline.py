"""
RAG Pipeline — Retrieval-Augmented Generation for Smart Farming
Combines ChromaDB retrieval + IBM Granite generation with farming-specific prompts.
"""
import logging
from typing import Optional
from rag.vector_store import vector_store
from rag.granite_client import granite_client

logger = logging.getLogger(__name__)

# ── Prompts ───────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are KrishiMitra (Farm Friend), an expert AI farming advisor.
You help small-scale Indian farmers with crop selection, soil health, pest control,
weather-based decisions, and market prices. Respond in a simple, friendly tone.
Always give practical, actionable advice suitable for resource-constrained farmers.
If the farmer writes in a regional language, respond in the same language."""

USER_TEMPLATE = """### Relevant Agricultural Knowledge:
{context}

### Farmer's Question:
{question}

Answer the farmer's question using the knowledge above. Be concise and practical."""


class RAGPipeline:
    """Orchestrates retrieval + IBM watsonx.ai LLM generation for farming queries."""

    def __init__(self):
        self._vector_store = vector_store
        self._llm = granite_client

    def answer(
        self,
        question: str,
        language: str = "en",
        extra_context: Optional[str] = None,
    ) -> dict:
        """
        Full RAG answer pipeline:
        1. Retrieve relevant farming knowledge from ChromaDB
        2. Build system + user messages
        3. Generate answer via IBM watsonx.ai chat API
        Returns dict with answer, sources, and retrieved_docs.
        """
        # Step 1 — Retrieve
        retrieved_docs = self._vector_store.retrieve(question, language=language)
        context_parts = [doc["text"] for doc in retrieved_docs]

        if extra_context:
            context_parts.insert(0, extra_context)

        context = "\n\n---\n\n".join(context_parts) if context_parts else \
            "No specific knowledge found; use general agricultural expertise."

        # Step 2 — Build messages
        user_message = USER_TEMPLATE.format(context=context, question=question)

        # Step 3 — Generate via chat API
        answer_text = self._llm.chat(system=SYSTEM_PROMPT, user=user_message)

        sources = [
            {
                "id":       doc["metadata"].get("id", ""),
                "category": doc["metadata"].get("category", ""),
                "score":    round(1 - doc["distance"], 3),
            }
            for doc in retrieved_docs
        ]

        return {
            "answer":        answer_text,
            "sources":       sources,
            "retrieved_docs": retrieved_docs,
            "language":      language,
        }


# module-level singleton
rag_pipeline = RAGPipeline()
