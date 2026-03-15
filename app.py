from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
import json

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from core.main_engine import TataMF_Chatbot

app = FastAPI(title="Tata Mutual Fund FAQ Chatbot API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy Initialize Bot to prevent timeout on serverless boot
bot = None

def get_bot():
    global bot
    if bot is None:
        bot = TataMF_Chatbot()
    return bot

class QueryRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    status: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: QueryRequest):
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        response = get_bot().ask(request.query)
        return ChatResponse(answer=response, status="success")
    except Exception as e:
        return ChatResponse(answer=f"An error occurred: {str(e)}", status="error")

@app.get("/metadata")
async def get_metadata():
    metadata_path = "data/structured/courses.json"
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            return json.load(f)
    return {"metadata": {"last_updated": "Unavailable"}}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Serve static files locally (Vercel handles this via vercel.json)
if os.getenv("VERCEL") != "1":
    app.mount("/", StaticFiles(directory="ui", html=True), name="ui")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
