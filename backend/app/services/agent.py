from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from app.services.drive import drive_service
from app.core.config import settings

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
        return drive_service.search_files(q)

def get_agent_executor():
    if settings.GROQ_API_KEY:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    else:
        # Fallback if GROQ is not available
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    tools = [DriveSearchTool()]
    
    # We use LangGraph's prebuilt agent which is the modern LangChain standard
    agent_executor = create_react_agent(llm, tools)
    return agent_executor

def format_history(history: List[Dict]) -> List:
    formatted = []
    for msg in history:
        if msg["role"] == "user":
            formatted.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            formatted.append(AIMessage(content=msg["content"]))
    return formatted

# Initialize agent
agent_executor = get_agent_executor()
