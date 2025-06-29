from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings

processed_documents = set()

def get_embeddings():
    """
    Initialize the embedding model from Ollama.
    """
    return OllamaEmbeddings(
        model=settings.EMBEDDING_MODEL,
        base_url=settings.OLLAMA_BASE_URL
    )

def get_vectorstore(collection_name: str):
    """
    Get a persistent Chroma vector store for the given collection.
    Persistence is handled automatically by Chroma
    """
    return Chroma(
        collection_name=collection_name,
        persist_directory=settings.VECTOR_DB_PATH,
        embedding_function=get_embeddings()
    )

def get_text_splitter():
    """
    Create a text splitter instance for breaking up long PDF content.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
