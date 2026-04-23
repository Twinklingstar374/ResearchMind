import streamlit as st
from agent.researcher import run_research

st.set_page_config(
    page_title="ResearchMind",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean minimal CSS with Glassmorphism
st.markdown("""
<style>
    /* Global Styles */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
    }
    .stApp {
        font-family: 'Inter', 'Roboto', sans-serif;
    }
    .main {
        padding: 2rem 3rem;
        background-color: transparent !important;
    }
    
    /* Header and Subheader text */
    h1, h2, h3, p {
        color: #ffffff !important;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.5);
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#fff, #b3b3ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        text-align: center;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: #ddd !important;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 300;
    }

    /* Buttons */
    .stButton > button {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    /* Input Field */
    .stTextInput > div > div > input {
        background: rgba(0, 0, 0, 0.4) !important;
        color: white !important;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 1rem;
        font-size: 18px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .stTextInput > div > div > input::placeholder {
        color: #aaa !important;
    }
    .stTextInput > div > div > input:focus {
        border: 1px solid #b3b3ff;
        box-shadow: 0 0 10px rgba(179, 179, 255, 0.5);
    }

    /* Glassmorphism Card for Results */
    .glass-card {
        background: rgba(10, 10, 25, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
        color: #e0e0e0;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-top: 2rem;
    }
    
    .glass-card h1, .glass-card h2, .glass-card h3 {
        color: #fff !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    
    .glass-card a {
        color: #b3b3ff !important;
        text-decoration: none;
    }
    
    .glass-card a:hover {
        text-decoration: underline;
    }
    
    .glass-card ul {
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem 2rem;
        border-radius: 8px;
        border-left: 3px solid #b3b3ff;
    }

    .glass-card li {
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }

    /* Download button specific */
    .stDownloadButton > button {
        background: rgba(179, 179, 255, 0.2);
        color: white;
        border: 1px solid rgba(179, 179, 255, 0.5);
        border-radius: 8px;
        font-weight: 500;
        margin-top: 1rem;
    }
    
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    header { background: transparent !important; }
    .block-container { padding-top: 3rem; max-width: 900px; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 20, 0.9) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
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

# Main Page UI
st.markdown("<h1 class='hero-title'>ResearchMind</h1>", unsafe_allow_html=True)
st.markdown("<p class='hero-subtitle'>Discover deep insights. AI-powered research, zero fluff.</p>", unsafe_allow_html=True)

query = st.text_input(
    "",
    value=st.session_state.get("query", ""),
    placeholder="What would you like to research today? (e.g. Impact of AI on markets...)",
    label_visibility="collapsed"
)

# Layout buttons centered
c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
with c2:
    search_btn = st.button("Generate Brief", use_container_width=True)
with c3:
    clear_btn = st.button("Clear Search", use_container_width=True)

if clear_btn:
    st.session_state.query = ""
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

if search_btn and query.strip():
    with st.status("Synthesizing intelligence...", expanded=True) as status:
        st.write("Searching the web for relevant sources...")
        st.write("Chunking and embedding article content...")
        st.write("Retrieving most relevant context...")
        st.write("Generating structured brief...")
        
        try:
            result = run_research(query)
            status.update(label="Research Complete!", state="complete")
        except Exception as e:
            st.error(f"An error occurred during research: {str(e)}")
            result = None

    if result:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(result)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="Download Structured Brief (.md)",
                data=result,
                file_name=f"{query[:30].replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )

elif search_btn and not query.strip():
    st.warning("Please enter a research topic to begin.")


