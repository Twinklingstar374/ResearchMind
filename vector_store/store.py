"""
VectorStore — Per-session ChromaDB vector store with semantic search,
reset, and stats capabilities.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
_chroma_client = chromadb.Client()


class VectorStore:
    """
    Per-session ChromaDB collection for embedding and retrieving source chunks.
    Each instance gets its own unique collection name.
    """

    def __init__(self, session_id: str = None):
        if session_id:
            self.collection_name = f"session_{session_id[:8]}"
        else:
            self.collection_name = f"session_{uuid4().hex[:8]}"
        self._collection = None
        self._doc_count = 0
        self._ensure_collection()

    def _ensure_collection(self):
        """Get or create the session collection."""
        self._collection = _chroma_client.get_or_create_collection(
            name=self.collection_name
        )

    def embed_sources(self, sources: list[dict]) -> int:
        """
        Embed and store a list of source dicts.

        Args:
            sources: List of source dicts with title, url, content fields.

        Returns:
            Number of chunks stored.
        """
        if not sources:
            return 0

        texts, ids, metadatas = [], [], []

        for i, source in enumerate(sources):
            content = source.get("content", "").strip()
            if not content:
                continue

            # Split into ~500-char chunks
            chunks = _split_into_chunks(content, chunk_size=500, overlap=50)
            for j, chunk in enumerate(chunks):
                chunk_id = f"{self.collection_name}_{i}_{j}"
                texts.append(chunk)
                ids.append(chunk_id)
                metadatas.append({
                    "source": source.get("url", ""),
                    "title": source.get("title", "Untitled"),
                    "credibility_score": str(source.get("credibility_score", 0)),
                })

        if not texts:
            return 0

        embeddings = _embedding_model.encode(texts).tolist()

        self._collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

        self._doc_count += len(texts)
        return len(texts)

    def semantic_search(self, query: str, k: int = 3) -> list[dict]:
        """
        Retrieve k most semantically relevant chunks for a query.

        Args:
            query: The search query string
            k: Number of results to return

        Returns:
            List of dicts with text, source, title, credibility_score
        """
        try:
            count = self._collection.count()
            if count == 0:
                return []

            k = min(k, count)
            query_embedding = _embedding_model.encode([query]).tolist()

            results = self._collection.query(
                query_embeddings=query_embedding,
                n_results=k
            )

            chunks = []
            for i in range(len(results["documents"][0])):
                meta = results["metadatas"][0][i]
                chunks.append({
                    "text": results["documents"][0][i],
                    "source": meta.get("source", ""),
                    "title": meta.get("title", ""),
                    "credibility_score": float(meta.get("credibility_score", 0)),
                })
            return chunks

        except Exception as e:
            print(f"[VectorStore] semantic_search error: {e}")
            return []

    def reset(self) -> None:
        """Delete the current collection and create a fresh one."""
        try:
            _chroma_client.delete_collection(name=self.collection_name)
        except Exception:
            pass
        self._doc_count = 0
        self._collection = _chroma_client.get_or_create_collection(
            name=self.collection_name
        )

    def get_stats(self) -> dict:
        """Return stats about the current collection."""
        try:
            count = self._collection.count()
        except Exception:
            count = 0
        return {
            "collection_name": self.collection_name,
            "embedded_chunks": count,
        }


def _split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Simple character-based chunker with overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
        if start >= len(text):
            break
    return chunks
