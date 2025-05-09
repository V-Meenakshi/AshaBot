# Asha AI Chatbot

## Overview
Asha AI is an intelligent career assistant specifically designed for women, offering seamless access to job listings, community events, and mentorship programs. Built on a sophisticated retrieval-augmented generation (RAG) architecture with Neo4j graph database integration, Asha delivers context-aware, personalized guidance to support women's professional growth.

## Key Features

### 📊 Smart Data Retrieval
- **Job Search**: Find relevant positions based on role, location, and remote work preferences
- **Event Discovery**: Access upcoming workshops, conferences, and networking opportunities
- **Mentor Matching**: Connect with industry professionals for career guidance

### 🤖 Intelligent Conversation
- **Context-Aware Responses**: Maintains conversation history to provide coherent follow-ups
- **Intent Detection**: Identifies user needs through advanced query analysis
- **Empathetic Guidance**: Offers supportive career advice tailored to women's professional journeys

### 🔐 Secure Platform
- **User Authentication**: Ensures personalized and secure experiences
- **Privacy-First Design**: Handles sensitive career information responsibly

## Architecture

### Backend (FastAPI)
The application uses FastAPI to create RESTful endpoints that handle user authentication, chat processing, and data retrieval:
- `/chat`: Processes user queries and returns AI-generated responses with relevant data
- `/jobs`, `/events`, `/mentors`: Dedicated endpoints for filtered data retrieval
- `/users`: Handles user registration and authentication

### Data Layer (Neo4j)
Leverages Neo4j graph database for efficient storage and retrieval of interconnected career data:
- **Graph-Based Storage**: Models relationships between jobs, companies, events, locations, and mentors
- **Semantic Search**: Enables powerful contextual queries across the knowledge graph

### AI Component
Utilizes Google's Gemini models for natural language understanding and generation:
- **Intent Detection**: Gemini 1.5 Flash model for efficient query classification
- **Response Generation**: Gemini 1.5 Pro model for comprehensive, helpful responses
- **RAG System**: Augments AI responses with relevant retrieval from the knowledge base

### Frontend (Streamlit)
Features an intuitive chat interface with:
- **Responsive UI**: Clean, accessible design for seamless interaction
- **Interactive Elements**: Example queries, expandable result sections
- **Secure Authentication**: Login and registration flows

## Setup Instructions

### Prerequisites
- Python 3.8+
- Neo4j Database
- Google API Key (for Gemini models)

### Installation
1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```
   NEO4J_URI=<your-neo4j-uri>
   NEO4J_USER=<your-neo4j-username>
   NEO4J_PASSWORD=<your-neo4j-password>
   GEMINI_API_KEY=<your-gemini-api-key>
   ```

### Running the Application
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Start the FastAPI backend:
   ```
   uvicorn main:app --reload
   ```
3. Launch the Streamlit frontend:
   ```
   streamlit run streamlit_app.py
   ```

## Project Structure
```
asha-ai-chatbot/
├── database/
│   └── neo4j_db.py         # Neo4j database connector
├── services/
│   ├── auth_service.py     # Authentication service
│   ├── events_service.py   # Events data service
│   ├── jobs_service.py     # Jobs data service 
│   ├── llm_service.py      # LLM integration service
│   └── mentors_service.py  # Mentors data service
├── utils/
│   └── rag_utils.py        # RAG implementation
├── main.py                 # FastAPI application
├── streamlit_app.py        # Streamlit frontend
├── config.py               # contains Neo4J Aura details
├── .env                    # contains API key
└── requirements.txt        # Project dependencies
```

## Future Enhancements
- **Personalized Recommendations**: Learning from user interactions to suggest relevant opportunities
- **Advanced Filtering**: More granular search options for jobs and events
- **Resume Analysis**: AI-powered feedback on resume content and structure
- **Interview Preparation**: Customized guidance for interview success
- **Mobile Application**: Native mobile experience for on-the-go career assistance
- **Production Deployment**: Scalable cloud infrastructure for public access

## Ethics and Inclusion
Asha AI is built on ethical AI principles that emphasize:
- **Gender Bias Mitigation**: Carefully designed to avoid reinforcing stereotypes
- **Accessibility**: Interface designed to be inclusive and user-friendly
- **Transparency**: Clear disclosure of AI capabilities and limitations
- **Privacy**: Responsible handling of user data and career information

## About
Developed for the JobsForHer Foundation to enhance user engagement and provide better access to career resources for women professionals. Asha AI aims to make career advancement resources more accessible, personalized, and effective.


