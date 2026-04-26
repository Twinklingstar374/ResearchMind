"""
Query Decomposer — Breaks a user query into 3 focused sub-questions
using Groq LLM for multi-angle research coverage.
"""

import json
import re
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()


DECOMPOSE_PROMPT = """You are a research query decomposer. Given a user's research query, break it down into exactly 3 focused sub-questions that together cover the topic comprehensively from different angles.

Rules:
- Return ONLY a JSON array of 3 strings
- Each sub-question should explore a different angle (e.g., current state, impact, future trends)
- Sub-questions should be specific and searchable
- Do NOT include any explanation, markdown, or extra text

Example input: "Impact of AI on healthcare"
Example output: ["What are the current applications of AI in medical diagnosis and treatment?", "How is AI improving healthcare efficiency and reducing costs?", "What are the ethical concerns and regulatory challenges of AI in healthcare?"]

User query: {query}"""


def decompose_query(query: str) -> list[str]:
    """
    Breaks a research query into 3 focused sub-questions.
    
    Args:
        query: The user's research query
        
    Returns:
        List of 3 sub-question strings
    """
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
                    temperature=0.3,
                    max_tokens=1024
                )
        
                response = llm.invoke([
                    {"role": "system", "content": "You are a precise JSON-only responder. Return only valid JSON arrays."},
                    {"role": "user", "content": DECOMPOSE_PROMPT.format(query=query)}
                ])
                break
            except Exception as e:
                last_e = e
                continue
                
        if response is None:
            raise last_e

        raw = response.content.strip()
        
        # Try direct JSON parse
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list) and len(parsed) >= 3:
                return [str(q) for q in parsed[:3]]
        except json.JSONDecodeError:
            pass

        # Fallback: extract JSON array from response using regex
        json_match = re.search(r'\[.*?\]', raw, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, list) and len(parsed) >= 3:
                    return [str(q) for q in parsed[:3]]
            except json.JSONDecodeError:
                pass

        # Final fallback: generate simple sub-questions
        return _fallback_decompose(query)

    except Exception as e:
        if "413" in str(e) or "rate_limit" in str(e) or "too large" in str(e).lower():
            return ["The research context is too large. Please try a shorter or more specific topic."]
        print(f"[Decomposer] Error during decomposition: {e}")
        return _fallback_decompose(query)


def _fallback_decompose(query: str) -> list[str]:
    """
    Generates 3 generic sub-questions when LLM parsing fails.
    """
    return [
        f"What is the current state of {query}?",
        f"What are the key challenges and opportunities in {query}?",
        f"What are the future trends and predictions for {query}?"
    ]
