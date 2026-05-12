# 📁 AI-Powered Google Drive File Discovery Assistant

## 📝 Project Overview
A complete production-ready AI agent that helps users search, filter, and discover files from a Google Drive folder through natural language conversation. The assistant correctly interprets natural language, formulates Google Drive `q` queries via tool-calling, and returns formatted, accurate results with clickable links.

## 🏗️ Architecture

Here is how the data flows from the user to the Google Drive API:

```text
Streamlit UI
     ↓
FastAPI Backend
     ↓
LangChain Agent
     ↓
DriveSearchTool
     ↓
Google Drive API
```

## ✨ Features
- **Handles Natural Language Properly**: Interprets complex requests for dates, file types, and content.
- **Accurate Results**: Uses exact/partial name matching, file type filtering, full-text search, and modified date filtering.
- **Polished UI**: Clean, modern chat interface built with Streamlit, featuring quick-access sample queries.
- **Robust Backend**: Modular and asynchronous FastAPI service holding a state-of-the-art LangGraph agent.

## 💻 Tech Stack
| Purpose      | Tool                     |
| ------------ | ------------------------ |
| Backend      | FastAPI                  |
| AI Framework | LangChain & LangGraph    |
| LLM          | Groq (Llama 3.1 8B)      |
| Frontend     | Streamlit                |
| File Search  | Google Drive API         |
| Deployment   | Render + Streamlit Cloud |

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.9+
- A Google Cloud Project with Google Drive API enabled.
- A Service Account and its JSON credentials file.
- A shared Google Drive folder.
- Groq API Key.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Backend
From the root of the project:
```bash
uvicorn app.main:app --app-dir backend --reload --port 8000
```
*(The API will run at http://localhost:8000)*

### 4. Run the Frontend
In a new terminal window, run:
```bash
streamlit run frontend/app.py
```

## 🔐 Environment Variables
Copy `.env.example` to `.env` and fill in your values:

```env
# API Keys
GROQ_API_KEY=your_groq_api_key

# Google Drive Integration
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
DRIVE_FOLDER_ID=your_shared_folder_id

# Backend URL for frontend
BACKEND_URL=http://localhost:8000
```
**Important:** Ensure your `credentials.json` (Service Account Key) is placed at the root of the project alongside the `.env` file.

## 🔗 Deployment Links

- **Frontend (Streamlit Cloud):** `[Insert Streamlit URL Here]`
- **Backend (Render):** `[Insert Render URL Here]`

### Recommended Deployment Steps
- **Backend → Render**: Deploy as a Web Service. Set the Build Command to `pip install -r requirements.txt` and Start Command to `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`. Inject all Environment Variables, including `credentials.json` via a Secret File.
- **Frontend → Streamlit Cloud**: Connect your GitHub repository. Point the Main file path to `frontend/app.py`. Add the `BACKEND_URL` environment variable pointing to the newly deployed Render instance.

## 🗣️ Sample Queries

Try asking the assistant:
- "Find finance PDFs"
- "Show spreadsheets uploaded recently"
- "Find documents containing internship"
- "Search image files"
- "Find reports modified last week"

## 📸 Screenshots

*(Add screenshots of your UI here before submitting!)*
![App Screenshot](https://via.placeholder.com/800x400?text=App+Screenshot)
