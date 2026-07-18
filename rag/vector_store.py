"""
Vector Store — ChromaDB + IBM Granite Embeddings
Ingests farming knowledge base and provides semantic retrieval.
"""
import logging
import chromadb
from chromadb.config import Settings
from data.knowledge_base import DOCUMENT_IDS, DOCUMENT_TEXTS, DOCUMENT_METADATAS
import config

logger = logging.getLogger(__name__)


class FarmingVectorStore:
    """ChromaDB vector store backed by IBM Granite slate embeddings."""

    def __init__(self, granite_client=None):
        # Allow injecting a mock client for tests; lazy-import real one otherwise
        self._granite_client = granite_client
        self._client = chromadb.PersistentClient(
            path=config.CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("ChromaDB collection '%s' loaded (%d docs)",
                    config.COLLECTION_NAME, self._collection.count())

    def _client_lazy(self):
        if self._granite_client is None:
            from rag.granite_client import granite_client
            self._granite_client = granite_client
        return self._granite_client

    def ingest(self, force: bool = False) -> int:
        """
        Load FARMING_DOCUMENTS into the vector store.
        Skips ingestion if documents already exist unless force=True.
        Returns number of documents ingested.
        """
        existing = self._collection.count()
        if existing >= len(DOCUMENT_IDS) and not force:
            logger.info("Knowledge base already ingested (%d docs). Skipping.", existing)
            return 0

        logger.info("Ingesting %d farming documents…", len(DOCUMENT_IDS))
        client = self._client_lazy()
        embeddings = client.embed(DOCUMENT_TEXTS)

        # Upsert in batches of 50
        batch_size = 50
        for i in range(0, len(DOCUMENT_IDS), batch_size):
            self._collection.upsert(
                ids=DOCUMENT_IDS[i:i + batch_size],
                embeddings=embeddings[i:i + batch_size],
                documents=DOCUMENT_TEXTS[i:i + batch_size],
                metadatas=DOCUMENT_METADATAS[i:i + batch_size],
            )
        logger.info("Ingestion complete.")
        return len(DOCUMENT_IDS)

    def retrieve(self, query: str, top_k: int = config.RETRIEVAL_TOP_K,
                 language: str = "en") -> list[dict]:
        """
        Retrieve top-k relevant documents for a query.
        Optionally filter by language metadata.
        Returns list of {text, metadata, distance}.
        """
        client = self._client_lazy()
        query_embedding = client.embed_query(query)

        where_filter = None
        if language and language != "en":
            # try language-specific first; fall back to English if empty
            where_filter = {"language": language}

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        docs = []
        if results and results["documents"]:
            for text, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                docs.append({"text": text, "metadata": meta, "distance": dist})

        # If no language-specific docs found, fall back to English
        if not docs and where_filter:
            return self.retrieve(query, top_k=top_k, language="en")

        return docs

    def add_document(self, doc_id: str, text: str, metadata: dict) -> None:
        """Add a single new document to the store (for dynamic updates)."""
        client = self._client_lazy()
        embedding = client.embed_query(text)
        self._collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
        )
        logger.info("Document '%s' added to vector store.", doc_id)


# module-level singleton
vector_store = FarmingVectorStore()
