from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from app.services.agent import agent_executor, format_history

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []

class ChatResponse(BaseModel):
    response: str

SYSTEM_PROMPT = (
    "You are an AI assistant helping users discover files in a Google Drive folder. "
    "You have access to the google_drive_search tool. "
    "When a user asks for a file, translate their request into a valid Google Drive 'q' query "
    "and call the google_drive_search tool. "
    "IMPORTANT: If the user doesn't specify an exact search, use 'contains' for name or fullText. "
    "When returning results, provide a clean, Markdown-formatted list containing the file name, "
    "type, modified date, and make the webViewLink clickable."
)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Format the incoming history into LangChain messages
        chat_history = format_history(request.history)
        
        # Inject the system prompt as the very first message
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + chat_history + [HumanMessage(content=request.message)]
        
        # Invoke the LangGraph agent
        result = agent_executor.invoke({"messages": messages})
        
        # The agent's final response is the last message in the returned list
        final_answer = result["messages"][-1].content
        
        return ChatResponse(response=final_answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
