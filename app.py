"""
ResearchMind — Agentic Chat-Based Research Assistant
Streamlit Custom UI Version - Fixed Layout
"""

import streamlit as st
import sys
import os
from uuid import uuid4
from datetime import datetime

# Ensure Streamlit Cloud correctly resolves local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.brain import ResearchAgent
from memory.chat_memory import ResearchMemory
from vector_store.store import VectorStore

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session State Init ────────────────────────────────────────────────────────
if "screen" not in st.session_state:
    st.session_state.screen = "landing"
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid4().hex
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = []
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "memory" not in st.session_state:
    st.session_state.memory = ResearchMemory()
if "agent" not in st.session_state:
    st.session_state.agent = ResearchAgent()
if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore(session_id=st.session_state.session_id)

def _reset_session():
    st.session_state.memory.clear()
    st.session_state.vector_store.reset()
    st.session_state.messages = []
    st.session_state.sources = []
    st.session_state.topic = ""
    st.session_state.session_id = uuid4().hex
    st.session_state.vector_store = VectorStore(session_id=st.session_state.session_id)
    st.session_state.screen = "landing"

# ── Global CSS Injection ──────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Syne:wght@700;800&display=swap');

    /* Hide all Streamlit defaults */
    #MainMenu, header, footer, .stDeployButton { display: none !important; }
    .block-container { padding: 2rem !important; max-width: 1400px !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #020510 !important;
        font-family: 'DM Sans', sans-serif;
        color: rgba(228,224,245,0.9);
    }
    
    /* Global scrollbar styling */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }

    /* Fix Streamlit button generic hover */
    .stButton > button {
        border-radius: 10px;
        transition: all 0.2s ease;
    }
    .stButton > button:focus {
        box-shadow: none !important;
        color: white !important;
    }

    /* Chat Input Override */
    [data-testid="stChatInputContainer"] {
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 16px !important;
        padding: 0.5rem !important;
        margin-bottom: 1rem !important;
    }
    [data-testid="stChatInputContainer"] textarea {
        color: #e4e0f5 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    
    /* Spinner override */
    .stSpinner > div > div {
        border-top-color: #8b5cf6 !important;
        border-right-color: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.session_state.screen == "landing":
    # ── Screen 1: Landing Page ────────────────────────────────────────────────
    st.markdown(
        """
        <style>
        .block-container { padding: 0 !important; max-width: 100% !important; }
        .bg-orbs {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: 
                radial-gradient(circle at 20% 30%, rgba(109,40,217,0.2) 0%, transparent 40%),
                radial-gradient(circle at 80% 70%, rgba(67,56,202,0.2) 0%, transparent 40%);
            z-index: 0;
            animation: orbsFloat 10s infinite alternate;
        }
        .star-field {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: radial-gradient(rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 40px 40px;
            z-index: 0;
            opacity: 0.5;
        }
        @keyframes orbsFloat {
            from { transform: translateY(0) scale(1); }
            to { transform: translateY(-20px) scale(1.05); }
        }
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.5); opacity: 0.5; }
            100% { transform: scale(1); opacity: 1; }
        }
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Specialized Landing Button */
        div[data-testid="stButton"] > button {
            background: linear-gradient(135deg, #6d28d9, #4338ca) !important;
            border: none !important;
            border-radius: 100px !important;
            box-shadow: 0 20px 60px rgba(109,40,217,0.4) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            padding: 1.5rem !important;
            font-size: 1.2rem !important;
            width: 100%;
        }
        div[data-testid="stButton"] > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 25px 70px rgba(109,40,217,0.6) !important;
        }
        </style>

        <div class="bg-orbs"></div>
        <div class="star-field"></div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="position: relative; z-index: 1; text-align: center; animation: fadeUp 1s ease-out; padding: 0 2rem;">
            <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 6px 16px; border-radius: 100px; font-size: 0.85rem; color: rgba(200,190,230,0.8); margin-bottom: 2rem;">
                <div style="width: 8px; height: 8px; background: #8b5cf6; border-radius: 50%; box-shadow: 0 0 10px #8b5cf6; animation: pulse 2s infinite;"></div>
                AI Research Intelligence
            </div>
            <h1 style="font-family: 'Syne', sans-serif; font-weight: 800; font-size: clamp(2rem, 4vw, 3.2rem); line-height: 1.1; margin: 0 0 1.5rem 0; background: linear-gradient(135deg, #ffffff 0%, #c4b5fd 50%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Research at the<br>speed of thought</h1>
            <p style="font-size: 1.2rem; color: rgba(200,190,230,0.7); max-width: 600px; margin: 0 auto 3rem auto; line-height: 1.6;">Multi-angle search, credibility scoring, and AI synthesis to uncover the truth hidden in the noise.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render Streamlit Button safely in columns
    _, col_btn, _ = st.columns([1, 0.3, 1])
    with col_btn:
        if st.button("Start Researching →", use_container_width=True):
            st.session_state.screen = "research"
            st.rerun()
            
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="position: relative; z-index: 2; display: flex; flex-wrap: wrap; justify-content: center; gap: 1rem; padding: 0 2rem;">
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; color: rgba(200,190,230,0.6);">Live web sources</div>
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; color: rgba(200,190,230,0.6);">AI synthesis</div>
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; color: rgba(200,190,230,0.6);">Credibility scoring</div>
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; color: rgba(200,190,230,0.6);">Follow-up questions</div>
        </div>
        """,
        unsafe_allow_html=True
    )

elif st.session_state.screen == "research":
    # ── Screen 2: Research Interface ──────────────────────────────────────────
    
    st.markdown(
        """
        <style>
        /* Top nav buttons styling */
        .nav-btn div[data-testid="stButton"] > button {
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 100px !important;
            color: rgba(228,224,245,0.9) !important;
            padding: 0.4rem 1rem !important;
            font-size: 0.9rem !important;
        }
        .nav-btn div[data-testid="stButton"] > button:hover {
            background: rgba(255,255,255,0.1) !important;
        }
        
        /* Chip container CSS */
        div[data-testid="stHorizontalBlock"] [data-testid="stButton"] > button {
            border-radius: 100px !important;
            background: rgba(109,40,217,0.15) !important;
            border: 1px solid rgba(139,92,246,0.25) !important;
            color: #c4b5fd !important;
            font-size: 13px !important;
        }
        div[data-testid="stHorizontalBlock"] [data-testid="stButton"] > button:hover {
            background: rgba(109,40,217,0.3) !important;
            border-color: rgba(139,92,246,0.5) !important;
        }
        
        /* New Question Banner */
        .banner-btn div[data-testid="stButton"] > button {
            background: transparent !important;
            border: 1px solid rgba(139,92,246,0.3) !important;
            border-radius: 12px !important;
            color: #c4b5fd !important;
            padding: 0.8rem 1rem !important;
        }
        .banner-btn div[data-testid="stButton"] > button:hover {
            background: rgba(109,40,217,0.1) !important;
            border-color: rgba(139,92,246,0.6) !important;
        }
        
        /* Chat Input Styling */
        div[data-testid="stChatInput"] {
            background: transparent !important;
        }
        div[data-testid="stChatInput"] > div {
            background-color: rgba(10,10,25,0.5) !important;
            border: 1px solid rgba(139,92,246,0.3) !important;
            border-radius: 20px !important;
            transition: all 0.2s ease;
        }
        div[data-testid="stChatInput"] > div:focus-within {
            border-color: rgba(139,92,246,0.8) !important;
            box-shadow: 0 0 10px rgba(139,92,246,0.2) !important;
        }
        div[data-testid="stChatInput"] div[data-baseweb="textarea"],
        div[data-testid="stChatInput"] div[data-baseweb="base-input"],
        div[data-testid="stChatInput"] textarea {
            background-color: transparent !important;
            color: #f1f5f9 !important;
        }
        div[data-testid="stChatInput"] textarea::placeholder {
            color: rgba(196,181,253,0.5) !important;
        }
        div[data-testid="stChatInput"] button {
            color: #c4b5fd !important;
            background-color: transparent !important;
        }
        div[data-testid="stChatInput"] button:hover {
            color: #ffffff !important;
            background-color: rgba(109,40,217,0.5) !important;
            border-radius: 50% !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # ── Top Nav (using Streamlit columns cleanly) ──
    col_logo, col_space, col_new, col_home = st.columns([4, 4, 1.2, 1.2], vertical_alignment="center")
    
    with col_logo:
        st.markdown("<div style='font-family:Syne; font-weight:800; font-size:1.4rem; background:linear-gradient(135deg, #a5b4fc, #c4b5fd); -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>⬡ ResearchMind</div>", unsafe_allow_html=True)
    
    with col_new:
        st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
        if st.button("New Topic", use_container_width=True):
            st.session_state.topic = ""
            st.session_state.messages = []
            st.session_state.sources = []
            st.session_state.memory.clear()
            st.session_state.vector_store.reset()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_home:
        st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
        if st.button("← Home", use_container_width=True):
            _reset_session()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin-top: 0.5rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

    # ── Main Layout ──
    col_chat, col_sources = st.columns([2, 1], gap="large")
    
    with col_chat:
        st.markdown(
            """
            <style>
            .robot-wrapper {
                position: relative;
                width: 100px;
                height: 100px;
                margin: 0 auto 2rem auto;
            }
            .robot-glow {
                position: absolute;
                top: 50%; left: 50%;
                transform: translate(-50%, -50%);
                width: 120px;
                height: 120px;
                background: radial-gradient(circle, rgba(139,92,246,0.4) 0%, transparent 70%);
                filter: blur(20px);
                z-index: 0;
            }
            .robot-svg {
                position: relative;
                z-index: 1;
                animation: robotFloat 4s ease-in-out infinite;
            }
            @keyframes robotFloat {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-8px); }
            }
            @keyframes fadeBreath { 
                0%, 100% {opacity:0.3} 
                50% {opacity:1} 
            }
            .fade-breath {
                animation: fadeBreath 2s infinite ease-in-out;
            }
            .msg-bubble {
                max-width: 85%;
                padding: 1rem 1.2rem;
                margin-bottom: 1.5rem;
                line-height: 1.6;
                font-size: 0.95rem;
            }
            .msg-user {
                background: rgba(109,40,217,0.2);
                border: 1px solid rgba(139,92,246,0.3);
                border-radius: 12px 0 12px 12px;
            }
            .msg-ai {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 0 12px 12px 12px;
                display: flex;
                gap: 12px;
            }
            .ai-avatar {
                flex-shrink: 0;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: linear-gradient(135deg, #6d28d9, #4338ca);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1rem;
            }
            /* Markdown styling inside AI bubble */
            .msg-bubble p:last-child { margin-bottom: 0; }
            .msg-bubble h1, .msg-bubble h2, .msg-bubble h3 { color: #fff; margin-top:0; font-family: 'Syne', sans-serif;}
            .msg-bubble a { color: #a5b4fc; }
            .msg-bubble ul, .msg-bubble ol { padding-left: 1.5rem; margin-bottom: 1rem; }
            </style>
            """,
            unsafe_allow_html=True
        )

        chat_container = st.container(height=650, border=False)

        with chat_container:
            if st.session_state.get("is_loading", False):
                st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
                st.markdown(
                    """
                    <div class="robot-wrapper fade-breath">
                        <div class="robot-glow"></div>
                        <svg class="robot-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <line x1="50" y1="15" x2="50" y2="30" stroke="#8b5cf6" stroke-width="3"/>
                            <circle cx="50" cy="15" r="4" fill="#c4b5fd"/>
                            <rect x="25" y="30" width="50" height="45" rx="12" fill="url(#botGrad)"/>
                            <rect x="35" y="40" width="12" height="6" rx="3" fill="#020510"/>
                            <circle cx="41" cy="43" r="1.5" fill="#ffffff" filter="drop-shadow(0 0 2px #fff)"/>
                            <rect x="53" y="40" width="12" height="6" rx="3" fill="#020510"/>
                            <circle cx="59" cy="43" r="1.5" fill="#ffffff" filter="drop-shadow(0 0 2px #fff)"/>
                            <circle cx="35" cy="60" r="3" fill="#818cf8"/>
                            <circle cx="45" cy="60" r="3" fill="#4ade80"/>
                            <line x1="55" y1="60" x2="65" y2="60" stroke="#020510" stroke-width="3" stroke-linecap="round"/>
                            <defs>
                                <linearGradient id="botGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stop-color="#6d28d9"/>
                                    <stop offset="100%" stop-color="#4338ca"/>
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                    <div style="color:rgba(139,92,246,0.8); text-align:center; font-size: 0.9rem; margin-top:1rem;">Researching...</div>
                    """,
                    unsafe_allow_html=True
                )
            elif not st.session_state.messages:
                # ── Idle State ──
                st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
                st.markdown(
                    """
                    <div class="robot-wrapper">
                        <div class="robot-glow"></div>
                        <svg class="robot-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <line x1="50" y1="15" x2="50" y2="30" stroke="#8b5cf6" stroke-width="3"/>
                            <circle cx="50" cy="15" r="4" fill="#c4b5fd"/>
                            <rect x="25" y="30" width="50" height="45" rx="12" fill="url(#botGrad)"/>
                            <rect x="35" y="40" width="12" height="6" rx="3" fill="#020510"/>
                            <circle cx="41" cy="43" r="1.5" fill="#ffffff" filter="drop-shadow(0 0 2px #fff)"/>
                            <rect x="53" y="40" width="12" height="6" rx="3" fill="#020510"/>
                            <circle cx="59" cy="43" r="1.5" fill="#ffffff" filter="drop-shadow(0 0 2px #fff)"/>
                            <circle cx="35" cy="60" r="3" fill="#818cf8"/>
                            <circle cx="45" cy="60" r="3" fill="#4ade80"/>
                            <line x1="55" y1="60" x2="65" y2="60" stroke="#020510" stroke-width="3" stroke-linecap="round"/>
                            <defs>
                                <linearGradient id="botGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" stop-color="#6d28d9"/>
                                    <stop offset="100%" stop-color="#4338ca"/>
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                    <h2 style="font-family:'Syne', sans-serif; font-weight:700; font-size:2rem; color:#e4e0f5; text-align:center; margin-bottom:0.5rem;">What shall we research today?</h2>
                    <div style="color:rgba(200,190,230,0.5); text-align:center; margin-bottom:2rem;">Select a topic below or type your own question to begin.</div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Suggestion Chips
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Quantum Computing", use_container_width=True):
                        st.session_state.prompt_trigger = "Quantum Computing"
                        st.rerun()
                with col2:
                    if st.button("Fusion Energy", use_container_width=True):
                        st.session_state.prompt_trigger = "Fusion Energy"
                        st.rerun()
                with col3:
                    if st.button("CRISPR Tech", use_container_width=True):
                        st.session_state.prompt_trigger = "CRISPR Breakthroughs"
                        st.rerun()

            else:
                # ── Active State ──
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        st.markdown(
                            f"""
                            <div style="display:flex; justify-content:flex-end;">
                                <div class="msg-bubble msg-user">{msg["content"]}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        import markdown as md
                        ai_html = md.markdown(msg["content"], extensions=["fenced_code", "tables"])
                        st.markdown(
                            f"""
                            <div style="display:flex;">
                                <div class="msg-bubble msg-ai">
                                    <div class="ai-avatar">🤖</div>
                                    <div style="flex-grow:1; overflow-x:hidden;">{ai_html}</div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                


                if len(st.session_state.messages) >= 4 and not st.session_state.get("is_loading", False):
                    st.markdown('<div class="banner-btn">', unsafe_allow_html=True)
                    if st.button("✦ Ask a new research question →", use_container_width=True):
                        st.session_state.topic = ""
                        st.session_state.messages = []
                        st.session_state.sources = []
                        st.session_state.memory.clear()
                        st.session_state.vector_store.reset()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        
        # ── Input Area ──
        prompt = st.chat_input("Research any topic, or ask a follow-up...")
        
        if st.session_state.get("prompt_trigger"):
            prompt = st.session_state.prompt_trigger
            st.session_state.prompt_trigger = None
            
        if prompt and not st.session_state.get("is_loading", False):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.is_loading = True
            st.rerun()

        if st.session_state.get("is_loading", False):
            user_msg = st.session_state.messages[-1]["content"]
            
            try:
                result = st.session_state.agent.run(
                    query=user_msg,
                    memory=st.session_state.memory,
                    vector_store=st.session_state.vector_store,
                )
                
                if result.get("error"):
                    ai_content = f"⚠️ Error: {result['error']}"
                else:
                    ai_content = result.get("report", "No report generated.")
                    st.session_state.sources = result.get("sources", [])
                
            except Exception as e:
                ai_content = f"⚠️ Error: {str(e)}"
                
            st.session_state.messages.append({"role": "assistant", "content": ai_content})
            st.session_state.is_loading = False
            st.rerun()

    with col_sources:
        html_str = """<style>
.sources-panel {
    border-left: 1px solid rgba(255,255,255,0.05);
    padding-left: 2rem;
    height: 650px;
    overflow-y: auto;
    margin-top: 0;
}
.panel-header {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgba(200,190,230,0.5);
    margin-bottom: 1.5rem;
    font-weight: 700;
}
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: rgba(200,190,230,0.4);
    font-size: 0.9rem;
    text-align: center;
    border: 1px dashed rgba(255,255,255,0.1);
    border-radius: 12px;
}
.empty-state span {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}
.source-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
    transition: transform 0.2s ease, background 0.2s ease;
}
.source-card:hover {
    transform: translateX(4px);
    background: rgba(109,40,217,0.08);
    border-color: rgba(139,92,246,0.3);
}
.source-num {
    color: #8b5cf6;
    font-size: 0.75rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
    display: block;
}
.source-title {
    color: #f1f5f9;
    font-weight: 500;
    font-size: 0.95rem;
    line-height: 1.4;
    margin-bottom: 0.4rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.source-url {
    color: rgba(196,181,253,0.6);
    font-size: 0.8rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 0.8rem;
    display: block;
}
.score-bar-bg {
    background: rgba(255,255,255,0.05);
    height: 3px;
    border-radius: 2px;
    width: 100%;
    overflow: hidden;
}
.score-bar-fill {
    background: linear-gradient(90deg, #6d28d9, #c4b5fd);
    height: 100%;
    border-radius: 2px;
}
</style>
<div class="sources-panel">
<div class="panel-header">SOURCES & REFERENCES</div>
"""

        if not st.session_state.sources:
            html_str += """<div class="empty-state">
    <span>🔗</span>
    Sources will appear here<br>as we research
</div>"""
        else:
            for i, src in enumerate(st.session_state.sources):
                title = src.get("title", "Untitled Source")
                url = src.get("url", "#")
                score = src.get("score", 50)
                if isinstance(score, dict):
                    score = score.get("total", 50)
                    
                score_val = score
                try:
                    score_val = float(score_val)
                    score_pct = round(score_val * 100) if score_val <= 1.0 else round(score_val)
                except:
                    score_pct = 50
                    
                html_str += f"""<a href="{url}" target="_blank" style="text-decoration:none;">
<div class="source-card">
    <span class="source-num">SOURCE {i+1}</span>
    <div class="source-title">{title}</div>
    <div class="source-url">{url}</div>
    <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; color:#8b5cf6; margin-bottom:4px;">
        <span>Credibility Score</span>
        <span>{score_pct}%</span>
    </div>
    <div class="score-bar-bg">
        <div class="score-bar-fill" style="width: {score_pct}%;"></div>
    </div>
</div>
</a>"""

        html_str += '</div>'
        st.markdown(html_str, unsafe_allow_html=True)
