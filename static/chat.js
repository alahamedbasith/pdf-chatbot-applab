// DOM elements
const fileInput = document.getElementById('fileInput');
const uploadButton = document.getElementById('uploadButton');
const uploadStatus = document.getElementById('uploadStatus');
const documentsList = document.getElementById('documentsList');
const chatMessages = document.getElementById('chatMessages');
const questionInput = document.getElementById('questionInput');
const sendButton = document.getElementById('sendButton');
const connectionStatus = document.getElementById('connectionStatus');

// Application state
let activeDocument = null;
let isDocumentLoading = false;
let isUploading = false;

initApp();

async function initApp() {
    await checkOllamaConnection();
    await loadDocuments();
}

// Event listeners
fileInput.addEventListener('change', handleFileUpload);
sendButton.addEventListener('click', sendQuestion);
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendQuestion();
});

// Check Ollama health
async function checkOllamaConnection() {
    try {
        const response = await fetch('/api/ollama-health');
        if (response.ok) {
            connectionStatus.textContent = "Connected to Ollama";
            connectionStatus.className = "connected";
        } else {
            connectionStatus.textContent = "Ollama connection failed";
            connectionStatus.className = "disconnected";
        }
    } catch (error) {
        connectionStatus.textContent = "Ollama not reachable";
        connectionStatus.className = "disconnected";
    }
}

// Load uploaded documents
async function loadDocuments() {
    try {
        const response = await fetch('/api/documents');
        const documents = await response.json();

        documentsList.innerHTML = '';

        if (documents.length === 0) {
            documentsList.innerHTML = '<p>No documents uploaded yet.</p>';
            return;
        }

        // Remove duplicates (case-insensitive)
        const uniqueDocs = [];
        const seen = new Set();

        documents.forEach(doc => {
            const lowerDoc = doc.toLowerCase();
            if (!seen.has(lowerDoc)) {
                seen.add(lowerDoc);
                uniqueDocs.push(doc);
            }
        });

        // Sort alphabetically
        uniqueDocs.sort((a, b) => a.localeCompare(b));

        uniqueDocs.forEach(doc => {
            const docElement = document.createElement('div');
            docElement.className = 'document-item';
            docElement.textContent = doc;

            if (doc === activeDocument) {
                docElement.classList.add('active');
            }

            docElement.addEventListener('click', () => selectDocument(doc));
            documentsList.appendChild(docElement);
        });

    } catch (error) {
        documentsList.innerHTML = `<p>Error loading documents: ${error.message}</p>`;
    }
}

// Select a document
async function selectDocument(docName) {
    if (isDocumentLoading) return;

    isDocumentLoading = true;
    activeDocument = docName;

    // Update UI
    const docItems = documentsList.querySelectorAll('.document-item');
    docItems.forEach(item => {
        item.classList.remove('active', 'document-loading');
        if (item.textContent === docName) {
            item.classList.add('active', 'document-loading');
        }
    });

    questionInput.disabled = true;
    sendButton.disabled = true;
    uploadButton.classList.add('disabled');

    try {
        await new Promise(resolve => setTimeout(resolve, 300));
        addMessage(`Document loaded: ${docName}`, 'bot');

        questionInput.disabled = false;
        sendButton.disabled = false;
        questionInput.focus();
    } catch (error) {
        addMessage(`Error loading document: ${error.message}`, 'error');
    } finally {
        isDocumentLoading = false;
        uploadButton.classList.remove('disabled');
        await loadDocuments();
    }
}

// Handle file upload
async function handleFileUpload() {
    if (!fileInput.files.length || isUploading) return;

    isUploading = true;
    uploadButton.classList.add('disabled');
    uploadButton.textContent = 'Uploading...';

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        showStatus('Uploading and processing document...', 'info');

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.status === 'success') {
            showStatus(result.message, 'success');
            await loadDocuments();
            await selectDocument(result.collection_name);
        } else {
            showStatus(result.message, 'error');
        }

    } catch (error) {
        showStatus('Error uploading file: ' + error.message, 'error');
    } finally {
        isUploading = false;
        uploadButton.classList.remove('disabled');
        uploadButton.textContent = 'Upload PDF';
        fileInput.value = '';
    }
}

// Send user question
async function sendQuestion() {
    const question = questionInput.value.trim();
    if (!question || !activeDocument || isDocumentLoading) return;

    addMessage(question, 'user');
    questionInput.value = '';
    questionInput.disabled = true;
    sendButton.disabled = true;

    const loadingId = 'loading-' + Date.now();
    addMessage('Processing your question...', 'bot', loadingId);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                collection_name: activeDocument
            })
        });

        removeMessage(loadingId);

        if (!response.ok) {
            const errorResult = await response.json();
            addMessage(`Error: ${errorResult.message || 'Unknown server error'}`, 'error');
            return;
        }

        const result = await response.json();

        if (result.response) {
            addMessage(result.response, 'bot');
        } else {
            addMessage('Error: Unexpected response format from server', 'error');
        }
    } catch (error) {
        removeMessage(loadingId);
        addMessage('Error: ' + error.message, 'error');
    } finally {
        questionInput.disabled = false;
        sendButton.disabled = false;
        questionInput.focus();
    }
}

// Utility to add message
function addMessage(text, sender, id = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    if (sender === 'bot') {
        messageDiv.innerHTML = marked.parse(text);
    } else {
        messageDiv.textContent = text;
    }

    if (id) {
        messageDiv.id = id;
        if (sender === 'bot') {
            const loadingSpan = document.createElement('span');
            loadingSpan.className = 'loading';
            messageDiv.appendChild(loadingSpan);
        }
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Utility to remove message
function removeMessage(id) {
    const message = document.getElementById(id);
    if (message) {
        message.remove();
    }
}

// Utility to show status messages
function showStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = 'status-message ' + type;
}
