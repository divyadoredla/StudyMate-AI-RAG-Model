# 📚 StudyMate AI - RAG-Powered Study Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://studymate-ai-rag-model.streamlit.app/)

## 🚀 Live Demo
**Try it now:** [https://studymate-ai-rag-model.streamlit.app/](https://studymate-ai-rag-model.streamlit.app/)

## Overview
StudyMate AI is an intelligent study companion that leverages RAG (Retrieval-Augmented Generation) architecture to help students learn from their PDF study materials. Upload multiple PDFs (lecture notes, textbooks, etc.) and interact with them through AI-powered chat, summaries, quizzes, and flashcards.

## 🎯 Key Features

### 1. **Multi-PDF Chat** 💬
- Upload multiple PDF documents simultaneously
- Ask questions about your study material in natural language
- Get contextually relevant answers backed by your documents
- Maintains conversation history for follow-up questions

### 2. **Smart Summarizer** 📝
- Generates structured summaries of uploaded documents
- Organized with key concepts, definitions, and review points
- Perfect for quick revision before exams

### 3. **Quiz Generator** 🧠
- Creates multiple-choice questions from your content
- Interactive quiz interface with instant scoring
- Shows correct answers with explanations
- Helps test knowledge retention

### 4. **Flashcards** 🃏
- Auto-generates Q&A flashcards from study material
- Interactive flip cards for active recall practice
- Progress tracking through card sets

## 🏗️ Technical Architecture

### RAG Pipeline (5 Stages)

```
PDFs → Text Extraction → Chunking → Embedding → Vector Store → RAG Chain
```

**Stage 1-2: PDF Loading** (`pdf_loader.py`)
- Extracts text from uploaded PDFs using `pypdf`
- Handles multiple files and corrupted PDFs gracefully
- Provides metadata extraction for source citation

**Stage 3: Text Chunking** (`text_splitter.py`)
- Splits large text into overlapping chunks (1000 chars, 200 overlap)
- Uses `RecursiveCharacterTextSplitter` for semantic boundaries
- Optimal chunk size for embedding quality

**Stage 4: Embeddings** (`embeddings.py`)
- Converts text to 384-dim vectors using `all-MiniLM-L6-v2`
- Free, local model (no API costs)
- Normalizes embeddings for cosine similarity

**Stage 5: Vector Store** (`vector_store.py`)
- Uses FAISS for efficient similarity search
- In-memory index with persistence support
- Returns top-k most relevant chunks per query

**RAG Chain** (`rag_chain.py`)
- Custom conversational chain using Groq's free LLM
- Combines retrieved context + chat history
- Llama-3.1-8b-instant for fast, accurate responses

## 🛠️ Tech Stack

### Core Framework
- **Streamlit** - Web UI and session management
- **Python 3.8+** - Backend language

### LLM & NLP
- **LangChain** - RAG pipeline orchestration
- **Groq** - Free LLM API (Llama 3.1)
- **Sentence Transformers** - Local embeddings
- **HuggingFace** - Model hub integration

### Vector Database
- **FAISS** - Fast similarity search (Facebook AI)

### PDF Processing
- **pypdf** - Modern PDF text extraction

### Authentication
- **SQLite** - User database
- **bcrypt** - Password hashing

### Environment
- **python-dotenv** - API key management

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Groq API key (free from https://console.groq.com)

### Setup Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd StudyMate-AI-RAG-Model
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API keys**
```bash
cp .env.example .env
# Edit .env and add your Groq API key:
# GROQ_API_KEY=your_groq_api_key_here
```

5. **Run the application**
```bash
streamlit run app.py
```

6. **Open in browser**
```
Navigate to http://localhost:8501
```

## 🚀 Usage Guide

### First Time Setup
1. Launch the app and create an account (Sign Up)
2. Login with your credentials

### Using the Chat Feature
1. Click "Upload PDFs" in sidebar
2. Select one or more PDF files (study notes, textbooks)
3. Click "⚡ Process PDFs" and wait for indexing
4. Ask questions in the chat interface
5. Get AI-powered answers from your documents

### Using Other Features
- **Summarizer**: Process PDFs first, then switch to Summarizer tab
- **Quiz**: Generates MCQs automatically from your content
- **Flashcards**: Creates Q&A cards for active recall practice

## 📁 Project Structure

```
├── app.py                  # Main Streamlit application entry point
├── auth.py                 # User authentication (login/signup)
├── database.py             # SQLite user database management
├── pdf_loader.py           # PDF text extraction (Stage 1-2)
├── text_splitter.py        # Text chunking logic (Stage 3)
├── embeddings.py           # Embedding model setup (Stage 4)
├── vector_store.py         # FAISS vector store (Stage 5)
├── rag_chain.py            # RAG conversational chain
├── summarizer.py           # Smart summary generation
├── quiz_generator.py       # MCQ quiz creation
├── flashcards.py           # Flashcard generator
├── htmlTemplates.py        # CSS styling and templates
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
└── app.db                  # SQLite database (auto-created)
```

## 🔐 Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **Session Management**: Streamlit session state for auth persistence
- **Environment Variables**: API keys stored securely in .env (not committed)
- **Input Validation**: Sanitized user inputs to prevent injection

## 🎓 RAG Concepts (Interview Ready)

### What is RAG?
**Retrieval-Augmented Generation** combines document retrieval with LLM generation. Instead of relying solely on the LLM's training data, RAG retrieves relevant information from your documents and uses it as context for generating answers.

**Benefits:**
- Reduces hallucinations (LLM making up facts)
- Grounds answers in your specific documents
- More accurate than pure LLM or pure search

### Why FAISS?
FAISS (Facebook AI Similarity Search) enables sub-linear time similarity search over dense vectors using approximate nearest neighbor algorithms. For our use case (<50k chunks), it provides exact search with BLAS-optimized performance.

### Why all-MiniLM-L6-v2?
- 384 dimensions (compact, fast)
- 22MB model size (runs locally)
- Zero API costs
- 58.8 STSB benchmark score (excellent semantic understanding)
- Free alternative to OpenAI embeddings

### Why Groq?
- **Free tier** with generous limits
- **Fast inference** (10x faster than OpenAI)
- Llama 3.1 8B model with strong performance
- No cold starts

## 🔧 Performance Optimization

- **Chunking**: 1000 chars with 200 overlap balances context vs precision
- **Retrieval**: Returns top-4 chunks (adjustable via k parameter)
- **Embeddings**: Batch processing with GPU support option
- **Caching**: FAISS index persistence prevents re-processing

## 🐛 Common Issues & Solutions

**Issue**: "No text extracted from PDF"
- **Cause**: Image-based (scanned) PDFs
- **Solution**: Use PDFs with selectable text, or add OCR support

**Issue**: Slow first run
- **Cause**: Downloading embedding model (22MB)
- **Solution**: Normal behavior, subsequent runs load from cache

**Issue**: "GROQ_API_KEY not found"
- **Cause**: Missing .env file
- **Solution**: Copy .env.example to .env and add your API key

## 📊 Scalability

- **Current**: Handles ~100 PDFs, ~10,000 chunks efficiently
- **CPU**: 15 seconds to embed 1000 chunks
- **GPU**: Can accelerate by changing device="cuda" in embeddings.py
- **Memory**: ~200MB for FAISS index with 10k chunks

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- OCR support for scanned PDFs
- Multi-language support
- Export features (study guides, notes)
- Mobile responsive design
- Progress tracking & analytics

## 👨‍💻 Author

Doredla Divya Sri
divyadoredla24@gmail.com

## 🙏 Acknowledgments

- LangChain for RAG framework
- Groq for free LLM access
- Sentence Transformers for embeddings
- Streamlit for rapid prototyping
