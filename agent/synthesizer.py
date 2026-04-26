"""
Synthesizer — Generates structured research reports from scored sources,
chat history, and the original query using Groq LLM.
"""

import re
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

SYNTHESIS_SYSTEM_PROMPT = """You are a senior research analyst. Write with precision. Cite sources inline. Acknowledge uncertainty. Never hallucinate.

Your task is to produce a structured research report using ONLY the information provided in the sources. If information is absent, say so honestly. Never invent facts, statistics, or citations.

Your report MUST contain these exact sections with these exact markdown headers:

## Executive Summary
2-3 sentences giving a crisp overview of the key answer.

## Key Findings
- Finding 1 (cite source inline as [Source Title])
- Finding 2 (cite source inline)
- Finding 3 (cite source inline)
- Finding 4 (cite source inline)
- Finding 5 (cite source inline)

## Deep Analysis
2-3 paragraphs of detailed analysis. Cite sources inline. Discuss nuance and context.

## Conflicting Viewpoints
Note where sources disagree or present different perspectives. If sources are consistent, write: "Sources are broadly consistent on this topic."

## Knowledge Gaps
What important aspects remain unclear, understudied, or absent from the available sources?

## Sources Used
For each source: **[Title]** — URL — Credibility: X/100
"""

FOLLOWUP_SYSTEM_PROMPT = """You are a senior research analyst continuing a conversation. Use the provided context chunks and conversation history to give a focused, precise answer.

Rules:
- Answer ONLY from the provided context
- Cite sources inline where possible
- Acknowledge if context is insufficient
- Be concise — this is a follow-up, not a new report
- If the question goes beyond the research context, say so clearly
"""


def _format_sources_for_prompt(sources: list[dict]) -> str:
    """Format scored sources into a clear prompt string."""
    formatted = []
    for i, source in enumerate(sources, 1):
        title = source.get("title", f"Source {i}")
        url = source.get("url", "")
        content = source.get("content", "")[:1500]  # cap content per source
        credibility = source.get("credibility_score", 0)
        date = source.get("published_date", "Unknown date")

        formatted.append(
            f"[SOURCE {i}]\n"
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Credibility Score: {credibility}/100\n"
            f"Published: {date}\n"
            f"Content:\n{content}\n"
        )
    return "\n---\n".join(formatted)


def _format_history_for_prompt(history: list[dict]) -> str:
    """Format chat history into a prompt string."""
    if not history:
        return "No prior conversation."
    lines = []
    messages = history[-6:]  # Only last 3 exchanges
    for msg in messages:
        role = msg.get("role", "user").capitalize()
        lines.append(f"{role}: {msg.get('content', '')}")
    return "\n".join(lines)


def synthesize_report(
    query: str,
    sources: list[dict],
    sub_questions: list[str],
    chat_history: list[dict] = None
) -> dict:
    """
    Generate a structured research report.

    Args:
        query: The original user query
        sources: Top scored source dicts (with credibility_score etc.)
        sub_questions: The 3 sub-questions used for research
        chat_history: Optional list of prior conversation messages

    Returns:
        dict with keys: report (markdown str), sections (parsed dict)
    """
    if chat_history is None:
        chat_history = []

    sources_text = _format_sources_for_prompt(sources)
    research_text = sources_text[:2500]
    history_text = _format_history_for_prompt(chat_history)
    sub_q_text = "\n".join(f"  {i+1}. {q}" for i, q in enumerate(sub_questions))

    user_prompt = f"""Research Query: {query}

Sub-questions researched:
{sub_q_text}

Conversation history:
{history_text}

Sources retrieved:
{research_text}

Generate a comprehensive, structured research report following the exact format specified."""

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
                    {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ])
                break
            except Exception as e:
                last_e = e
                continue
                
        if response is None:
            raise last_e

        report_md = response.content.strip()

        # Build structured dict from parsed sections
        sections = _parse_sections(report_md)

        # Append a clean sources section
        source_lines = []
        for s in sources:
            source_lines.append(
                f"**{s.get('title', 'Untitled')}** — {s.get('url', '')} — "
                f"Credibility: {s.get('credibility_score', 0)}/100"
            )
        sections["sources_list"] = sources

        return {
            "report": report_md,
            "sections": sections
        }

    except Exception as e:
        if "413" in str(e) or "rate_limit" in str(e) or "too large" in str(e).lower():
            err_msg = "The research context is too large. Please try a shorter or more specific topic."
            return {
                "report": err_msg,
                "sections": {"error": err_msg, "sources_list": sources}
            }
        fallback_md = (
            f"## Research Report: {query}\n\n"
            f"An error occurred during report generation: {str(e)}\n\n"
            f"**Sources found:**\n"
            + "\n".join(f"- [{s.get('title','')}]({s.get('url','')})" for s in sources)
        )
        return {
            "report": fallback_md,
            "sections": {"error": str(e), "sources_list": sources}
        }


def synthesize_followup(
    question: str,
    context_chunks: list[dict],
    chat_history: list[dict]
) -> dict:
    """
    Generate a focused answer to a follow-up question using existing context.

    Args:
        question: The follow-up question
        context_chunks: Relevant chunks from the vector store
        chat_history: Prior conversation history

    Returns:
        dict with keys: report (markdown str), sections (dict)
    """
    context_text = "\n\n---\n\n".join(
        f"Source: {c.get('source', '')}\n{c.get('text', '')}"
        for c in context_chunks
    )
    research_text = context_text[:2500]
    history_text = _format_history_for_prompt(chat_history)

    user_prompt = f"""Follow-up question: {question}

Conversation history:
{history_text}

Relevant context from previous research:
{research_text}

Please answer the follow-up question based strictly on the above context."""

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
                    {"role": "system", "content": FOLLOWUP_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ])
                break
            except Exception as e:
                last_e = e
                continue
                
        if response is None:
            raise last_e

        answer_md = response.content.strip()

        return {
            "report": answer_md,
            "sections": {"answer": answer_md, "sources_list": context_chunks}
        }

    except Exception as e:
        if "413" in str(e) or "rate_limit" in str(e) or "too large" in str(e).lower():
            err_msg = "The research context is too large. Please try a shorter or more specific topic."
            return {
                "report": err_msg,
                "sections": {"error": err_msg, "sources_list": []}
            }
        return {
            "report": f"Error generating follow-up answer: {str(e)}",
            "sections": {"error": str(e), "sources_list": []}
        }


def _parse_sections(markdown: str) -> dict:
    """Extract named sections from the markdown report."""
    sections = {}
    section_patterns = {
        "executive_summary": r"##\s*Executive Summary\s*\n(.*?)(?=##|\Z)",
        "key_findings": r"##\s*Key Findings\s*\n(.*?)(?=##|\Z)",
        "deep_analysis": r"##\s*Deep Analysis\s*\n(.*?)(?=##|\Z)",
        "conflicting_viewpoints": r"##\s*Conflicting Viewpoints\s*\n(.*?)(?=##|\Z)",
        "knowledge_gaps": r"##\s*Knowledge Gaps\s*\n(.*?)(?=##|\Z)",
        "sources_used": r"##\s*Sources Used\s*\n(.*?)(?=##|\Z)",
    }

    for key, pattern in section_patterns.items():
        match = re.search(pattern, markdown, re.DOTALL | re.IGNORECASE)
        sections[key] = match.group(1).strip() if match else ""

    return sections
