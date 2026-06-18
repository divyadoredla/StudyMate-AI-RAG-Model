import streamlit as st
import database


def show_auth_page():
    # Hero Header
    st.markdown("""
        <div style="text-align: center; padding: 40px 20px 20px;">
            <div style="font-size: 56px; margin-bottom: 12px;">📚</div>
            <h1 style="font-size: 2.6rem; font-weight: 800; margin-bottom: 8px;">StudyMate AI</h1>
            <p style="color: #94a3b8; font-size: 1.05rem; max-width: 420px; margin: 0 auto;">
                Your intelligent study companion. Upload PDFs, ask questions, generate quizzes &amp; flashcards.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.write("")

    # Centered card layout
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        choice = st.radio("", ["🔐  Login", "✨  Sign Up"], horizontal=True, label_visibility="collapsed")

        st.write("")

        if "Sign Up" in choice:
            st.markdown('<p style="color:#94a3b8; font-size:0.85rem; margin-bottom:4px;">Create your free account</p>', unsafe_allow_html=True)
            with st.form("signup_form"):
                new_user = st.text_input("Username", placeholder="Choose a username...")
                new_password = st.text_input("Password", type='password', placeholder="Create a strong password...")
                submit = st.form_submit_button("🚀  Create Account")

                if submit:
                    if new_user and new_password:
                        if len(new_password) < 6:
                            st.warning("⚠️ Password must be at least 6 characters.")
                        else:
                            success = database.add_user(new_user, new_password)
                            if success:
                                st.success("✅ Account created! Switch to Login to get started.")
                            else:
                                st.error("❌ Username already taken. Try a different one.")
                    else:
                        st.warning("⚠️ Please fill in all fields.")

        else:
            st.markdown('<p style="color:#94a3b8; font-size:0.85rem; margin-bottom:4px;">Welcome back!</p>', unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username...")
                password = st.text_input("Password", type='password', placeholder="Enter your password...")
                submit = st.form_submit_button("🔓  Login")

                if submit:
                    if username and password:
                        if database.verify_user(username, password):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.success("✅ Login successful! Loading your workspace...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password.")
                    else:
                        st.warning("⚠️ Please fill in all fields.")

    # Feature highlights at bottom
    st.write("")
    st.markdown("---")
    st.markdown("""
        <div style="display:flex; justify-content:center; gap:32px; flex-wrap:wrap; padding: 16px 0;">
            <div style="text-align:center; color:#94a3b8;">
                <div style="font-size:24px;">💬</div>
                <div style="font-size:0.8rem; margin-top:4px;">Multi-PDF Chat</div>
            </div>
            <div style="text-align:center; color:#94a3b8;">
                <div style="font-size:24px;">📝</div>
                <div style="font-size:0.8rem; margin-top:4px;">Smart Summaries</div>
            </div>
            <div style="text-align:center; color:#94a3b8;">
                <div style="font-size:24px;">🧠</div>
                <div style="font-size:0.8rem; margin-top:4px;">Quiz Generator</div>
            </div>
            <div style="text-align:center; color:#94a3b8;">
                <div style="font-size:24px;">🃏</div>
                <div style="font-size:0.8rem; margin-top:4px;">Flashcards</div>
            </div>
            <div style="text-align:center; color:#94a3b8;">
                <div style="font-size:24px;">🔍</div>
                <div style="font-size:0.8rem; margin-top:4px;">Source Citation</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
