#main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import secrets

# Import your service modules
from services.jobs_service import JobsService
from services.events_service import EventsService
from services.mentors_service import MentorsService
from services.llm_service import LLMService

# Import our simplified auth service
from services.auth_service import SimpleAuthService, User, UserCreate

app = FastAPI(title="Asha AI Chatbot API")
security = HTTPBasic()
auth_service = SimpleAuthService()  # Create a single instance

# Dependency injection for services
def get_jobs_service():
    service = JobsService()
    try:
        yield service
    finally:
        service.close()

def get_events_service():
    service = EventsService()
    try:
        yield service
    finally:
        service.close()

def get_mentors_service():
    service = MentorsService()
    try:
        yield service
    finally:
        service.close()

def get_llm_service():
    return LLMService()

# Models
class ChatRequest(BaseModel):
    query: str
    chat_history: Optional[List[List[str]]] = []

class ChatResponse(BaseModel):
    response: str
    data: Optional[Dict[str, Any]] = None

class JobFilter(BaseModel):
    search: Optional[str] = None
    location: Optional[str] = None
    remote: Optional[bool] = None
    page: Optional[int] = 1

class EventFilter(BaseModel):
    category: Optional[str] = None
    location: Optional[str] = None

class MentorFilter(BaseModel):
    search: Optional[str] = None
    company: Optional[str] = None
    service: Optional[str] = None

# Simple authentication function
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = auth_service.authenticate(credentials.username, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

# Authentication routes
@app.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """Register a new user"""
    # Check if username already exists
    if user.username in auth_service.users:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    return auth_service.create_user(user)

# Routes
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, 
               current_user: User = Depends(get_current_user),
               llm_service: LLMService = Depends(get_llm_service)):
    """Process chat query and provide response with any relevant data"""
    try:
        # Process the query through LLM service
        processed_result = llm_service.process_query(request.query, request.chat_history)
        
        return ChatResponse(
            response=processed_result["response"],
            data=processed_result.get("data", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/jobs")
async def get_jobs(filters: JobFilter, 
                  current_user: User = Depends(get_current_user),
                  jobs_service: JobsService = Depends(get_jobs_service)):
    """Get job listings with filtering options"""
    try:
        jobs = jobs_service.search_jobs(
            search=filters.search,
            location=filters.location,
            remote=filters.remote
        )
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")

@app.post("/events")
async def get_events(filters: EventFilter, 
                    current_user: User = Depends(get_current_user),
                    events_service: EventsService = Depends(get_events_service)):
    """Get event listings with filtering options"""
    try:
        events = events_service.get_events(
            category=filters.category,
            location=filters.location
        )
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

@app.get("/categories")
async def get_categories(current_user: User = Depends(get_current_user),
                        events_service: EventsService = Depends(get_events_service)):
    """Get all event categories"""
    try:
        categories = events_service.get_categories()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@app.get("/locations")
async def get_locations(current_user: User = Depends(get_current_user),
                       events_service: EventsService = Depends(get_events_service)):
    """Get all event locations"""
    try:
        locations = events_service.get_locations()
        return {"locations": locations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching locations: {str(e)}")

@app.get("/job-locations")
async def get_job_locations(current_user: User = Depends(get_current_user),
                           jobs_service: JobsService = Depends(get_jobs_service)):
    """Get all job locations"""
    try:
        locations = jobs_service.get_locations()
        return {"locations": locations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job locations: {str(e)}")

@app.post("/mentors")
async def get_mentors(filters: MentorFilter, 
                     current_user: User = Depends(get_current_user),
                     mentors_service: MentorsService = Depends(get_mentors_service)):
    """Get mentor listings with filtering options"""
    try:
        mentors = mentors_service.get_mentors(
            search=filters.search,
            company=filters.company,
            service=filters.service
        )
        return {"mentors": mentors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching mentors: {str(e)}")

@app.get("/mentor-companies")
async def get_mentor_companies(current_user: User = Depends(get_current_user),
                              mentors_service: MentorsService = Depends(get_mentors_service)):
    """Get all companies with mentors"""
    try:
        companies = mentors_service.get_companies()
        return {"companies": companies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching mentor companies: {str(e)}")

@app.get("/mentor-services")
async def get_mentor_services(current_user: User = Depends(get_current_user),
                             mentors_service: MentorsService = Depends(get_mentors_service)):
    """Get all mentor services"""
    try:
        services = mentors_service.get_services()
        return {"services": services}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching mentor services: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # Add this at the bottom of main.py
    
