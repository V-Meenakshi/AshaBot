import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")  # Note: Match the variable name with .env
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# RAG Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50