import re
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama

from app.vectorstore import get_text_splitter, get_vectorstore, processed_documents
from app.config import settings

chat_histories = {}  # In-memory chat history per collection

def sanitize_filename(filename: str) -> str:
    """
    Sanitize the filename to create a valid collection ID.
    Replaces non-alphanumeric characters with underscores
    """
    base = os.path.splitext(filename)[0]
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', base)
    clean = re.sub(r'_+', '_', clean.lower())
    return clean

def process_pdf(file_path: str, original_filename: str) -> dict:
    """
    Process the uploaded PDF file, split it into chunks,
    and store it in the vectorstore.
    """
    collection_id = sanitize_filename(original_filename)

    if collection_id in processed_documents:
        return {"status": "error", "message": "Document already processed"}

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # validation for if image or no text
    # If no documents or all documents have empty page content, return an error
    # This will handle as future enhancements for image-based PDFs
    # This project does not currently support OCR or image extraction because it requires additional libraries and resources 
    # due to the complexity of image processing and Hardware requirements.
    # As per assessment requirements for Applab Qatar, We only handle text-based PDFs for Chatbot functionality.

    if not documents or all(not doc.page_content.strip() for doc in documents):
        return {
            "status": "error",
            "message": "PDF may be image-based or has no extractable text as per assessment requirements. We currently only support text-based PDFs.It is recommended to use text-based PDFs for the chatbot functionality.Currently, we do not support OCR or image extraction due to the complexity and hardware requirements."
        }

    splitter = get_text_splitter()
    split_docs = splitter.split_documents(documents)

    store = get_vectorstore(collection_id)
    store.add_documents(split_docs)
    
    processed_documents.add(collection_id)

    return {
        "status": "success",
        "message": "PDF processed successfully",
        "collection_name": collection_id
    }

def format_docs(docs) -> str:
    """Format the retrieved documents into a single string for context.
    This function concatenates the page content of each document.
    """
    return "\n\n".join(doc.page_content for doc in docs)

def get_response(question: str, collection_name: str) -> str:
    """
    Generate a response to the user's question based on the provided document collection.
    If the collection does not exist or has no relevant documents, return an error message.
    """
    if collection_name not in processed_documents:
        return "Error: Document not found. Please re-upload it."

    vectorstore = get_vectorstore(collection_name)
    retriever = vectorstore.as_retriever()
    relevant_docs = retriever.invoke(question)

    if not relevant_docs:
        return "Sorry, I couldn't find anything related. Please try re-uploading the document."

    context = format_docs(relevant_docs)
    history = chat_histories.get(collection_name, [])[-6:]
    history_text = "\n".join(f"User: {q}\nAssistant: {a}" for q, a in history)

    prompt_template = (
        "You are a helpful and professional assistant designed to answer questions based on PDF documents."
        " Use only the information provided in the context to answer clearly and accurately."
        " If the answer is not in the context, respond politely or suggest what the user can try next.\n\n"
        "Context:\n{context}\n\n"
        "{history}\n\n"
        "Question:\n{question}\n\n"
        "Answer:"
    )

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question", "history"]
    )

    llm = Ollama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.5
    )

    response = llm.invoke(
        prompt.format(context=context, question=question, history=history_text)
    ).strip()

    chat_histories.setdefault(collection_name, []).append((question, response))

    return response
