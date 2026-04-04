import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def search_web(query: str, max_results: int = 5) -> list[dict]:
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_raw_content=True
    )
    
    results = []
    for r in response["results"]:
        results.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("raw_content") or r.get("content", ""),
        })
    
    return results


if __name__ == "__main__":
    results = search_web("AI agents in 2025")
    for i, r in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Title: {r['title']}")
        print(f"URL:   {r['url']}")
        print(f"Content preview: {r['content'][:200]}...")