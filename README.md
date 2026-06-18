# 📚 StudyMate AI - RAG-Powered Study Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://studymate-ai-rag-model.streamlit.app/)

**🚀 Live Demo:** [https://studymate-ai-rag-model.streamlit.app/](https://studymate-ai-rag-model.streamlit.app/)

## Overview
An intelligent study companion using RAG (Retrieval-Augmented Generation) to help students learn from PDF study materials. Upload PDFs and interact through AI-powered chat, summaries, quizzes, and flashcards.

## ✨ Features
- 💬 **Multi-PDF Chat** - Ask questions about your documents in natural language
- 📝 **Smart Summarizer** - Generate structured summaries with key concepts
- 🧠 **Quiz Generator** - Create MCQs with instant scoring
- 🃏 **Flashcards** - Auto-generate Q&A cards for active recall

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **LLM**: Groq (Llama 3.1), LangChain
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector DB**: FAISS
- **PDF Processing**: pypdf
- **Auth**: SQLite + bcrypt

## 🏗️ Architecture
```
PDFs → Text Extraction → Chunking → Embedding → FAISS Vector Store → RAG Chain
```

## 📦 Installation

1. **Clone repository**
```bash
git clone https://github.com/divyadoredla/StudyMate-AI-RAG-Model.git
cd StudyMate-AI-RAG-Model
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API key**
```bash
cp .env.example .env
# Add your Groq API key to .env file
# Get free key from: https://console.groq.com
```

4. **Run the app**
```bash
streamlit run app.py
```

## 🚀 Usage
1. Sign up and login
2. Upload PDF files in the sidebar
3. Click "Process PDFs" 
4. Start chatting or use other features (Summarizer, Quiz, Flashcards)

## 📁 Project Structure
```
├── app.py              # Main application
├── auth.py             # Authentication
├── database.py         # User database
├── pdf_loader.py       # PDF text extraction
├── text_splitter.py    # Text chunking
├── embeddings.py       # Embedding model
├── vector_store.py     # FAISS vector store
├── rag_chain.py        # RAG conversational chain
├── summarizer.py       # Summary generation
├── quiz_generator.py   # Quiz creation
├── flashcards.py       # Flashcard generator
└── htmlTemplates.py    # CSS styling
```

## 🔑 Key Concepts
**RAG (Retrieval-Augmented Generation)**: Combines document retrieval with LLM generation to provide accurate, grounded answers from your specific documents.

**Why FAISS?** Fast similarity search optimized for dense vectors.

**Why Groq?** Free tier, 10x faster than OpenAI, no cold starts.

## 👨‍💻 Author
Created with ❤️ by **Doredla Divya Sri** © 2026

📧 divyadoredla24@gmail.com

## 🙏 Acknowledgments
LangChain • Groq • Sentence Transformers • Streamlit
