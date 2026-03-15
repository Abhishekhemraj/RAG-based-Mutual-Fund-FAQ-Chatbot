import os
from groq import Groq
import sys

# Ensure parent folder for config is available
sys.path.append(os.getcwd())
from core import rag_config as config

class GroqRAGHandler:
    """Handles communication with Groq LLM using strict RAG constraints."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or config.GROQ_API_KEY
        if not self.api_key:
            raise ValueError("Groq API Key not found. Please add 'GROQ_API_KEY=your_key_here' to your .env file in the project root.")
        self.client = Groq(api_key=self.api_key)

    def generate_response(self, query, context_chunks):
        """Constructs the grounding prompt and generates a response."""
        
        if not context_chunks:
            return "The requested information is not available in the current knowledge base.\n\n"
        
        # Combine context chunks for LLM context
        context_text = "\n---\n".join([c["content"] for c in context_chunks])
        
        # Determine the source URL (assuming multiple chunks share a source for simple FAQ)
        source_url = context_chunks[0].get("source_url", "Official Tata Mutual Fund Website")
        
        prompt = f"""RETRIEVED CONTEXT:
{context_text}

SOURCE LINK: {source_url}

USER QUERY:
{query}

INSTRUCTION: 
1. Use the 'RETRIEVED CONTEXT' to answer the 'USER QUERY'. 
2. Ensure you follow all system format rules, specifically ending with the 'SOURCE LINK'.
"""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": config.SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=config.GROQ_MODEL,
                temperature=config.TEMPERATURE,
            )
            
            answer = chat_completion.choices[0].message.content
            
            # Ensure the mandatory suffix is present if the LLM potentially missed it
            if "Last updated from sources:" not in answer:
                answer += f"\n\nLast updated from sources: {source_url}"
                
            return answer
            
        except Exception as e:
            return f"Error connecting to Groq: {str(e)}"
