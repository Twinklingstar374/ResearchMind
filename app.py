import streamlit as st
from agent.researcher import run_research

st.set_page_config(
    page_title="ResearchMind",
    page_icon="",
    layout="wide"
)

# Clean minimal CSS
st.markdown("""
<style>
    .main { padding: 2rem 3rem; }
    .stButton > button {
        background-color: #1a1a1a;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #333;
    }
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #ddd;
        padding: 0.75rem;
        font-size: 15px;
    }
    .stDownloadButton > button {
        background-color: white;
        color: #1a1a1a;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 13px;
    }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ResearchMind")
    st.markdown("---")
    st.markdown("""
    An autonomous AI research agent that searches 
    the web, builds a knowledge base, and generates 
    structured research briefs in seconds.
    """)
    st.markdown("---")
    st.markdown("**Sample topics**")

    samples = [
        "AI agents in 2025",
        "Indian startup ecosystem",
        "RAG vs Fine-tuning",
        "Generative AI in healthcare",
        "LangChain vs LlamaIndex"
    ]

    for sample in samples:
        if st.button(sample, use_container_width=True, key=sample):
            st.session_state.query = sample

    st.markdown("---")
# Main area
st.markdown("## ResearchMind")
st.markdown(
    "<p style='color: #666; font-size: 15px; margin-top: -10px;'>"
    "Enter a topic and get a structured research brief from live web sources."
    "</p>",
    unsafe_allow_html=True
)
st.markdown("---")

query = st.text_input(
    "",
    value=st.session_state.get("query", ""),
    placeholder="e.g. Impact of AI on Indian job market...",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([1, 1, 5])
with col1:
    search_btn = st.button("Generate", type="primary", use_container_width=True)
with col2:
    clear_btn = st.button("Clear", use_container_width=True)

if clear_btn:
    st.session_state.query = ""
    st.rerun()

st.markdown("---")

if search_btn and query.strip():
    with st.status("Researching...", expanded=True) as status:
        st.write("Searching the web for relevant sources...")
        st.write("Chunking and embedding article content...")
        st.write("Retrieving most relevant context...")
        st.write("Generating structured brief...")
        result = run_research(query)
        status.update(label="Done", state="complete")

    st.markdown("### Research Brief")
    st.markdown(result)
    st.markdown("---")

    col1, col2 = st.columns([1, 5])
    with col1:
        st.download_button(
            label="Download (.md)",
            data=result,
            file_name=f"{query[:30].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )

elif search_btn and not query.strip():
    st.warning("Please enter a research topic.")


