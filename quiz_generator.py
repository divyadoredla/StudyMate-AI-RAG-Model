"""
quiz_generator.py — Interactive Quiz Generator
Generates 5 multiple-choice questions from uploaded PDF content.
"""

import re
import streamlit as st
from langchain_groq import ChatGroq


def _get_llm():
    return ChatGroq(model="llama-3.1-8b-instant", temperature=0.5)


def _parse_quiz(raw: str) -> list[dict]:
    """
    Robust parser: splits on '---' delimiters and extracts fields.
    Falls back to line-by-line parsing if delimiters not found.
    """
    questions = []

    # Split on --- delimiter
    blocks = [b.strip() for b in raw.split("---") if b.strip()]

    for block in blocks:
        if not block:
            continue
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if len(lines) < 3:
            continue

        q = {"question": "", "options": {}, "correct": "", "explanation": ""}

        for line in lines:
            # Question line
            if re.match(r'^(?:Q(?:UESTION)?[\s\d]*[:.\-]?|^\d+[\.\)])\s*', line, re.IGNORECASE) and not q["question"]:
                text = re.sub(r'^(?:Q(?:UESTION)?[\s\d]*[:.\-]?|\d+[\.\)])\s*', '', line, flags=re.IGNORECASE).strip()
                if text:
                    q["question"] = text
            # Option lines A) B) C) D)
            elif re.match(r'^[A-D][)\.\:]\s+', line):
                key = line[0].upper()
                val = line[2:].strip() if line[1] in ').:' else line[3:].strip()
                q["options"][key] = val
            # Correct answer
            elif re.match(r'^(?:ANSWER|CORRECT|ANS)[:\s]+', line, re.IGNORECASE):
                ans = re.sub(r'^(?:ANSWER|CORRECT|ANS)[:\s]+', '', line, flags=re.IGNORECASE).strip()
                q["correct"] = ans[0].upper() if ans else ""
            # Explanation
            elif re.match(r'^(?:EXPLAIN(?:ATION)?|REASON)[:\s]+', line, re.IGNORECASE):
                q["explanation"] = re.sub(r'^(?:EXPLAIN(?:ATION)?|REASON)[:\s]+', '', line, flags=re.IGNORECASE).strip()
            # If question still empty, first meaningful line is the question
            elif not q["question"] and len(line) > 10:
                q["question"] = line

        # Only add if we have a question and at least 2 options
        if q["question"] and len(q["options"]) >= 2:
            # If no correct answer found, default to A
            if not q["correct"]:
                q["correct"] = "A"
            questions.append(q)

    return questions[:5]


def run_quiz_feature():
    st.markdown("""
        <div style="margin-bottom:24px;">
            <h1 style="font-size:2rem; margin-bottom:6px;">🧠 Quiz Generator</h1>
            <p style="color:#94a3b8; font-size:0.95rem;">
                Test your knowledge with AI-generated multiple choice questions from your notes.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("raw_text"):
        st.markdown("""
            <div style="text-align:center; padding:60px 20px; color:#94a3b8;">
                <div style="font-size:56px; margin-bottom:16px;">🧠</div>
                <h3 style="color:#e2e8f0; margin-bottom:8px;">No Documents Loaded</h3>
                <p>Upload and process your PDFs in the sidebar first, then generate a quiz.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    # ── Controls ──────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🎯 Generate New Quiz", use_container_width=True):
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False

            with st.spinner("🧠 Generating quiz questions..."):
                text = st.session_state.raw_text[:5000]
                llm = _get_llm()
                prompt = f"""Create 5 multiple choice questions from this document. 
Use EXACTLY this format with --- as separator between questions:

---
QUESTION: <question text here>
A) <first option>
B) <second option>
C) <third option>
D) <fourth option>
ANSWER: <just the letter, e.g. B>
EXPLANATION: <one sentence why>
---
QUESTION: <next question>
A) ...
B) ...
C) ...
D) ...
ANSWER: ...
EXPLANATION: ...
---

Important: Use exactly this format. Separate each question with ---. 
Generate 5 questions total based on this document:

{text}"""
                response = llm.invoke(prompt)
                raw = response.content

                questions = _parse_quiz(raw)

                if questions:
                    st.session_state.quiz_questions = questions
                else:
                    st.error("❌ Could not parse quiz. Raw output below — please report this:")
                    st.code(raw[:500])

    with col2:
        if st.session_state.get("quiz_questions") and not st.session_state.get("quiz_submitted"):
            if st.button("✅ Submit Quiz", use_container_width=True):
                st.session_state.quiz_submitted = True
                st.rerun()

    # ── Quiz Display ──────────────────────────────────────────
    questions = st.session_state.get("quiz_questions", [])
    if not questions:
        return

    submitted = st.session_state.get("quiz_submitted", False)
    answers = st.session_state.get("quiz_answers", {})

    if submitted:
        score = sum(1 for i, q in enumerate(questions) if answers.get(i) == q["correct"])
        total = len(questions)
        pct = int(score / total * 100)
        color = "#10b981" if pct >= 60 else "#f59e0b" if pct >= 40 else "#ef4444"
        grade = "🏆 Excellent!" if pct >= 80 else "👍 Good job!" if pct >= 60 else "📚 Keep studying!"
        st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(16,185,129,0.12),rgba(6,182,212,0.08));
                border:2px solid {color}; border-radius:16px; padding:28px; text-align:center; margin-bottom:20px;">
                <div style="font-size:3rem; font-weight:800; color:{color};">{score}/{total}</div>
                <div style="color:#94a3b8; font-size:1rem; margin-top:6px;">{pct}% · {grade}</div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Try Again", use_container_width=True):
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.rerun()

    st.markdown("---")

    for i, q in enumerate(questions):
        user_ans = answers.get(i)
        is_correct = user_ans == q["correct"]
        border = "#10b981" if (submitted and is_correct) else "#ef4444" if (submitted and user_ans) else "rgba(99,102,241,0.3)"

        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03); border:1px solid {border};
                border-radius:14px; padding:20px 24px; margin-bottom:8px;">
                <p style="font-weight:600; color:#e2e8f0; margin:0; font-size:1rem;">
                    Q{i+1}. {q['question']}
                </p>
            </div>
        """, unsafe_allow_html=True)

        if not submitted:
            option_keys = sorted(q["options"].keys())
            chosen = st.radio(
                f"q{i}",
                option_keys,
                format_func=lambda k, q=q: f"{k}) {q['options'].get(k, '')}",
                key=f"quiz_radio_{i}",
                label_visibility="collapsed"
            )
            st.session_state.quiz_answers[i] = chosen
        else:
            for key in sorted(q["options"].keys()):
                val = q["options"][key]
                if key == q["correct"]:
                    icon, style = "✅", "color:#10b981; font-weight:600;"
                elif key == user_ans:
                    icon, style = "❌", "color:#ef4444;"
                else:
                    icon, style = "  ·", "color:#64748b;"
                st.markdown(f'<p style="{style} margin:4px 0 4px 16px;">{icon} {key}) {val}</p>', unsafe_allow_html=True)

            if q.get("explanation"):
                st.markdown(f"""
                    <div style="background:rgba(99,102,241,0.08); border-left:3px solid #6366f1;
                        padding:8px 14px; border-radius:6px; margin:8px 0 4px 0;
                        color:#94a3b8; font-size:0.88rem;">
                        💡 {q['explanation']}
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
