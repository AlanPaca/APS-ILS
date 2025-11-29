from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class ChatRequest(BaseModel):
    message: str
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ChatResponse(BaseModel):
    response: str
    session_id: str

class StoreRequest(BaseModel):
    content: str

class StoredEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # user or assistant
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# System message for APS ILS specialization
APS_SYSTEM_MESSAGE = """You are an expert assistant specializing in the Australian Public Service (APS) Integrated Leadership System (ILS). 
You help job applicants with:

1. Understanding APS ILS competencies:
   - Achieves Results
   - Supports Productive Working Relationships
   - Displays Personal Drive and Integrity
   - Communicates with Influence
   - Shapes Strategic Thinking

2. Crafting responses to selection criteria
3. Structuring STAR (Situation, Task, Action, Result) responses
4. Understanding APS work level standards (APS 1-6, EL 1-2, SES)
5. General advice on APS job applications

When analyzing text for storage, identify relevant tags based on:
- APS ILS competencies mentioned
- Work level (APS1-6, EL1-2, SES, etc.)
- Key skills or themes
- Document type (cover letter, selection criteria, resume point, etc.)

Be professional, concise, and supportive."""


@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with AI assistant about APS job applications"""
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured. Please add OPENAI_API_KEY to backend/.env")
        
        # Save user message
        user_msg = ChatMessage(
            session_id=request.session_id,
            role="user",
            content=request.message
        )
        user_msg_dict = user_msg.model_dump()
        user_msg_dict['timestamp'] = user_msg_dict['timestamp'].isoformat()
        await db.chat_messages.insert_one(user_msg_dict)
        
        # Get chat history for context
        history = await db.chat_messages.find(
            {"session_id": request.session_id},
            {"_id": 0}
        ).sort("timestamp", 1).limit(20).to_list(20)
        
        # Initialize AI chat
        chat_client = LlmChat(
            api_key=api_key,
            session_id=request.session_id,
            system_message=APS_SYSTEM_MESSAGE
        ).with_model("openai", "gpt-4o-mini")
        
        # Send message and get response
        user_message = UserMessage(text=request.message)
        ai_response = await chat_client.send_message(user_message)
        
        # Save assistant response
        assistant_msg = ChatMessage(
            session_id=request.session_id,
            role="assistant",
            content=ai_response
        )
        assistant_msg_dict = assistant_msg.model_dump()
        assistant_msg_dict['timestamp'] = assistant_msg_dict['timestamp'].isoformat()
        await db.chat_messages.insert_one(assistant_msg_dict)
        
        return ChatResponse(response=ai_response, session_id=request.session_id)
    
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@api_router.post("/store", response_model=StoredEntry)
async def store_entry(request: StoreRequest):
    """Store text with AI-generated tags"""
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured. Please add OPENAI_API_KEY to backend/.env")
        
        # Generate tags using AI
        tag_prompt = f"""Analyze this text related to APS job applications and provide 3-5 relevant tags.
Tags should be based on:
- APS ILS competencies (Achieves Results, Supports Productive Working Relationships, etc.)
- Work level (APS1-6, EL1-2, SES)
- Key skills or themes
- Document type

Respond ONLY with a comma-separated list of tags, nothing else.

Text to analyze:
{request.content}"""
        
        chat_client = LlmChat(
            api_key=api_key,
            session_id="tagging",
            system_message="You are a tagging assistant. Return only comma-separated tags."
        ).with_model("openai", "gpt-4o-mini")
        
        tag_response = await chat_client.send_message(UserMessage(text=tag_prompt))
        tags = [tag.strip() for tag in tag_response.split(',') if tag.strip()]
        
        # Create and store entry
        entry = StoredEntry(
            content=request.content,
            tags=tags
        )
        
        entry_dict = entry.model_dump()
        entry_dict['created_at'] = entry_dict['created_at'].isoformat()
        entry_dict['updated_at'] = entry_dict['updated_at'].isoformat()
        
        await db.stored_entries.insert_one(entry_dict)
        
        return entry
    
    except Exception as e:
        logging.error(f"Store error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Store error: {str(e)}")


@api_router.get("/entries", response_model=List[StoredEntry])
async def get_entries(tag: Optional[str] = None):
    """Get all stored entries, optionally filtered by tag"""
    try:
        query = {}
        if tag:
            query["tags"] = tag
        
        entries = await db.stored_entries.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
        
        # Convert ISO strings back to datetime
        for entry in entries:
            if isinstance(entry['created_at'], str):
                entry['created_at'] = datetime.fromisoformat(entry['created_at'])
            if isinstance(entry['updated_at'], str):
                entry['updated_at'] = datetime.fromisoformat(entry['updated_at'])
        
        return entries
    except Exception as e:
        logging.error(f"Get entries error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get entries error: {str(e)}")


@api_router.get("/tags", response_model=List[str])
async def get_tags():
    """Get all unique tags"""
    try:
        entries = await db.stored_entries.find({}, {"_id": 0, "tags": 1}).to_list(1000)
        all_tags = set()
        for entry in entries:
            all_tags.update(entry.get('tags', []))
        return sorted(list(all_tags))
    except Exception as e:
        logging.error(f"Get tags error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get tags error: {str(e)}")


@api_router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str):
    """Delete a stored entry"""
    try:
        result = await db.stored_entries.delete_one({"id": entry_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Entry not found")
        return {"message": "Entry deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")


@api_router.get("/")
async def root():
    return {"message": "APS Job Helper API"}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()