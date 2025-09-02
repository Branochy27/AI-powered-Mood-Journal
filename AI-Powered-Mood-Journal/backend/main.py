from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn
from database import Database
from ai_sentiment import SentimentAnalyzer
from auth import get_current_user

app = FastAPI(title="Mood Journal API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = Database()
sentiment_analyzer = SentimentAnalyzer()

# Pydantic models
class MoodEntry(BaseModel):
    text: str
    date: str
    time: str

class MoodResponse(BaseModel):
    id: int
    text: str
    date: str
    time: str
    sentiment: dict
    timestamp: datetime

@app.get("/")
def read_root():
    return {"message": "Mood Journal API is running"}

@app.post("/api/mood/analyze")
async def analyze_mood(entry: MoodEntry):
    """Analyze mood from text using AI"""
    try:
        sentiment = await sentiment_analyzer.analyze(entry.text)
        return {"sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mood/entry")
async def create_entry(entry: MoodEntry, user=Depends(get_current_user)):
    """Create a new mood journal entry"""
    try:
        sentiment = await sentiment_analyzer.analyze(entry.text)
        entry_id = db.create_entry(
            user_id=user["id"],
            text=entry.text,
            date=entry.date,
            time=entry.time,
            sentiment=sentiment
        )
        return {"id": entry_id, "sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mood/history")
async def get_history(user=Depends(get_current_user)):
    """Get user's mood history"""
    try:
        entries = db.get_user_entries(user["id"])
        return {"entries": entries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights/trends")
async def get_trends(user=Depends(get_current_user)):
    """Get mood trends and insights"""
    try:
        trends = db.get_mood_trends(user["id"])
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)