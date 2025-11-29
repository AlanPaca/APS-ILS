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
class WorkExample(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    example_text: str
    role: str
    aps_level: str  # APS1, APS2, APS3, APS4, APS5, APS6, EL1, EL2
    capabilities: List[str] = Field(default_factory=list)
    behaviours: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    date_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkExampleCreate(BaseModel):
    title: str
    example_text: str
    role: str
    aps_level: str
    capabilities: List[str] = Field(default_factory=list)
    behaviours: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class ILSReference(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capability_name: str
    aps_level: str
    behaviour: str
    description: str

class AssessmentRequest(BaseModel):
    example_text: str
    aps_level: Optional[str] = "APS6"

class AssessmentResponse(BaseModel):
    assessment: str
    example_text: str

class SavedAssessment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    example_id: Optional[str] = None
    example_text: str
    assessment_text: str
    date_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# APS ILS Assessment System Message
APS_ASSESSMENT_SYSTEM = """You are an expert APS (Australian Public Service) assessor specializing in the Integrated Leadership System (ILS) framework.

Your role is to evaluate work examples against the APS ILS capabilities and behaviours for various APS levels (APS1-6, EL1-2).

The 5 core ILS capabilities are:
1. Supports Strategic Direction
2. Achieves Results
3. Supports Productive Working Relationships
4. Displays Personal Drive and Integrity
5. Communicates with Influence

When assessing a work example, provide:

1. **Capability Coverage Analysis**: Score each of the 5 capabilities (0-5 scale) based on evidence in the example

2. **Behaviour Alignment**: Identify which specific ILS behaviours are demonstrated

3. **Work Level Standards (WLS) Assessment**: Evaluate if the example meets the expected standard for the target APS level

4. **Strengths**: Highlight what the example does well

5. **Gaps & Missing Elements**: Identify what's missing or could be stronger

6. **Specific Improvements**: Provide actionable recommendations

7. **Refined Version**: Rewrite the example to better demonstrate ILS capabilities while maintaining authenticity

Format your response with clear headings and be specific with references to ILS behaviours."""


@api_router.post("/work-examples", response_model=WorkExample)
async def create_work_example(example: WorkExampleCreate):
    """Create a new work example"""
    try:
        work_example = WorkExample(**example.model_dump())
        example_dict = work_example.model_dump()
        example_dict['date_created'] = example_dict['date_created'].isoformat()
        
        await db.work_examples.insert_one(example_dict)
        return work_example
    except Exception as e:
        logging.error(f"Create work example error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating work example: {str(e)}")


@api_router.get("/work-examples", response_model=List[WorkExample])
async def get_work_examples(
    aps_level: Optional[str] = None,
    capability: Optional[str] = None,
    behaviour: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all work examples with optional filters"""
    try:
        query = {}
        
        if aps_level:
            query["aps_level"] = aps_level
        if capability:
            query["capabilities"] = capability
        if behaviour:
            query["behaviours"] = behaviour
        if tag:
            query["tags"] = tag
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"example_text": {"$regex": search, "$options": "i"}}
            ]
        
        examples = await db.work_examples.find(query, {"_id": 0}).sort("date_created", -1).to_list(1000)
        
        for example in examples:
            if isinstance(example['date_created'], str):
                example['date_created'] = datetime.fromisoformat(example['date_created'])
        
        return examples
    except Exception as e:
        logging.error(f"Get work examples error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching work examples: {str(e)}")


@api_router.get("/work-examples/{example_id}", response_model=WorkExample)
async def get_work_example(example_id: str):
    """Get a specific work example"""
    try:
        example = await db.work_examples.find_one({"id": example_id}, {"_id": 0})
        if not example:
            raise HTTPException(status_code=404, detail="Work example not found")
        
        if isinstance(example['date_created'], str):
            example['date_created'] = datetime.fromisoformat(example['date_created'])
        
        return example
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get work example error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching work example: {str(e)}")


@api_router.put("/work-examples/{example_id}", response_model=WorkExample)
async def update_work_example(example_id: str, example: WorkExampleCreate):
    """Update a work example"""
    try:
        existing = await db.work_examples.find_one({"id": example_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Work example not found")
        
        update_dict = example.model_dump()
        await db.work_examples.update_one({"id": example_id}, {"$set": update_dict})
        
        updated = await db.work_examples.find_one({"id": example_id}, {"_id": 0})
        if isinstance(updated['date_created'], str):
            updated['date_created'] = datetime.fromisoformat(updated['date_created'])
        
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Update work example error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating work example: {str(e)}")


@api_router.delete("/work-examples/{example_id}")
async def delete_work_example(example_id: str):
    """Delete a work example"""
    try:
        result = await db.work_examples.delete_one({"id": example_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Work example not found")
        return {"message": "Work example deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Delete work example error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting work example: {str(e)}")


@api_router.post("/assess", response_model=AssessmentResponse)
async def assess_example(request: AssessmentRequest):
    """Assess a work example against APS ILS framework"""
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured. Please add OPENAI_API_KEY to backend/.env")
        
        # Get ILS reference data for context
        ils_data = await db.ils_reference.find({"aps_level": request.aps_level}, {"_id": 0}).to_list(100)
        
        ils_context = "\n\n### APS ILS Framework Reference:\n"
        for item in ils_data:
            ils_context += f"**{item['capability_name']}** ({item['aps_level']}): {item['behaviour']} - {item['description']}\n"
        
        # Create assessment prompt
        assessment_prompt = f"""Please assess this work example against the APS ILS framework for {request.aps_level} level.

{ils_context}

### Work Example to Assess:
{request.example_text}

Provide a comprehensive assessment following the structured format outlined in your system instructions."""
        
        # Initialize AI chat
        chat_client = LlmChat(
            api_key=api_key,
            session_id=f"assessment_{uuid.uuid4()}",
            system_message=APS_ASSESSMENT_SYSTEM
        ).with_model("openai", "gpt-4o-mini")
        
        # Get assessment
        assessment = await chat_client.send_message(UserMessage(text=assessment_prompt))
        
        return AssessmentResponse(
            assessment=assessment,
            example_text=request.example_text
        )
    
    except Exception as e:
        logging.error(f"Assessment error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assessment error: {str(e)}")


@api_router.post("/assessments/save")
async def save_assessment(assessment: SavedAssessment):
    """Save an assessment for future reference"""
    try:
        assessment_dict = assessment.model_dump()
        assessment_dict['date_created'] = assessment_dict['date_created'].isoformat()
        
        await db.saved_assessments.insert_one(assessment_dict)
        return {"message": "Assessment saved successfully", "id": assessment.id}
    except Exception as e:
        logging.error(f"Save assessment error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving assessment: {str(e)}")


@api_router.get("/assessments", response_model=List[SavedAssessment])
async def get_saved_assessments():
    """Get all saved assessments"""
    try:
        assessments = await db.saved_assessments.find({}, {"_id": 0}).sort("date_created", -1).to_list(1000)
        
        for assessment in assessments:
            if isinstance(assessment['date_created'], str):
                assessment['date_created'] = datetime.fromisoformat(assessment['date_created'])
        
        return assessments
    except Exception as e:
        logging.error(f"Get assessments error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching assessments: {str(e)}")


@api_router.get("/ils-reference", response_model=List[ILSReference])
async def get_ils_reference(aps_level: Optional[str] = None, capability: Optional[str] = None):
    """Get ILS reference data"""
    try:
        query = {}
        if aps_level:
            query["aps_level"] = aps_level
        if capability:
            query["capability_name"] = capability
        
        references = await db.ils_reference.find(query, {"_id": 0}).to_list(1000)
        return references
    except Exception as e:
        logging.error(f"Get ILS reference error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching ILS reference: {str(e)}")


@api_router.get("/filters")
async def get_filter_options():
    """Get all unique filter options for dropdowns"""
    try:
        examples = await db.work_examples.find({}, {"_id": 0}).to_list(1000)
        
        capabilities = set()
        behaviours = set()
        tags = set()
        aps_levels = set()
        
        for example in examples:
            capabilities.update(example.get('capabilities', []))
            behaviours.update(example.get('behaviours', []))
            tags.update(example.get('tags', []))
            aps_levels.add(example.get('aps_level', ''))
        
        return {
            "capabilities": sorted(list(capabilities)),
            "behaviours": sorted(list(behaviours)),
            "tags": sorted(list(tags)),
            "aps_levels": sorted(list(aps_levels))
        }
    except Exception as e:
        logging.error(f"Get filter options error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching filter options: {str(e)}")


@api_router.get("/")
async def root():
    return {"message": "APS ILS Work Examples API"}


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