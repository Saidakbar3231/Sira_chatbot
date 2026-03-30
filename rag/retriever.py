import asyncio
from rag.embeddings import _get_collection


async def retrieve(query: str, top_k: int = 3) -> str:
    """Return top_k relevant chunks as a single context string."""
    def _sync():
        collection = _get_collection()
        if collection.count() == 0:
            return ""
        results = collection.query(query_texts=[query], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        return "\n\n".join(docs)

    return await asyncio.to_thread(_sync)
