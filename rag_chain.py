"""
rag_chain.py  —  RAG pipeline: retrieval + Groq LLM (FREE)
"""

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage


class ConversationalChain:
    """
    Custom conversational chain using Groq (free) + FAISS retriever.
    """

    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        self.chat_history = []

    def __call__(self, inputs: dict) -> dict:
        question = inputs["question"]

        # Build history string
        history_str = ""
        for msg in self.chat_history:
            role = "Student" if isinstance(msg, HumanMessage) else "StudyMate AI"
            history_str += f"{role}: {msg.content}\n"

        # Retrieve relevant chunks from FAISS
        source_docs = self.retriever.invoke(question)
        context = "\n\n".join(doc.page_content for doc in source_docs)

        # Build prompt
        prompt = f"""You are StudyMate AI, an intelligent academic assistant helping students study.

Use the context below from the student's uploaded documents to answer the question.
If the context has relevant information, use it to give a detailed answer.
If the context does not fully cover the question, use your general knowledge to help,
but mention that the answer is based on general knowledge.

Context from uploaded documents:
{context}

Previous conversation:
{history_str}
Student's Question: {question}

Give a clear, well-structured answer with:
- A brief definition or direct answer first
- Then details, steps, or explanation
- Use numbered lists for steps, bullet points for features/properties

Answer:"""

        # Call Groq
        response = self.llm.invoke(prompt)
        answer = response.content

        # Update history
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))

        return {
            "answer": answer,
            "chat_history": self.chat_history,
            "source_documents": source_docs,
        }


def get_conversation_chain(vectorstore):
    """
    Returns a ConversationalChain using Groq's free Llama 3 model.
    GROQ_API_KEY must be set in .env
    """
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 6},
    )

    return ConversationalChain(llm=llm, retriever=retriever)
