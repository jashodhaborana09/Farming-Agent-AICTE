"""
IBM watsonx.ai Client — LLM (chat API) + Embeddings
Region: eu-gb  |  LLM: meta-llama/llama-3-3-70b-instruct
                   Embed: ibm/granite-embedding-278m-multilingual
"""
import logging
from typing import Optional
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference, Embeddings
import config

logger = logging.getLogger(__name__)


class GraniteClient:
    """
    Wraps the IBM watsonx.ai LLM and embedding models.
    Uses the chat() API for fast inference (~2-4s vs 100s+ for generate_text).
    """

    def __init__(self):
        self._credentials = Credentials(
            url=config.WATSONX_URL,
            api_key=config.WATSONX_API_KEY,
        )
        self._project_id = config.WATSONX_PROJECT_ID
        self._llm: Optional[ModelInference] = None
        self._embedder: Optional[Embeddings] = None

    def _get_llm(self) -> ModelInference:
        if self._llm is None:
            self._llm = ModelInference(
                model_id=config.GRANITE_LLM_MODEL,
                credentials=self._credentials,
                project_id=self._project_id,
            )
            logger.info("LLM initialised: %s", config.GRANITE_LLM_MODEL)
        return self._llm

    def _get_embedder(self) -> Embeddings:
        if self._embedder is None:
            self._embedder = Embeddings(
                model_id=config.GRANITE_EMBED_MODEL,
                credentials=self._credentials,
                project_id=self._project_id,
            )
            logger.info("Embeddings initialised: %s", config.GRANITE_EMBED_MODEL)
        return self._embedder

    def chat(self, system: str, user: str) -> str:
        """
        Call the LLM via the chat API.
        Returns the assistant's reply as a plain string.
        """
        llm = self._get_llm()
        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ]
        params = {
            "max_tokens":          config.GRANITE_PARAMS["max_new_tokens"],
            "temperature":         config.GRANITE_PARAMS["temperature"],
            "repetition_penalty":  config.GRANITE_PARAMS["repetition_penalty"],
        }
        resp = llm.chat(messages=messages, params=params)
        return resp["choices"][0]["message"]["content"].strip()

    # kept for backwards-compat; delegates to chat()
    def generate(self, prompt: str) -> str:
        """Legacy generate interface — wraps chat() with a single user turn."""
        return self.chat(system="You are a helpful farming advisor.", user=prompt)

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for a list of texts."""
        embedder = self._get_embedder()
        return embedder.embed_documents(texts=texts)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string."""
        return self.embed([text])[0]


# module-level singleton
granite_client = GraniteClient()
