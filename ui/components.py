"""
Upgraded ui/components.py — New visual components for the agentic chat UI.
Keeps a clean namespace so existing imports remain compatible.
"""

import streamlit as st


# ── Thinking Steps ───────────────────────────────────────────────────────────

def render_thinking_steps(sub_questions: list[str]):
    """
    Show animated agent thinking steps while research runs.
    Displays each sub-question being researched in a styled expander.

    Args:
        sub_questions: List of 3 sub-question strings
    """
    with st.expander("🧠 Agent Thinking Process", expanded=True):
        st.markdown(
            """
            <style>
            .think-step {
                background: rgba(100, 100, 255, 0.08);
                border-left: 3px solid #7c7cff;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                margin: 0.4rem 0;
                color: #d0d0ff;
                font-size: 0.92rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("**Breaking your query into research angles...**")
        for i, sq in enumerate(sub_questions, 1):
            st.markdown(
                f"<div class='think-step'>🔍 <b>Angle {i}:</b> {sq}</div>",
                unsafe_allow_html=True,
            )


# ── Source Card ───────────────────────────────────────────────────────────────

def render_source_card(source: dict):
    """
    Render a single source as a styled card with credibility badge.

    Args:
        source: Dict with title, url, credibility_score,
                recency_score, relevance_score, domain_score, content
    """
    score = source.get("credibility_score", 0)
    title = source.get("title", "Untitled")
    url = source.get("url", "#")
    recency = source.get("recency_score", 0)
    relevance = source.get("relevance_score", 0)
    domain = source.get("domain_score", 0)
    preview = source.get("content", "")[:180] + "..." if source.get("content") else ""

    # Color badge based on score
    if score >= 70:
        badge_color = "#22c55e"   # green
        badge_label = "High"
    elif score >= 40:
        badge_color = "#f59e0b"   # yellow
        badge_label = "Medium"
    else:
        badge_color = "#ef4444"   # red
        badge_label = "Low"

    st.markdown(
        f"""
        <div style="
            background: rgba(15, 15, 40, 0.85);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.8rem;
        ">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <a href="{url}" target="_blank" style="
                    color:#a5b4fc; font-weight:600; font-size:0.95rem;
                    text-decoration:none; flex:1; margin-right:0.5rem;
                ">🔗 {title}</a>
                <span style="
                    background:{badge_color}22; color:{badge_color};
                    border:1px solid {badge_color}55;
                    border-radius:20px; padding:2px 10px;
                    font-size:0.78rem; font-weight:700; white-space:nowrap;
                ">{badge_label} · {score:.0f}</span>
            </div>
            <div style="
                display:flex; gap:1rem; margin:0.5rem 0;
                font-size:0.78rem; color:#888;
            ">
                <span>📅 Recency: <b style="color:#c4b5fd">{recency}</b></span>
                <span>🎯 Relevance: <b style="color:#c4b5fd">{relevance}</b></span>
                <span>🌐 Domain: <b style="color:#c4b5fd">{domain}</b></span>
            </div>
            <p style="color:#aaa; font-size:0.82rem; margin:0; line-height:1.5;">
                {preview}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Report Renderer ───────────────────────────────────────────────────────────

def render_report(report_dict: dict):
    """
    Render the full structured markdown report with styled section headers.

    Args:
        report_dict: Dict with at minimum a 'report' key (markdown string)
    """
    report_md = report_dict.get("report", "")
    is_followup = report_dict.get("is_followup", False)

    tag = "💬 Follow-up Answer" if is_followup else "📋 Research Report"

    st.markdown(
        f"""
        <div style="
            background: rgba(10, 10, 30, 0.75);
            border: 1px solid rgba(130, 120, 255, 0.25);
            border-radius: 16px;
            padding: 1.8rem 2rem;
            margin-top: 1rem;
        ">
            <div style="
                color:#a5b4fc; font-size:0.82rem;
                font-weight:600; letter-spacing:0.08em;
                text-transform:uppercase; margin-bottom:1rem;
            ">{tag}</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        .report-body h2 {
            color: #c4b5fd !important;
            border-bottom: 1px solid rgba(196,181,253,0.2);
            padding-bottom: 0.3rem;
            margin-top: 1.4rem;
            font-size: 1.1rem;
        }
        .report-body ul { padding-left: 1.5rem; }
        .report-body li { margin-bottom: 0.4rem; line-height: 1.6; color: #ddd; }
        .report-body p { color: #d1d5db; line-height: 1.7; }
        .report-body a { color: #a5b4fc; }
        </style>
        <div class="report-body">
        """,
        unsafe_allow_html=True,
    )

    st.markdown(report_md)
    st.markdown("</div></div>", unsafe_allow_html=True)


# ── Session Stats ─────────────────────────────────────────────────────────────

def render_session_stats(stats_dict: dict):
    """
    Render compact session statistics in the sidebar.

    Args:
        stats_dict: Dict with:
            queries_made (int), sources_searched (int),
            last_query_sec (float), embedded_chunks (int)
    """
    queries = stats_dict.get("queries_made", 0)
    sources = stats_dict.get("sources_searched", 0)
    elapsed = stats_dict.get("last_query_sec", 0)
    chunks = stats_dict.get("embedded_chunks", 0)

    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            padding: 0.8rem 1rem;
            margin: 0.5rem 0;
        ">
            <div style="font-size:0.75rem; color:#888; font-weight:600;
                        letter-spacing:0.06em; text-transform:uppercase;
                        margin-bottom:0.5rem;">Session Stats</div>
            <table style="width:100%; font-size:0.82rem; color:#ccc;">
                <tr>
                    <td>🔎 Queries</td>
                    <td style="text-align:right; color:#a5b4fc; font-weight:700">{queries}</td>
                </tr>
                <tr>
                    <td>📄 Sources found</td>
                    <td style="text-align:right; color:#a5b4fc; font-weight:700">{sources}</td>
                </tr>
                <tr>
                    <td>🧩 Chunks embedded</td>
                    <td style="text-align:right; color:#a5b4fc; font-weight:700">{chunks}</td>
                </tr>
                <tr>
                    <td>⏱ Last query</td>
                    <td style="text-align:right; color:#a5b4fc; font-weight:700">{elapsed}s</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
