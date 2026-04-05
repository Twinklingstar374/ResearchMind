# ResearchMind

An autonomous AI research agent that searches the web, builds a vector knowledge base, and generates structured research
briefs using a full RAG pipeline.

**Live Demo → [researchmind.streamlit.app](https://researchmind-idvhtpjhjwmt4zuydlztjv.streamlit.app/)**


## What it does

You type a research topic. The agent:
1. Searches the live web for relevant articles (Tavily API)
2. Chunks and embeds article content into a vector store (ChromaDB)
3. Retrieves the most semantically relevant context (HuggingFace)
4. Generates a structured research brief using an LLM (Groq + LLaMA 3.1)

All in under 60 seconds.

---

## Architecture
User Query
↓
Tavily Search API       → fetches live web articles
↓
LangChain Text Splitter → chunks articles (500 chars, 50 overlap)
↓
HuggingFace Embeddings  → converts chunks to vectors
(all-MiniLM-L6-v2)
↓
ChromaDB Vector Store   → stores and retrieves by semantic similarity
↓
Groq LLaMA 3.1          → generates structured research brief
↓
Streamlit UI            → displays output to user

---

## Output format

Every research brief contains:
- **Summary** — 3-4 sentence overview
- **Key Findings** — 5 specific insights with data
- **Key Takeaway** — single most important insight
- **Sources** — all URLs used

---
## Tech Stack

| Layer | Tool |
|-------|------|
| Web Search | Tavily API |
| Text Splitting | LangChain Text Splitters |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Vector Store | ChromaDB |
| LLM | Groq + LLaMA 3.1-8b-instant |
| Orchestration | LangChain |
| Frontend | Streamlit |
| Deployment | Streamlit Cloud |

---
## Run locally
```bash
# Clone the repo
git clone https://github.com/Twinklingstar374/ResearchMind
cd ResearchMind

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add API keys
touch .env
# Add to .env:
# TAVILY_API_KEY=your_key
# GROQ_API_KEY=your_key

# Run
streamlit run app.py
```

---

## API Keys needed

| Key | Get it free at |
|-----|---------------|
| Tavily API | [tavily.com](https://tavily.com) |
| Groq API | [console.groq.com](https://console.groq.com) |

---

## Key engineering decisions

**Why RAG instead of direct GPT?**
GPT training data has a cutoff. RAG gives the model real-time, 
source-grounded information and prevents hallucination by 
restricting answers to retrieved context only.

**Why Groq instead of OpenAI?**
Groq runs LLaMA on custom LPU hardware — inference is significantly 
faster and the free tier is generous enough for production use.

**Bug fixed during development**
Identified and fixed a context pollution issue where ChromaDB retained 
embeddings from previous queries, contaminating new search results. 
Fixed by resetting the collection on each new research session.

---

## Project structure
researchmind/
├── agent/
│   ├── researcher.py     # core agent logic
│   └── prompts.py        # GPT system prompts
├── utils/
│   ├── search.py         # Tavily web search
│   ├── chunker.py        # text splitting
│   └── embeddings.py     # ChromaDB + HuggingFace
├── app.py                # Streamlit frontend
└── requirements.txt

---

## What's next

- Adaptive RAG — check vector store before web search
- Multi-query retrieval for better context coverage
- LangGraph migration for proper agentic orchestration
- LangSmith integration for agent observability

---

*Built by Bulbul Agarwalla — B.Tech AI, Newton School of Technology*
