from typing import List, Dict, Any
import json
import logging
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from app.services.drive import drive_service
from app.core.config import settings

logger = logging.getLogger(__name__)

class DriveSearchInput(BaseModel):
    q: str = Field(description="The Google Drive API 'q' query string.")

class DriveSearchTool(BaseTool):
    name: str = "google_drive_search"
    description: str = (
        "Searches Google Drive for files using the Drive API 'q' parameter. "
        "Formulate 'q' according to Google Drive API v3. Examples: "
        "name contains 'financial', mimeType='application/pdf', "
        "fullText contains 'finance', modifiedTime > '2023-10-24T12:00:00'."
    )
    args_schema: type[BaseModel] = DriveSearchInput
    
    def _run(self, q: str) -> str:
        logger.info(f"[TOOL] DriveSearchTool invoked with query: {q}")
        result = drive_service.search_files(q)
        logger.info(f"[TOOL] DriveSearchTool result: {result}")
        
        # Parse the result to check for errors
        try:
            result_obj = json.loads(result)
            if "status" in result_obj:
                if result_obj["status"] != "SUCCESS":
                    logger.error(f"[TOOL] Drive search returned error status: {result_obj['status']}")
                    if "error" in result_obj:
                        logger.error(f"[TOOL] Error message: {result_obj['error']}")
        except json.JSONDecodeError:
            logger.error(f"[TOOL] Could not parse result as JSON: {result}")
        
        return result

def get_agent_executor():
    logger.info("[AGENT] Initializing LangChain agent executor...")
    
    # Verify credentials are loaded
    if not drive_service.credentials:
        logger.error("[AGENT] ⚠️ WARNING: Google Drive credentials not loaded!")
        logger.error("[AGENT] The agent will be unable to search Google Drive.")
    
    # Verify service is initialized
    if not drive_service.service:
        logger.error("[AGENT] ⚠️ WARNING: Google Drive service not initialized!")
        logger.error("[AGENT] The agent will be unable to execute searches.")
    
    # Initialize LLM
    if settings.GROQ_API_KEY:
        logger.info("[AGENT] Using Groq LLM (llama-3.1-8b-instant)")
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    else:
        logger.warning("[AGENT] GROQ_API_KEY not set, falling back to OpenAI")
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Create tools
    tools = [DriveSearchTool()]
    logger.info(f"[AGENT] Registered {len(tools)} tools")
    
    # Create ReAct agent
    logger.info("[AGENT] Creating ReAct agent with LangGraph...")
    agent_executor = create_react_agent(llm, tools)
    logger.info("[AGENT] ✅ Agent executor initialized successfully")
    
    return agent_executor

def format_history(history: List[Dict]) -> List:
    """Convert message dicts to LangChain message objects"""
    formatted = []
    for msg in history:
        if msg.get("role") == "user":
            formatted.append(HumanMessage(content=msg.get("content", "")))
        elif msg.get("role") == "assistant":
            formatted.append(AIMessage(content=msg.get("content", "")))
    return formatted

# Initialize agent on module load
logger.info("[STARTUP] Initializing agent on module load...")
agent_executor = get_agent_executor()
logger.info("[STARTUP] ✅ Agent ready")
