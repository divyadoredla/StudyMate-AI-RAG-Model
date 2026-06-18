"""
flashcards.py — Interactive Flashcard Generator
Creates Q&A flashcards from uploaded PDF content.
"""

import re
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage


def _get_llm():
    return ChatGroq(model="llama-3.1-8b-instant", temperature=0)


def _parse_flashcards(raw: str) -> list[dict]:
    """
    Parses numbered flashcard format:
    1. Q: ... A: ...
    Also handles multi-line Q/A pairs.
    """
    cards = []
    # Normalize: remove markdown bold/italic
    text = re.sub(r'\*+', '', raw)

    # Strategy 1: find all Q: ... A: ... pairs
    pattern = re.findall(
        r'Q\s*\d*\s*[:\-]\s*(.+?)\s*A\s*\d*\s*[:\-]\s*(.+?)(?=Q\s*\d*\s*[:\-]|$)',
        text, re.DOTALL | re.IGNORECASE
    )
    for front, back in pattern:
        f = front.strip().replace("\n", " ")
        b = back.strip().replace("\n", " ")
        if f and b and len(f) > 3:
            cards.append({"front": f, "back": b})

    # Strategy 2: line-by-line fallback
    if not cards:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        i = 0
        while i < len(lines):
            q_m = re.match(r'^(?:\d+[\.\)]\s*)?(?:Q|FRONT|QUESTION)\s*\d*\s*[:\-]\s*(.+)', lines[i], re.IGNORECASE)
            if q_m:
                front = q_m.group(1).strip()
                for j in range(i + 1, min(i + 5, len(lines))):
                    a_m = re.match(r'^(?:A|BACK|ANSWER)\s*\d*\s*[:\-]\s*(.+)', lines[j], re.IGNORECASE)
                    if a_m:
                        back = a_m.group(1).strip()
                        if front and back:
                            cards.append({"front": front, "back": back})
                        i = j
                        break
            i += 1

    return cards[:10]


def run_flashcards_feature():
    st.markdown("""
        <div style="margin-bottom:24px;">
            <h1 style="font-size:2rem; margin-bottom:6px;">🃏 Flashcards</h1>
            <p style="color:#94a3b8; font-size:0.95rem;">
                Study smarter with AI-generated flashcards from your uploaded notes.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("raw_text"):
        st.markdown("""
            <div style="text-align:center; padding:60px 20px; color:#94a3b8;">
                <div style="font-size:56px; margin-bottom:16px;">🃏</div>
                <h3 style="color:#e2e8f0; margin-bottom:8px;">No Documents Loaded</h3>
                <p>Upload and process your PDFs in the sidebar first.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🎴 Generate Flashcards", use_container_width=True):
            st.session_state.flashcards = []
            st.session_state.current_card = 0
            st.session_state.card_flipped = False

            with st.spinner("🃏 Creating flashcards from your notes..."):
                text = st.session_state.raw_text[:4000]
                llm = _get_llm()

                messages = [
                    SystemMessage(content=(
                        "You are a flashcard generator. "
                        "You ONLY output flashcards. "
                        "You NEVER output document text, introductions, or explanations. "
                        "You ALWAYS follow the exact format given."
                    )),
                    HumanMessage(content=f"""Generate 10 flashcards from the study material below.

OUTPUT FORMAT — follow this EXACTLY:
Q: <question or key term>
A: <answer or definition>

Q: <question or key term>
A: <answer or definition>

...repeat for all 10 flashcards.

DO NOT write anything before the first Q:.
DO NOT write anything after the last A:.
DO NOT number the cards.
DO NOT include document text directly.

Study material:
{text}""")
                ]

                response = llm.invoke(messages)
                raw = response.content
                cards = _parse_flashcards(raw)

                if cards:
                    st.session_state.flashcards = cards
                    st.rerun()
                else:
                    st.error("❌ Could not parse. Raw LLM output:")
                    st.code(raw[:1000])

    cards = st.session_state.get("flashcards", [])
    if not cards:
        return

    current = st.session_state.get("current_card", 0)
    flipped = st.session_state.get("card_flipped", False)

    with col2:
        if st.button("🔄 New Set", use_container_width=True):
            st.session_state.flashcards = []
            st.session_state.current_card = 0
            st.session_state.card_flipped = False
            st.rerun()

    # Progress
    progress = (current + 1) / len(cards)
    st.markdown(f"""
        <div style="text-align:center; color:#94a3b8; font-weight:600; margin:12px 0 8px;">
            Card {current + 1} of {len(cards)}
        </div>
        <div style="background:rgba(255,255,255,0.06); border-radius:50px; height:6px; margin-bottom:20px;">
            <div style="background:linear-gradient(90deg,#6366f1,#a78bfa);
                width:{int(progress * 100)}%; height:100%; border-radius:50px;"></div>
        </div>
    """, unsafe_allow_html=True)

    # Card display
    card = cards[current]
    if not flipped:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.10));
                border: 2px solid rgba(99,102,241,0.45);
                border-radius: 20px; padding: 50px 40px;
                text-align: center; min-height: 200px; margin-bottom: 20px;">
                <div style="font-size:0.75rem; font-weight:700; letter-spacing:2px;
                    color:#818cf8; text-transform:uppercase; margin-bottom:16px;">❓ Question</div>
                <div style="font-size:1.2rem; font-weight:600; color:#e2e8f0; line-height:1.6;">
                    {card['front']}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(6,182,212,0.08));
                border: 2px solid rgba(16,185,129,0.45);
                border-radius: 20px; padding: 50px 40px;
                text-align: center; min-height: 200px; margin-bottom: 20px;">
                <div style="font-size:0.75rem; font-weight:700; letter-spacing:2px;
                    color:#10b981; text-transform:uppercase; margin-bottom:16px;">✅ Answer</div>
                <div style="font-size:1.1rem; color:#e2e8f0; line-height:1.7;">
                    {card['back']}
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Navigation
    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(current == 0)):
            st.session_state.current_card = current - 1
            st.session_state.card_flipped = False
            st.rerun()
    with nav2:
        label = "👁️ Show Answer" if not flipped else "🔄 Show Question"
        if st.button(label, use_container_width=True):
            st.session_state.card_flipped = not flipped
            st.rerun()
    with nav3:
        if st.button("Next ➡️", use_container_width=True, disabled=(current == len(cards) - 1)):
            st.session_state.current_card = current + 1
            st.session_state.card_flipped = False
            st.rerun()

    # All cards list
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    with st.expander("📋 View All Cards"):
        for idx, c in enumerate(cards):
            bg = "rgba(99,102,241,0.12)" if idx == current else "rgba(255,255,255,0.02)"
            border = "rgba(99,102,241,0.5)" if idx == current else "rgba(255,255,255,0.07)"
            st.markdown(f"""
                <div style="background:{bg}; border:1px solid {border};
                    border-radius:10px; padding:12px 16px; margin-bottom:8px;">
                    <span style="font-size:0.75rem; color:#818cf8; font-weight:600;">Card {idx+1} · </span>
                    <span style="color:#e2e8f0; font-size:0.9rem;">{c['front']}</span>
                </div>
            """, unsafe_allow_html=True)
