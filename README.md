# PDF Chatbot

This project is a PDF Chatbot developed as part of an assessment for Applab Qatar. It enables users to upload PDF documents and interactively query their contents. The solution leverages Ollama for local language model inference, FastAPI for the backend, and a straightforward HTML/CSS/JavaScript frontend.

## Features

*   **PDF Upload:** Upload PDF files to the application.
*   **Chat Interface:** Ask questions about the content of the uploaded PDFs.
*   **Local LLM:** Uses a local language model via Ollama for privacy and offline use.
*   **Dockerized:** The entire application can be run using Docker and Docker Compose.

## Project Structure

```
.
├── app/                # Main application folder
│   ├── main.py         # FastAPI application
│   ├── config.py       # Application configuration
│   ├── models.py       # Pydantic models
│   ├── utils.py        # Utility functions for PDF processing and chat
│   └── vectorstore.py  # Vectorstore management
├── data/               # Data folder for Chroma DB
├── ollama/             # Ollama service folder
│   ├── Dockerfile      # Dockerfile for Ollama service
│   └── pull.sh         # Script to pull Ollama models
├── static/             # Static files (CSS, JS)
├── templates/          # HTML templates
├── compose.yml         # Docker Compose file
├── Dockerfile          # Dockerfile for the main application
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Prerequisites

### For Local Setup

*   Python 3.8+
*   [Ollama](https://ollama.ai/) installed and running.
*   The following Ollama models pulled:
    *   `gemma3:1b`
    *   `nomic-embed-text:v1.5`

### For Docker Setup

*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/)

## Setup and Run Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/alahamedbasith/pdf-chatbot-applab.git
    cd pdf-chatbot
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ensure Ollama is installed:**
    Make sure [Ollama](https://ollama.ai/) is installed on your machine and running.

5.  **Run Ollama and pull required models:**
    Pull the required models using the following commands:
    ```bash
    ollama pull gemma3:1b
    ollama pull nomic-embed-text:v1.5
    ```

6.  **Run the FastAPI application:**
    ```bash
    uvicorn app.main:app --reload
    ```

7.  Open your browser and navigate to `http://localhost:8000`.

## Setup and Run with Docker

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/alahamedbasith/pdf-chatbot-applab.git
    cd pdf-chatbot
    ```

2.  **Build and run the services using Docker Compose:**
    ```bash
    docker-compose up -d --build
    ```
    This will build the Docker images for the application and the Ollama service, and start the containers in detached mode. The `pull.sh` script in the `ollama` service will pull the required models, which may take some time.

3.  Open your browser and navigate to `http://localhost:8000`.

> **Note:**  
> This project uses two separate Docker images: one for the FastAPI application (exposed on port `8000`) and one for the Ollama service (exposed on port `11434`). Building these images may take some time, as all dependencies and models are included to ensure a smooth setup process.
>
> **If the application is not running, possible causes include:**
> - **Internet connection issues:** Ensure your internet connection is stable, especially during the initial build and model download.
> - **Insufficient CPU resources in Docker:** Increase the CPU allocation for Docker, or use a machine with a GPU if available.
> - **Low storage space in Docker:** Free up space by running `docker system prune` to remove unused containers, images, and volumes.

## API Endpoints

*   `GET /`: Renders the homepage.
*   `POST /api/upload`: Handles PDF file uploads.
*   `POST /api/chat`: Handles chat requests.
*   `GET /api/documents`: Returns a list of uploaded documents.
*   `GET /api/ollama-health`: Checks the health of the Ollama service.

## Technologies Used

*   **Backend:** FastAPI, Python
*   **Frontend:** HTML, CSS, JavaScript
*   **LLM:** Ollama (with `gemma3:1b` and `nomic-embed-text:v1.5` models)
*   **Vectorstore:** Chroma DB
*   **Containerization:** Docker, Docker Compose
