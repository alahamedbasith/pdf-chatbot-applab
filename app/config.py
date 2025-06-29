# If needed set the envronment variable for this file
# It is achieved through python-dotenv package and .env file
# For this assessment, we will use a simple configuration class

class Settings:
    OLLAMA_BASE_URL = "http://ollama:11434"
    OLLAMA_MODEL = "gemma3:1b"
    EMBEDDING_MODEL = "nomic-embed-text:v1.5"
    OLLAMA_TIMEOUT =  300.0
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 200
    VECTOR_DB_PATH = "data/chroma_db"

settings = Settings()
