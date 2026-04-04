import os
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.Client()

def get_or_create_collection(collection_name: str = "research"):
    return chroma_client.get_or_create_collection(name=collection_name)

def embed_and_store(chunks: list[dict], collection_name: str = "research"):
    collection = get_or_create_collection(collection_name)
    
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts).tolist()
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": chunk["source"], "title": chunk["title"]} for chunk in chunks]
    
    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )
    
    print(f"Stored {len(chunks)} chunks in ChromaDB")
    return collection

def retrieve_context(query: str, collection_name: str = "research", n_results: int = 5) -> list[dict]:
    collection = get_or_create_collection(collection_name)
    query_embedding = model.encode([query]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    
    context = []
    for i in range(len(results["documents"][0])):
        context.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "title": results["metadatas"][0][i]["title"],
        })
    
    return context


if __name__ == "__main__":
    from chunker import chunk_text
    
    sample_docs = [{
        "title": "AI in 2025",
        "url": "https://example.com/ai",
        "content": "Artificial intelligence is revolutionizing industries. " * 30
    }]
    
    chunks = chunk_text(sample_docs)
    embed_and_store(chunks)
    
    results = retrieve_context("how is AI changing industries?")
    print(f"\nRetrieved {len(results)} relevant chunks")
    print(f"\nTop result preview:")
    print(results[0]["text"][:200])
    print(f"Source: {results[0]['source']}")