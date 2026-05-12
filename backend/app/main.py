from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env variables before importing routes
load_dotenv()

from app.api.routes import router as chat_router

app = FastAPI(
    title="Google Drive AI Assistant",
    description="Conversational AI agent for Google Drive file discovery",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Google Drive AI Assistant API is running"}
