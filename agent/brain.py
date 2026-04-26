"""
ResearchAgent (brain.py) — Main orchestrator that classifies queries,
runs multi-angle research or follow-up answers, and coordinates all modules.
"""

import time
from langchain_groq import ChatGroq
from dotenv import load_dotenv

from agent.decomposer import decompose_query
from agent.scorer import score_sources
from agent.synthesizer import synthesize_report, synthesize_followup
from utils.search import multi_search
from vector_store.store import VectorStore
from memory.chat_memory import ResearchMemory

load_dotenv()


CLASSIFY_PROMPT = """You are a query classifier. Given a user message and their conversation history, decide if this is:
- "new_research": A brand-new research topic requiring web search
- "followup": A follow-up question about something already researched

Rules:
- If there is no conversation history, it is ALWAYS "new_research"
- If the message asks to go deeper, explain more, or asks about a sub-topic of recent research, it is "followup"
- If the message introduces a completely different topic, it is "new_research"
- Return ONLY the string "new_research" or "followup" with no other text

Conversation history summary:
{history_summary}

Current message:
{message}"""


class ResearchAgent:
    """
    Main orchestrator for ResearchMind.
    Handles query classification, multi-angle research, follow-up answering.
    """

    def __init__(self):
        pass

    def _classify(self, query: str, memory: ResearchMemory) -> str:
        """
        Classify the query as 'new_research' or 'followup'.
        Falls back to 'new_research' on any error.
        """
        if not memory.has_research():
            return "new_research"

        history_summary = memory.get_research_context()

        models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile", 
            "gemma2-9b-it"
        ]
        
        response = None
        last_e = None

        try:
            for model_name in models_to_try:
                try:
                    llm = ChatGroq(
                        model=model_name,
                        temperature=0.1,
                        max_tokens=1024
                    )
                    response = llm.invoke([
                        {
                            "role": "user",
                            "content": CLASSIFY_PROMPT.format(
                                history_summary=history_summary,
                                message=query
                            )
                        }
                    ])
                    break
                except Exception as e:
                    last_e = e
                    continue
            
            if response is None:
                raise last_e
            classification = response.content.strip().lower()
            if "followup" in classification:
                return "followup"
            return "new_research"
        except Exception as e:
            if "413" in str(e) or "rate_limit" in str(e) or "too large" in str(e).lower():
                return "The research context is too large. Please try a shorter or more specific topic."
            print(f"[Brain] Classification error: {e}")
            return "new_research"

    def run(self, query: str, memory: ResearchMemory, vector_store: VectorStore) -> dict:
        """
        Main entry point for the research agent.

        Args:
            query: The user's input message
            memory: ResearchMemory instance for this session
            vector_store: VectorStore instance for this session

        Returns:
            dict with keys:
                report         — markdown string
                sources        — list of scored source dicts
                sub_questions  — list of 3 sub-question strings
                scores         — list of credibility scores
                is_followup    — bool
                error          — str or None
                elapsed_sec    — float
        """
        start_time = time.time()
        chat_history = memory.get_history()
        classification = self._classify(query, memory)
        is_followup = classification == "followup"

        try:
            if not is_followup:
                result = self._run_new_research(
                    query, chat_history, memory, vector_store
                )
            else:
                result = self._run_followup(query, chat_history, vector_store)

            elapsed = round(time.time() - start_time, 2)
            result["elapsed_sec"] = elapsed
            result["error"] = None

            # Store in memory
            memory.store_research(query, result)
            memory.add_exchange(query, result.get("report", ""))

            return result

        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            return {
                "report": f"An error occurred during research: {str(e)}",
                "sources": [],
                "sub_questions": [],
                "scores": [],
                "is_followup": is_followup,
                "elapsed_sec": elapsed,
                "error": str(e)
            }

    # ── New Research Pipeline ────────────────────────────────────────────────

    def _run_new_research(
        self,
        query: str,
        chat_history: list,
        memory: ResearchMemory,
        vector_store: VectorStore
    ) -> dict:
        """Full new-research pipeline: decompose → search → score → embed → synthesize."""

        # Step 1: Decompose into 3 sub-questions
        sub_questions = decompose_query(query)

        # Step 2: Search each sub-question (4 results each)
        search_results = multi_search(sub_questions)

        # Step 3: Collect all sources
        all_sources = []
        for angle_key, angle_data in search_results.items():
            all_sources.extend(angle_data.get("sources", []))

        # Step 4: Score and filter to top 5
        top_sources = score_sources(all_sources)

        # Step 5: Embed top 5 sources into vector store
        if top_sources:
            vector_store.embed_sources(top_sources)

        # Step 6: Synthesize structured report
        synthesis = synthesize_report(
            query=query,
            sources=top_sources,
            sub_questions=sub_questions,
            chat_history=chat_history
        )

        scores = [s.get("credibility_score", 0) for s in top_sources]

        return {
            "report": synthesis["report"],
            "sections": synthesis.get("sections", {}),
            "sources": top_sources,
            "sub_questions": sub_questions,
            "scores": scores,
            "search_angles": search_results,
            "is_followup": False
        }

    # ── Follow-Up Pipeline ───────────────────────────────────────────────────

    def _run_followup(
        self,
        query: str,
        chat_history: list,
        vector_store: VectorStore
    ) -> dict:
        """Follow-up pipeline: retrieve from vector store → synthesize focused answer."""

        # Retrieve relevant chunks from vector store
        context_chunks = vector_store.semantic_search(query, k=5)

        if not context_chunks:
            # Fallback: inform the user no context available
            return {
                "report": (
                    "I don't have enough context from our previous research to "
                    "answer that. Please try rephrasing or start a new research query."
                ),
                "sections": {},
                "sources": [],
                "sub_questions": [],
                "scores": [],
                "is_followup": True
            }

        # Generate focused answer
        synthesis = synthesize_followup(
            question=query,
            context_chunks=context_chunks,
            chat_history=chat_history
        )

        return {
            "report": synthesis["report"],
            "sections": synthesis.get("sections", {}),
            "sources": context_chunks,
            "sub_questions": [],
            "scores": [],
            "is_followup": True
        }
