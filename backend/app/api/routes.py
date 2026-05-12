from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import json
from langchain_core.messages import HumanMessage, SystemMessage

from app.services.agent import agent_executor, format_history
from app.services.drive import drive_service

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []

class ChatResponse(BaseModel):
    response: str

SYSTEM_PROMPT = (
    "You are an AI assistant helping users discover files in their Google Drive folder. "
    "You have access to the google_drive_search tool which searches Google Drive files. "
    "When a user asks for a file or searches for something:\n\n"
    "1. Understand what they're looking for (file type, name pattern, date range, etc.)\n"
    "2. Translate their request into a valid Google Drive API 'q' query\n"
    "3. Call the google_drive_search tool with the query\n\n"
    "IMPORTANT QUERY EXAMPLES:\n"
    "- For file type: mimeType='application/pdf' (PDFs), mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' (Excel)\n"
    "- For name search: name contains 'finance'\n"
    "- For content search: fullText contains 'budget'\n"
    "- For date: modifiedTime > '2024-01-01T00:00:00'\n"
    "- Combined: (name contains 'report') and mimeType='application/pdf' and modifiedTime > '2024-01-01T00:00:00'\n\n"
    "When returning results, provide a clean, Markdown-formatted list with:\n"
    "- File name (as a clickable link using webViewLink)\n"
    "- File type (mime type)\n"
    "- Modified date\n"
    "- Brief description if available\n\n"
    "If no files are found, explain why and suggest alternative searches."
)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    logger.info("=" * 80)
    logger.info("[API] POST /api/chat - Chat request received")
    logger.info(f"[API] User message: {request.message[:100]}...")
    logger.info(f"[API] History length: {len(request.history)}")
    
    # Check credentials before processing
    if not drive_service.credentials:
        logger.error("[API] ❌ Google Drive credentials not loaded")
        error_response = (
            "❌ **Google Drive Authentication Failed**\n\n"
            "The system cannot access your Google Drive. This means:\n\n"
            "1. **credentials.json is not loaded** - The Service Account credentials file is missing\n"
            "2. **Check your Render setup**:\n"
            "   - Go to your Render service Settings\n"
            "   - Add a **Secret File** named `credentials.json`\n"
            "   - Paste your entire Google Service Account JSON\n"
            "3. **Redeploy** your backend service\n\n"
            "Once fixed, your queries like 'Find PDFs' will work correctly."
        )
        logger.error(f"[API] Returning error message to user")
        return ChatResponse(response=error_response)
    
    if not drive_service.service:
        logger.error("[API] ❌ Google Drive API service not initialized")
        error_response = (
            "❌ **Google Drive Service Error**\n\n"
            "The Google Drive API service failed to initialize. This typically means:\n\n"
            "1. **Invalid credentials** - The credentials.json file may be malformed\n"
            "2. **Insufficient permissions** - The Service Account doesn't have Drive API access\n"
            "3. **API not enabled** - Google Drive API might not be enabled in Google Cloud Console\n\n"
            "Please check your Google Cloud Console settings and redeploy."
        )
        logger.error(f"[API] Returning error message to user")
        return ChatResponse(response=error_response)
    
    try:
        # Format the incoming history into LangChain messages
        chat_history = format_history(request.history)
        logger.info(f"[API] Formatted {len(chat_history)} historical messages")
        
        # Construct the message list: system prompt + history + current message
        messages = (
            [SystemMessage(content=SYSTEM_PROMPT)] + 
            chat_history + 
            [HumanMessage(content=request.message)]
        )
        logger.info(f"[API] Total messages for agent: {len(messages)}")
        logger.info(f"[API] Invoking agent executor...")
        
        # Invoke the LangGraph agent
        result = agent_executor.invoke({"messages": messages})
        
        # Extract the final answer
        final_answer = result.get("messages", [])[-1].content if result.get("messages") else "No response"
        logger.info(f"[API] ✅ Agent response generated")
        logger.info(f"[API] Response length: {len(final_answer)} characters")
        
        return ChatResponse(response=final_answer)
        
    except Exception as e:
        logger.error(f"[API] ❌ Exception occurred: {str(e)}", exc_info=True)
        error_response = (
            f"❌ **Error Processing Your Request**\n\n"
            f"An error occurred while searching your Google Drive:\n\n"
            f"```\n{str(e)}\n```\n\n"
            f"Please try:\n"
            f"1. Simplifying your search query\n"
            f"2. Checking that files exist in your shared Google Drive folder\n"
            f"3. Verifying your credentials are correctly configured"
        )
        raise HTTPException(status_code=500, detail=error_response)
