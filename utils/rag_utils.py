# utils/rag_utils.py
import google.generativeai as genai
from config import GEMINI_API_KEY, CHUNK_SIZE, CHUNK_OVERLAP

class RAGSystem: 
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def generate_response(self, query, context, chat_history=None):
        # Enhanced RAG implementation
        prompt = self._create_prompt(query, context, chat_history)
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def _create_prompt(self, query, context, chat_history=None):
        # Create a prompt with context and chat history
        history_text = ""
        if chat_history and len(chat_history) > 0:
            history_text = "Previous conversation:\n"
            for i, (q, a) in enumerate(chat_history[-3:]):  # Use last 3 exchanges
                history_text += f"User: {q}\nAsha: {a}\n"
        
        prompt = f"""
You are Asha, an AI assistant designed specifically to help women with career advice, job listings, and professional events.
Be empathetic, supportive, and provide practical guidance.

Key behaviors:
1. Always be conversational and helpful
2. When discussing jobs or events, provide specific details like company names, locations, and dates
3. If asked about jobs, encourage users to ask for specific job types, locations, or if they want remote work
4. If asked about events, mention categories and locations for more targeted results
5. When providing career advice, be empathetic and practical

{history_text}

Relevant information:
{context}

User query: {query}

Respond as Asha in a helpful, empathetic way. Focus on providing accurate information based on the context.
If you're suggesting events or jobs, mention specific details that would be relevant.
If you don't have enough information, ask clarifying questions to better help the user.
"""
        return prompt
