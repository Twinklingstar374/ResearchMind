"""
Upgraded utils/search.py — Keeps original search_web() and adds
multi_search() for parallel multi-angle research.
"""

import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Original single-query web search via Tavily.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of dicts with title, url, content fields
    """
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_raw_content=True
        )

        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("raw_content") or r.get("content", ""),
                "published_date": r.get("published_date", ""),
                "score": r.get("score", 0.5),
            })

        return results

    except Exception as e:
        print(f"[Search] search_web error for '{query}': {e}")
        return []


def multi_search(sub_questions: list[str], max_results: int = 4) -> dict:
    """
    Search multiple sub-questions and return results grouped by research angle.

    Args:
        sub_questions: List of 3 sub-question strings from the decomposer
        max_results: Number of results per sub-question (default 4)

    Returns:
        Dict with keys angle_1, angle_2, angle_3. Each value is:
        {
            "sub_question": str,
            "sources": [
                {
                    "title": str,
                    "url": str,
                    "content": str,
                    "published_date": str,
                    "score": float
                },
                ...
            ]
        }
    """
    result = {}

    for i, question in enumerate(sub_questions, 1):
        angle_key = f"angle_{i}"
        sources = search_web(question, max_results=max_results)
        result[angle_key] = {
            "sub_question": question,
            "sources": sources
        }

    return result


if __name__ == "__main__":
    # Test multi_search
    questions = [
        "What are the current applications of AI agents?",
        "What are the challenges of deploying AI agents?",
        "What is the future of autonomous AI systems?"
    ]
    results = multi_search(questions)
    for angle, data in results.items():
        print(f"\n{angle}: {data['sub_question']}")
        print(f"  Found {len(data['sources'])} sources")