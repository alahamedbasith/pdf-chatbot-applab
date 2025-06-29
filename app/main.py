# This is the main application file for the FastAPI-based PDF Chatbot.
# It handles file uploads, chat requests, and Ollama health checks.

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from tempfile import NamedTemporaryFile
import traceback 

import httpx

from app.models import ChatRequest
from app.utils import process_pdf, get_response, sanitize_filename
from app.vectorstore import processed_documents
from app.config import settings

# Disaable langchain telemetry because it can cause issues in some environments
# and is not necessary for this application.
os.environ["LANGCHAIN_TELEMETRY_ENABLED"] = "false" 

app = FastAPI(title="PDF Chatbot - AppLab Qatar", version="1.0.0")

# template engine and static files setup
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def load_homepage(request: Request):
    """Render the homepage with upload and chat UI."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ollama_base_url": settings.OLLAMA_BASE_URL
    })


@app.post("/api/upload")
async def handle_file_upload(file: UploadFile = File(...)):
    """
    Accept a only PDF upload, sanitize its name,
    and process it into the vectorstore.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed. Uploaded file is not a PDF."
        )
    
    try:
        collection_id = sanitize_filename(file.filename)

        if collection_id.lower() in (doc.lower() for doc in processed_documents):
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": f"'{file.filename}' is already uploaded."}
            )

        # Temporarily save file and process it
        with NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(await file.read())
            temp_file_path = tmp_file.name

        result = process_pdf(temp_file_path, collection_id)

        # Track the document if processed successfully
        if result.get("status") == "success":
            processed_documents.add(collection_id)

        os.remove(temp_file_path)

        return result

    except Exception as err:
        tb_str = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Upload failed: {str(err)}", "traceback": tb_str}
        )


@app.post("/api/chat")
async def handle_chat(chat_request: ChatRequest): 
    """
    Answer a user query based on the selected document.
    """
    try:
        answer = get_response(chat_request.question, chat_request.collection_name)
        return {"response": answer}
    except Exception as err:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Chat failed: {str(err)}"}
        )


@app.get("/api/documents")
async def get_uploaded_documents():
    """Return the list of all processed document names."""
    return sorted(set(processed_documents))

@app.get("/api/ollama-health")
async def ollama_health_check():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.OLLAMA_BASE_URL}/api/tags",
                timeout=2.0
            )
            response.raise_for_status()
            return JSONResponse(content={"status": "ok"})
    except Exception as err:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": f"Ollama connection failed: {str(err)}"}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
