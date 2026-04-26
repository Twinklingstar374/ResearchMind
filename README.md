# ResearchMind 🔬

An **agentic, chat-based AI research assistant** that searches the live web from multiple angles, scores source credibility, builds a per-session vector knowledge base, and generates structured, citation-backed research reports — all in a conversational interface.

**Live Demo → [researchmind.streamlit.app](https://researchmind-idvhtpjhjwmt4zuydlztjv.streamlit.app/)**

---

## What it does

You type any research question. ResearchMind:

1. **Classifies** your message — is it new research or a follow-up?
2. **Decomposes** your query into 3 focused research angles (using Groq LLaMA 3.1)
3. **Searches** the live web for 4 sources per angle via Tavily API (12 total)
4. **Scores** every source on Recency, Relevance, and Domain credibility
5. **Filters** to top 5 highest-credibility sources (min score: 40/100)
6. **Embeds** those sources into a per-session ChromaDB vector store
7. **Synthesizes** a structured 6-section report using Groq LLaMA 3.1
8. **Follow-ups** retrieve directly from the vector store — no extra search needed
9. **Exports** every report as a formatted PDF

---

## Architecture

```
User Query
    │
    ▼
Query Classifier (Groq LLaMA 3.1)
    │
    ├── new_research ─────────────────────────────────────────┐
    │       ↓                                                  │
    │   Query Decomposer → 3 Sub-Questions                     │
    │       ↓                                                  │
    │   Tavily Web Search (4 results × 3 angles)               │
    │       ↓                                                  │
    │   Source Scorer (Recency + Relevance + Domain)           │
    │       ↓                                                  │
    │   VectorStore.embed_sources() → ChromaDB                 │
    │       ↓                                                  │
    │   Synthesizer → 6-section Markdown Report                │
    │                                                          │
    └── followup ──────────────────────────────────────────────┤
            ↓                                                  │
        VectorStore.semantic_search() → Top 5 Chunks          │
            ↓                                                  │
        Synthesizer → Focused Answer                           │
            │                                                  │
            ▼                                                  ▼
        ResearchMemory (sliding window: 10 exchanges)
            ↓
        Streamlit Chat UI → PDF Download
```

---

## Report Structure

Every research report contains:
- **Executive Summary** — 2-3 sentence crisp overview
- **Key Findings** — 5 specific bullet points with inline citations
- **Deep Analysis** — 2-3 detailed paragraphs with nuance
- **Conflicting Viewpoints** — where sources disagree
- **Knowledge Gaps** — what remains unclear
- **Sources Used** — title + URL + credibility score

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq (LLaMA 3.1-8B Instant) |
| Web Search | Tavily API (multi-angle) |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Vector DB | ChromaDB (per-session collections) |
| Memory | Custom sliding-window chat memory |
| PDF Export | FPDF2 |
| Frontend | Streamlit (chat interface) |
| Deployment | Docker / HuggingFace Spaces / Streamlit Cloud |

---

## File Structure

```
researchmind/
├── agent/
│   ├── brain.py          ← ResearchAgent orchestrator
│   ├── decomposer.py     ← Query → 3 sub-questions
│   ├── prompts.py        ← LLM system prompts
│   ├── researcher.py     ← Original single-pipeline (preserved)
│   ├── scorer.py         ← Source credibility scoring
│   └── synthesizer.py    ← Report + follow-up generation
├── memory/
│   └── chat_memory.py    ← Sliding-window session memory
├── output/
│   └── pdf_generator.py  ← PDF export (FPDF2)
├── ui/
│   └── components.py     ← Chat UI components
├── utils/
│   ├── chunker.py        ← Text splitter
│   ├── embeddings.py     ← Original embed/retrieve helpers
│   └── search.py         ← search_web + multi_search
├── vector_store/
│   └── store.py          ← Per-session VectorStore class
├── app.py                ← Streamlit chat app
├── Dockerfile            ← HuggingFace Spaces compatible
└── requirements.txt
```

---

## Run Locally

```bash
# Clone
git clone https://github.com/Twinklingstar374/ResearchMind
cd ResearchMind

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add API keys
echo "GROQ_API_KEY=your_key_here" > .env
echo "TAVILY_API_KEY=your_key_here" >> .env

# Run
streamlit run app.py
```

## Run with Docker

```bash
docker build -t researchmind .
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  researchmind
```

---

## API Keys

| Key | Get it free at |
|---|---|
| Groq API | [console.groq.com](https://console.groq.com) |
| Tavily API | [tavily.com](https://tavily.com) |

Only 2 keys needed. Add them to `.env`.

---

## Key Engineering Decisions

**Why multi-angle decomposition?**
Single-query search misses adjacent perspectives. Breaking into 3 angles ensures coverage of current state, challenges, and future trends — giving the synthesizer richer, more balanced material.

**Why source scoring?**
Not all web results are equal. Scoring on domain credibility (arxiv vs random blog), recency, and Tavily relevance ensures the LLM synthesizes from the most trustworthy sources — reducing hallucination risk.

**Why per-session ChromaDB collections?**
Using `session_{uuid}` collection names prevents context pollution between users and sessions — a critical correctness fix for multi-user deployments.

**Why sliding-window memory?**
Keeping only the last 10 exchanges prevents context window overflow while giving the LLM enough history to classify follow-ups accurately.

---

*Built by Bulbul Agarwalla — B.Tech AI, Newton School of Technology*
