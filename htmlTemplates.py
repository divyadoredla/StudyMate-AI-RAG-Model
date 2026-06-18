css = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ===== GLOBAL BASE ===== */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
}

/* ===== MAIN BACKGROUND ===== */
.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #111827 40%, #0d1117 100%) !important;
    min-height: 100vh;
}

/* ===== ALL GLOBAL TEXT — light by default on dark bg ===== */
body, p, span, div, label, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stText, [class*="css"] {
    color: #e2e8f0;
}

/* ===== HEADERS — gradient ===== */
h1, h2, h3 {
    background: linear-gradient(90deg, #818cf8, #a78bfa, #c084fc) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-weight: 700 !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: rgba(15, 15, 30, 0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div { color: #e2e8f0 !important; }

/* ===== INPUT FIELDS — dark background, clearly visible text ===== */
input[type="text"],
input[type="password"],
input[type="email"],
textarea,
.stTextInput input,
.stTextArea textarea,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    border: 1.5px solid #334155 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    caret-color: #818cf8 !important;
}

input[type="text"]::placeholder,
input[type="password"]::placeholder,
textarea::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

input[type="text"]:focus,
input[type="password"]:focus,
textarea:focus,
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
    outline: none !important;
}

/* ===== LABELS above inputs ===== */
.stTextInput label,
.stTextArea label,
label[data-testid="stWidgetLabel"] {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    -webkit-text-fill-color: #94a3b8 !important;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 10px 24px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.55) !important;
    background: linear-gradient(135deg, #818cf8, #a78bfa) !important;
}

/* ===== FORM SUBMIT BUTTON ===== */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #10b981, #06b6d4) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(16,185,129,0.35) !important;
    width: 100% !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    border: none !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    box-shadow: 0 8px 25px rgba(16,185,129,0.55) !important;
    background: linear-gradient(135deg, #34d399, #22d3ee) !important;
    transform: translateY(-2px) !important;
}

/* ===== FILE UPLOADER ===== */
[data-testid="stFileUploader"] {
    background: rgba(30,41,59,0.6) !important;
    border: 2px dashed rgba(99,102,241,0.4) !important;
    border-radius: 14px !important;
    padding: 12px !important;
}
/* Text inside uploader is visible on dark bg */
[data-testid="stFileUploader"] *,
[data-testid="stFileDropzoneInstructions"] * {
    color: #cbd5e1 !important;
    -webkit-text-fill-color: #cbd5e1 !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(139,92,246,0.6) !important;
}

/* ===== UPLOADED FILE CHIP ===== */
[data-testid="stFileUploaderFile"] {
    background: rgba(30,41,59,0.8) !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploaderFile"] * {
    color: #e2e8f0 !important;
    -webkit-text-fill-color: #e2e8f0 !important;
}

/* ===== RADIO BUTTONS ===== */
.stRadio label, .stRadio span, .stRadio p {
    color: #cbd5e1 !important;
    -webkit-text-fill-color: #cbd5e1 !important;
    font-weight: 500 !important;
}

/* ===== CHAT MESSAGES ===== */
.chat-message {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 18px 22px;
    border-radius: 16px;
    margin-bottom: 16px;
    animation: fadeInUp 0.3s ease;
    border: 1px solid rgba(255,255,255,0.07);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.chat-message:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.chat-message.user {
    background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.15));
    border-color: rgba(99,102,241,0.3);
    flex-direction: row-reverse;
}
.chat-message.bot {
    background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(6,182,212,0.08));
    border-color: rgba(16,185,129,0.2);
}
.chat-message .avatar {
    flex-shrink: 0;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.chat-message.user .avatar { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
.chat-message.bot .avatar  { background: linear-gradient(135deg, #10b981, #06b6d4); }
.chat-message .message {
    flex: 1;
    color: #e2e8f0 !important;
    font-size: 0.95rem;
    line-height: 1.65;
    padding: 4px 0;
}
.chat-message.user .message { text-align: right; }

/* ===== ANIMATIONS ===== */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ===== ALERTS ===== */
.stSuccess { background: rgba(16,185,129,0.12) !important; border: 1px solid rgba(16,185,129,0.3) !important; border-radius: 10px !important; }
.stWarning { background: rgba(245,158,11,0.12) !important; border: 1px solid rgba(245,158,11,0.3) !important; border-radius: 10px !important; }
.stError   { background: rgba(239,68,68,0.12) !important;  border: 1px solid rgba(239,68,68,0.3) !important;  border-radius: 10px !important; }

/* ===== DIVIDER ===== */
hr { border-color: rgba(255,255,255,0.08) !important; margin: 20px 0 !important; }

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.7); }

/* ===== MAIN CONTENT ===== */
.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 900px !important;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">🤖</div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">👤</div>
    <div class="message">{{MSG}}</div>
</div>
'''
