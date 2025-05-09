#llm_service.py
from utils.rag_utils import RAGSystem
from services.jobs_service import JobsService
from services.events_service import EventsService
from services.mentors_service import MentorsService
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

class LLMService:
    def __init__(self):
        self.rag = RAGSystem()
        self.jobs_service = JobsService()
        self.events_service = EventsService()
        self.mentors_service = MentorsService()
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.intent_model = genai.GenerativeModel('gemini-1.5-flash')
        self.response_model = genai.GenerativeModel('gemini-1.5-pro')
        
    def process_query(self, query, chat_history=None):
        # First, detect intent
        intent_data = self._detect_intent(query)
        intent = intent_data.get("intent")
        filters = intent_data.get("filters", {})
        
        # Check if this is a follow-up query about events
        if chat_history and intent == "general" and query.lower() in ["virtual", "online", "remote"]:
            for i in range(len(chat_history) - 1, -1, -1):
                if "event" in chat_history[i][0].lower():
                    intent = "event_search"
                    # Extract category from previous query if possible
                    if "herkey" in chat_history[i][0].lower():
                        filters["category"] = "HerKey"
                    filters["location"] = None  # Clear any location restriction
                    filters["mode"] = "virtual"
                    break
        
        # Initialize data dictionary for storing fetched items
        data = {}
        
        # For job searches, get Neo4j job data
        if intent == "job_search":
            search = filters.get("search", "")
            location = filters.get("location")
            remote = filters.get("remote")
            
            # Only fetch jobs if we have search terms
            if search:
                jobs_result = self.jobs_service.search_jobs(
                    search=search,
                    location=location,
                    remote=remote,
                    limit=7
                )
                
                if jobs_result and "results" in jobs_result and jobs_result["results"]:
                    data["jobs"] = jobs_result["results"]
                
        # For event searches, get Neo4j event data
        elif intent == "event_search":
            category = filters.get("category")
            location = filters.get("location")
            
            # Extended logging for debugging
            print(f"Searching for events with category: {category}, location: {location}")
            
            events = self.events_service.get_events(category=category, location=location)
            if events:
                # Filter by mode if specified
                if "mode" in filters and filters["mode"] and filters["mode"].lower() in ["virtual", "online"]:
                    events = [event for event in events if event.get("mode", "").lower() in ["virtual", "online"]]
                
                data["events"] = events
                print(f"Found {len(events)} events")
            else:
                print("No events found in database")
        elif intent == "mentor_search":
            search = filters.get("search", "")
            company = filters.get("company")
            service = filters.get("service")
            
            mentors = self.mentors_service.get_mentors(
                search=search,
                company=company,
                service=service,
                limit=5
            )
            
            if mentors:
                data["mentors"] = mentors
        # Get relevant context based on the data for the RAG system
        context = self._build_context(intent, data)
        
        # Generate response using RAG
        response = self.rag.generate_response(query, context, chat_history)
        
        return {
            "response": response,
            "intent": intent,
            "filters": filters,
            "data": data
        }
    
    # Modified _detect_intent method in llm_service.py
    def _detect_intent(self, query):
        # Use Gemini to detect intent and extract search parameters
        prompt = f"""
        Analyze the following user query and determine if it's related to job searching, event searching, or mentor searching.
        If it's about job searching, extract search terms, location preferences, and whether remote work is mentioned.
        If it's about event searching, extract category interests and location preferences.
        If it's about mentor searching, extract search terms, company preferences, and service interests.
        
        User query: "{query}"
        
        For event searches:
        - Look for keywords like "event", "conference", "workshop", "webinar", "meetup"
        - Identify specific organizations mentioned (like "HerKey") as potential event categories
        - When a user mentions "virtual" after asking about events, understand they're looking for online events
        
        For mentor searches:
        - Look for keywords like "mentor", "coach", "advisor", "guidance", "career advice"
        - Extract company names if mentioned
        - Extract specific services like "resume review", "interview prep", "career transition"
        
        Respond in the following JSON format only:
        ```json
        {{
            "intent": "job_search" or "event_search" or "mentor_search" or "general",
            "filters": {{
                // For job_search:
                "search": "extracted job search terms or null",
                "location": "extracted location or null",
                "remote": true/false or null,
                
                // For event_search:  
                "category": "extracted category or null",
                "location": "extracted location or null",
                "mode": "virtual/online/in-person or null",
                
                // For mentor_search:
                "search": "extracted mentor search terms or null",
                "company": "extracted company or null", 
                "service": "extracted service or null"
            }}
        }}
        ```
        
        Don't include any explanation, just the JSON.
        """
        
        response = self.intent_model.generate_content(prompt)
        result_text = response.text
        
        # Extract the JSON part
        if "```json" in result_text:
            json_part = result_text.split("```json")[1].split("```")[0].strip()
        else:
            json_part = result_text.strip()
            
        try:
            return json.loads(json_part)
        except:
            # Default return if parsing fails
            return {"intent": "general", "filters": {}}
    
    def _build_context(self, intent, data):
        """Build context for RAG system based on intent and fetched data"""
        context_lines = []
        
        if intent == "job_search":
            if "jobs" in data and data["jobs"]:
                jobs = data["jobs"]
                context_lines.append(f"Found {len(jobs)} relevant jobs:")
                
                for job in jobs:
                    job_desc = f"- {job['role']} at {job['company_name']}"
                    if job.get('location'):
                        job_desc += f" ({job['location']})"
                    if job.get('remote'):
                        job_desc += " (Remote)"
                    context_lines.append(job_desc)
                    
                    # Add key details to context
                    if job.get('salary'):
                        context_lines.append(f"  Salary: {job['salary']}")
                    if job.get('hire_time'):
                        context_lines.append(f"  Hiring Timeline: {job['hire_time']}")
                    if job.get('text'):
                        # Use the text directly without cleaning
                        short_desc = job['text'][:150] + "..." if len(job['text']) > 150 else job['text']
                        context_lines.append(f"  Description: {short_desc}")
            else:
                context_lines.append("No matching jobs found. Consider broadening your search criteria.")
                
        elif intent == "event_search":
            if "events" in data and data["events"]:
                events = data["events"]
                context_lines.append(f"Found {len(events)} relevant events:")
                
                for event in events:
                    context_lines.append(f"- {event['name']} at {event['location']} ({event['start_date']} to {event['end_date']})")
                    context_lines.append(f"  Mode: {event['mode']}, Time: {event['timing']}")
                    
                    if 'categories' in event and event['categories']:
                        context_lines.append(f"  Categories: {', '.join(event['categories'])}")
                    
                    if event.get('about'):
                        # Use the about text directly without cleaning
                        short_about = event['about'][:150] + "..." if len(event['about']) > 150 else event['about']
                        context_lines.append(f"  About: {short_about}")
            else:
                context_lines.append("No matching events found. Consider broadening your search criteria.")
        
        elif intent == "mentor_search":
            if "mentors" in data and data["mentors"]:
                mentors = data["mentors"]
                context_lines.append(f"Found {len(mentors)} relevant mentors:")
                
                for mentor in mentors:
                    mentor_desc = f"- {mentor['name']}, {mentor['role']} at {mentor['company']}"
                    context_lines.append(mentor_desc)
                    
                    if mentor.get('bookings'):
                        context_lines.append(f"  Bookings: {mentor['bookings']}")
                    
                    if mentor.get('services') and len(mentor['services']) > 0:
                        services = [service.strip() for service in mentor['services']]
                        context_lines.append(f"  Services: {', '.join(services)}")
            else:
                context_lines.append("No matching mentors found. Consider broadening your search criteria.")

        return "\n".join(context_lines)
