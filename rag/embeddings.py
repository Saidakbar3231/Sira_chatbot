import asyncio
import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

from config import settings

COLLECTION_NAME = "sira_docs"

_embedding_fn = ONNXMiniLM_L6_V2()
_chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)


def _get_collection():
    return _chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embedding_fn,
    )


async def index_documents(docs: list[dict]) -> int:
    """Embed and store documents in ChromaDB. Returns count of indexed chunks."""
    if not docs:
        return 0

    def _sync():
        collection = _get_collection()
        ids = [f"{d['source']}_{i}" for i, d in enumerate(docs)]
        texts = [d["text"] for d in docs]
        metadatas = [{"source": d["source"]} for d in docs]
        collection.upsert(ids=ids, documents=texts, metadatas=metadatas)
        return len(docs)

    return await asyncio.to_thread(_sync)


async def get_collection_count() -> int:
    def _sync():
        return _get_collection().count()
    return await asyncio.to_thread(_sync)
