"""
summarizer.py — Smart Summarizer with PDF download
"""

import re
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage


def _get_llm():
    return ChatGroq(model="llama-3.1-8b-instant", temperature=0)



def run_summarizer_feature():
    st.markdown("""
        <div style="margin-bottom:24px;">
            <h1 style="font-size:2rem; margin-bottom:6px;">📝 Smart Summarizer</h1>
            <p style="color:#94a3b8; font-size:0.95rem;">
                Get a concise, structured summary of your uploaded study material.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("raw_text"):
        st.markdown("""
            <div style="text-align:center; padding:60px 20px; color:#94a3b8;">
                <div style="font-size:56px; margin-bottom:16px;">📄</div>
                <h3 style="color:#e2e8f0; margin-bottom:8px;">No Documents Loaded</h3>
                <p>Upload and process your PDFs in the sidebar first, then generate a summary.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("✨ Generate Summary", use_container_width=True):
            st.session_state.summary = None
            with st.spinner("📝 Summarizing your documents..."):
                text = st.session_state.raw_text[:6000]
                llm = _get_llm()
                messages = [
                    SystemMessage(content=(
                        "You are a study assistant that creates well-structured, organized summaries. "
                        "Always follow the exact output format requested. "
                        "Use clear sections, bullet points, and definitions."
                    )),
                    HumanMessage(content=f"""Summarize this study material for a student.

Use EXACTLY this structure:

## Main Topic
One clear sentence about what this document covers.

## Key Concepts
- Concept 1: Brief explanation
- Concept 2: Brief explanation
- Concept 3: Brief explanation
- Concept 4: Brief explanation
- Concept 5: Brief explanation

## Detailed Overview
Write 4-6 sentences explaining the main ideas in simple language. Cover the most important points a student needs to understand.

## Important Definitions
- **Term 1**: Definition
- **Term 2**: Definition
- **Term 3**: Definition
- **Term 4**: Definition

## Quick Review Points
1. First key takeaway for exam prep
2. Second key takeaway
3. Third key takeaway
4. Fourth key takeaway
5. Fifth key takeaway

Document:
{text}""")
                ]
                response = llm.invoke(messages)
                st.session_state.summary = response.content
                st.rerun()

    with col2:
        if st.session_state.get("summary"):
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.summary = None
                st.rerun()

    if st.session_state.get("summary"):
        st.markdown("---")
        # Use native Streamlit markdown container for robust rendering
        with st.container():
            st.markdown(st.session_state.summary)
