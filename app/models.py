from pydantic import BaseModel

class DocumentUpload(BaseModel):
    file_name: str

class ChatRequest(BaseModel):
    question: str
    collection_name: str
