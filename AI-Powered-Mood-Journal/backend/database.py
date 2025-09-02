import os
from supabase import create_client, Client
from datetime import datetime
import json

class Database:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        self.supabase: Client = create_client(url, key)
    
    def create_entry(self, user_id, text, date, time, sentiment):
        """Create a new mood entry"""
        data = {
            "user_id": user_id,
            "text": text,
            "date": date,
            "time": time,
            "sentiment": json.dumps(sentiment),
            "created_at": datetime.now().isoformat()
        }
        response = self.supabase.table("mood_entries").insert(data).execute()
        return response.data[0]["id"]
    
    def get_user_entries(self, user_id, limit=50):
        """Get user's mood entries"""
        response = self.supabase.table("mood_entries") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        
        entries = []
        for entry in response.data:
            entry["sentiment"] = json.loads(entry["sentiment"])
            entries.append(entry)
        return entries
    
    def get_mood_trends(self, user_id):
        """Calculate mood trends for user"""
        entries = self.get_user_entries(user_id, limit=100)
        
        if not entries:
            return {"message": "No data available"}
        
        trends = {
            "daily": [],
            "weekly": [],
            "monthly": [],
            "overall": {
                "positive": 0,
                "neutral": 0,
                "negative": 0
            }
        }
        
        for entry in entries:
            sentiment = entry["sentiment"]
            # Calculate overall sentiment
            if sentiment["positive"] > sentiment["negative"]:
                trends["overall"]["positive"] += 1
            elif sentiment["negative"] > sentiment["positive"]:
                trends["overall"]["negative"] += 1
            else:
                trends["overall"]["neutral"] += 1
        
        return trends