"""
Ingest farming knowledge into ChromaDB.
Run this script once before starting the server.
"""
import logging
import sys
import os
# Ensure project root is on the path when running as scripts/ingest.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting knowledge base ingestion…")
    try:
        from rag.vector_store import FarmingVectorStore
        from rag.granite_client import granite_client

        store = FarmingVectorStore(granite_client=granite_client)
        count = store.ingest(force="--force" in sys.argv)
        if count:
            logger.info("✅ Ingested %d documents into ChromaDB.", count)
        else:
            logger.info("ℹ️  Documents already in store. Use --force to re-ingest.")
    except Exception as exc:
        logger.error("Ingestion failed: %s", exc)
        logger.error("Make sure WATSONX_API_KEY and WATSONX_PROJECT_ID are set in .env")
        sys.exit(1)


if __name__ == "__main__":
    main()
