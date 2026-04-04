import streamlit as st
from agent.researcher import run_research

st.set_page_config(
    page_title="ResearchMind AI",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 ResearchMind AI")
st.write("Generate structured research briefs from real web sources.")

query = st.text_input("Enter a research topic")

if st.button("Generate Research Brief"):

    if query.strip() == "":
        st.warning("Please enter a research topic.")
    else:
        with st.spinner("Researching..."):
            result = run_research(query)

        st.markdown(result)