"""
app.py  —  Main Streamlit application entry point
──────────────────────────────────────────────────
WHAT THIS FILE DOES:
  Wires together all modules into a working Streamlit web app.
  Handles session state, routing between features, and the chat UI.

HOW STREAMLIT SESSION STATE WORKS:
  Streamlit reruns the entire app.py script on EVERY user interaction
  (button click, input change, form submit). Session state is the
  mechanism that persists data across these reruns.

  st.session_state is a dictionary-like object that lives as long as
  the browser tab is open. We store:
    - logged_in: bool — whether the user has authenticated
    - username: str — the logged-in user's name
    - conversation: ConversationalRetrievalChain — the active RAG chain
    - chat_history: list[Message] — all Q&A pairs from this session
    - processed_files: list[str] — filenames of uploaded PDFs

  Without session state, every interaction would reset the conversation
  and require re-uploading PDFs.

RUNNING THE APP:
  1. Create .env file:
       GOOGLE_API_KEY=your_gemini_api_key_here
  2. Install dependencies:
       pip install -r requirements.txt
  3. Run:
       streamlit run app.py
  4. Open http://localhost:8501 in your browser
"""

import streamlit as st
from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# Internal modules
import database
import auth
from pdf_loader import get_pdf_text
from text_splitter import get_text_chunks
from vector_store import build_vectorstore
from rag_chain import get_conversation_chain
from htmlTemplates import css, bot_template, user_template

from summarizer import run_summarizer_feature
from quiz_generator import run_quiz_feature
from flashcards import run_flashcards_feature


def initialize_session_state():
    """
    Initializes all session state variables with default values.

    WHY A FUNCTION INSTEAD OF INLINE CHECKS?
    Centralizing initialization makes it easy to add new state variables
    as we build Phase 5-7. Call this once at the top of main().
    """
    defaults = {
        "logged_in": False,
        "username": None,
        "conversation": None,
        "chat_history": [],
        "processed_files": [],
        "is_processing": False,
        # Summarizer
        "raw_text": "",
        "summary": None,
        # Quiz
        "quiz_questions": [],
        "quiz_answers": {},
        "quiz_submitted": False,
        # Flashcards
        "flashcards": [],
        "current_card": 0,
        "card_flipped": False,
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def handle_user_question(user_question: str):
    """
    Called when the user submits a question through the chat form.

    FLOW:
      1. Validate that PDFs have been processed (conversation chain exists)
      2. Call the RAG chain with the question
      3. Extract the chat history from the response
      4. Rerun the app so the new messages render immediately

    Args:
        user_question: The question text the user typed.
    """
    if st.session_state.conversation is None:
        st.warning(
            "⚠️ Please upload your PDFs and click **Process** first, "
            "then ask your question."
        )
        return

    with st.spinner("🔍 Searching your documents..."):
        # The chain returns a dict with keys:
        #   "answer"            — Gemini's response string
        #   "chat_history"      — Updated list of Message objects
        #   "source_documents"  — The retrieved chunks (for Phase 4)
        response = st.session_state.conversation({"question": user_question})

    st.session_state.chat_history = response["chat_history"]

    # Optionally store source documents for Phase 4 (Source Citation)
    # st.session_state.source_docs = response.get("source_documents", [])

    # Force Streamlit to rerun so the new messages appear immediately
    st.rerun()


def format_message(text: str) -> str:
    """Converts LLM markdown output to HTML for proper rendering in chat bubbles."""
    import re
    lines = text.split("\n")
    html_lines = []
    in_ul = False
    in_ol = False

    for line in lines:
        stripped = line.strip()
        ol_match = re.match(r'^(\d+)[\.\)] (.+)', stripped)
        ul_match = re.match(r'^[-\*•] (.+)', stripped)

        if ol_match:
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            if not in_ol:
                html_lines.append('<ol style="margin:8px 0 8px 20px; padding:0;">')
                in_ol = True
            html_lines.append(f'<li style="margin-bottom:4px;">{ol_match.group(2)}</li>')
        elif ul_match:
            if in_ol:
                html_lines.append("</ol>")
                in_ol = False
            if not in_ul:
                html_lines.append('<ul style="margin:8px 0 8px 20px; padding:0;">')
                in_ul = True
            html_lines.append(f'<li style="margin-bottom:4px;">{ul_match.group(1)}</li>')
        else:
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            if in_ol:
                html_lines.append("</ol>")
                in_ol = False
            if stripped == "":
                html_lines.append("<br>")
            else:
                formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
                formatted = re.sub(r'\*(.+?)\*', r'<em>\1</em>', formatted)
                html_lines.append(f'<p style="margin:4px 0;">{formatted}</p>')

    if in_ul:
        html_lines.append("</ul>")
    if in_ol:
        html_lines.append("</ol>")

    return "\n".join(html_lines)


def render_chat_history():
    """Renders all messages in chat_history as styled HTML bubbles."""
    if not st.session_state.chat_history:
        st.markdown("""
            <div style="text-align:center; padding:40px 0; color:#94a3b8;">
                <div style="font-size:48px; margin-bottom:12px;">📚</div>
                <p>Upload your PDFs in the sidebar and click <strong>Process</strong>.<br>
                Then ask anything about your study material!</p>
            </div>
        """, unsafe_allow_html=True)
        return

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            # Human message — plain text
            st.write(
                user_template.replace("{{MSG}}", message.content),
                unsafe_allow_html=True
            )
        else:
            # AI message — convert markdown to HTML first
            formatted = format_message(message.content)
            st.write(
                bot_template.replace("{{MSG}}", formatted),
                unsafe_allow_html=True
            )



def render_sidebar_uploader():
    """
    Renders the PDF upload section in the sidebar.
    Handles file processing and vectorstore creation.

    PROCESSING FLOW:
      1. User uploads PDF files via st.file_uploader
      2. User clicks "Process"
      3. We extract text, chunk it, embed it, and build FAISS index
      4. We create the conversational RAG chain and store it in session state
      5. User can now ask questions
    """
    with st.sidebar:
        # Welcome section
        st.markdown(f"""
            <div style="padding:16px 0 8px; text-align:center;">
                <div style="font-size:36px;">👋</div>
                <div style="font-weight:700; color:#e2e8f0; margin-top:6px;">Welcome back,</div>
                <div style="font-weight:800; font-size:1.1rem; background:linear-gradient(90deg,#818cf8,#a78bfa);
                     -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                    {st.session_state.username}
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # File uploader
        st.subheader("📁 Your Documents")
        pdf_docs = st.file_uploader(
            "Upload PDFs (DBMS, OS, CN, DSA notes...)",
            accept_multiple_files=True,
            type=["pdf"],    # Restrict to PDFs only
        )

        # Process button
        if st.button("⚡ Process PDFs", use_container_width=True):
            if not pdf_docs:
                st.warning("Please upload at least one PDF first.")
            else:
                with st.spinner("Processing your documents..."):

                    # Step 1: Extract text from all PDFs
                    st.write("📖 Extracting text...")
                    raw_text = get_pdf_text(pdf_docs)

                    if not raw_text.strip():
                        st.error(
                            "❌ No text could be extracted. Your PDFs might be "
                            "image-based (scanned). Try using PDFs with selectable text."
                        )
                        return

                    # Store raw text for Summarizer / Quiz / Flashcards
                    st.session_state.raw_text = raw_text

                    # Clear previous feature outputs when new PDFs are uploaded
                    st.session_state.summary = None
                    st.session_state.quiz_questions = []
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.session_state.flashcards = []
                    st.session_state.current_card = 0

                    # Step 2: Split text into chunks
                    st.write("✂️ Chunking text...")
                    text_chunks = get_text_chunks(raw_text)
                    st.write(f"   Created {len(text_chunks)} chunks")

                    # Step 3: Create vector store
                    st.write("🧠 Building vector index...")
                    vectorstore = build_vectorstore(text_chunks)

                    # Step 4: Create the RAG chain
                    st.write("🔗 Setting up RAG chain...")
                    st.session_state.conversation = get_conversation_chain(vectorstore)

                    # Track which files were processed
                    st.session_state.processed_files = [f.name for f in pdf_docs]

                    # Clear old chat history when new PDFs are uploaded
                    st.session_state.chat_history = []

                st.success(
                    f"✅ {len(pdf_docs)} PDF(s) processed successfully! "
                    "You can now ask questions."
                )

        # Show processed files
        if st.session_state.processed_files:
            st.markdown("**Loaded documents:**")
            for filename in st.session_state.processed_files:
                st.markdown(f"  📄 `{filename}`")

        st.markdown("---")

        # Navigation
        st.markdown(
            '<p style="color:#94a3b8; font-size:0.78rem; font-weight:600; '
            'letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;">Features</p>',
            unsafe_allow_html=True
        )
        feature_choice = st.radio("", [
            "💬  Multi-PDF Chat",
            "📝  Summarizer",
            "🧠  Quiz Generator",
            "🃏  Flashcards",
        ], label_visibility="collapsed")

        st.markdown("---")
            
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            # Clear all session state on logout
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    return feature_choice


def run_chat_feature():
    """
    Renders the main Multi-PDF Chat page.
    """
    st.markdown("""
        <div style="margin-bottom:24px;">
            <h1 style="font-size:2rem; margin-bottom:6px;">💬 Chat with your PDFs</h1>
            <p style="color:#94a3b8; font-size:0.95rem;">
                Upload your study notes in the sidebar, process them, then ask anything.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Render existing conversation
    render_chat_history()

    # Chat input form
    st.write("---")
    with st.form("chat_form", clear_on_submit=True):
        user_question = st.text_input(
            "Ask a question about your documents:",
            placeholder="e.g. What is the difference between B Tree and B+ Tree?"
        )
        submitted = st.form_submit_button("🚀 Ask")

    if submitted and user_question.strip():
        handle_user_question(user_question.strip())


def run_coming_soon(feature_name: str, icon: str):
    """
    Renders a placeholder page for features not yet implemented.
    Replace each call with the actual feature function as you build phases 4-7.
    """
    st.markdown(f"""
        <div style="text-align:center; padding:80px 20px;">
            <div style="font-size:72px; margin-bottom:20px;">{icon}</div>
            <h2 style="font-size:1.8rem; margin-bottom:12px;">{feature_name}</h2>
            <p style="color:#94a3b8; font-size:1rem; max-width:400px; margin:0 auto 24px;">
                Coming in the next phase! Process your PDFs first, then this feature
                will generate content from your uploaded documents.
            </p>
            <div style="display:inline-block; padding:8px 20px; border-radius:20px;
                 background:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.3);
                 color:#818cf8; font-size:0.85rem; font-weight:600;">
                🚧 Under Development
            </div>
        </div>
    """, unsafe_allow_html=True)


def main():
    """
    Entry point. Called every time Streamlit reruns the script.

    EXECUTION ORDER:
      1. Load environment variables (.env file → GOOGLE_API_KEY)
      2. Initialize SQLite database (creates tables if they don't exist)
      3. Configure Streamlit page settings
      4. Inject global CSS
      5. Initialize session state
      6. Route: auth page OR main app
    """
    # MUST be called before any LangChain/Gemini code runs
    load_dotenv()

    # Create users table if it doesn't exist
    database.init_db()

    # Page config — MUST be the first Streamlit call in the script
    st.set_page_config(
        page_title="StudyMate AI",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject the global dark theme CSS from htmlTemplates.py
    st.write(css, unsafe_allow_html=True)

    # Initialize session state variables with safe defaults
    initialize_session_state()

    # ── Routing ──────────────────────────────────────────────────────────────
    if not st.session_state.logged_in:
        # Show login/signup page
        auth.show_auth_page()
    else:
        # Show main app with sidebar navigation
        feature_choice = render_sidebar_uploader()

        if "Multi-PDF Chat" in feature_choice:
            run_chat_feature()
        elif "Summarizer" in feature_choice:
            run_summarizer_feature()
        elif "Quiz Generator" in feature_choice:
            run_quiz_feature()
        elif "Flashcards" in feature_choice:
            run_flashcards_feature()


if __name__ == "__main__":
    main()
