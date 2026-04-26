from utils.search import search_web
from utils.chunker import chunk_text
from utils.embeddings import embed_and_store, retrieve_context
from agent.prompts import RESEARCH_SYSTEM_PROMPT, RESEARCH_USER_PROMPT

from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()


def run_research(query: str):

    # 1️⃣ Search the web
    documents = search_web(query)

    if not documents:
        return "No search results found."

    # 2️⃣ Chunk the articles
    chunks = chunk_text(documents)

    if not chunks:
        return "No valid content found in articles."

    # 3️⃣ Store embeddings in ChromaDB
    embed_and_store(chunks)

    # 4️⃣ Retrieve relevant context
    context_chunks = retrieve_context(query)

    if not context_chunks:
        return "No relevant context retrieved."

    context = "\n\n".join(
        [f"{c['text']}\nSource: {c['source']}" for c in context_chunks]
    )

    # 5️⃣ Prepare prompt
    user_prompt = RESEARCH_USER_PROMPT.format(
        query=query,
        context=context
    )

    # 6️⃣ Call the LLM
    try:
        models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile", 
            "gemma2-9b-it"
        ]
        
        response = None
        last_e = None
        
        for model_name in models_to_try:
            try:
                llm = ChatGroq(
                    model=model_name,
                    temperature=0.2,
                    max_tokens=1024
                )
        
                response = llm.invoke([
                    {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ])
                break
            except Exception as e:
                last_e = e
                continue
                
        if response is None:
            raise last_e

        return response.content
    except Exception as e:
        if "413" in str(e) or "rate_limit" in str(e) or "too large" in str(e).lower():
            return "The research context is too large. Please try a shorter or more specific topic."
        return f"Error: {e}"