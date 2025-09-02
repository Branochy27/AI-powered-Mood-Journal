import os
import aiohttp
import asyncio
from typing import Dict

class SentimentAnalyzer:
    def __init__(self):
        self.api_key = os.environ.get("HUGGING_FACE_TOKEN")
        self.model = "nlptown/bert-base-multilingual-uncased-sentiment"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    async def analyze(self, text: str) -> Dict:
        """Analyze sentiment using Hugging Face API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url, 
                    headers=self.headers,
                    json={"inputs": text}
                ) as response:
                    result = await response.json()
                    
                    # Process the result
                    return self._process_sentiment(result, text)
        except Exception as e:
            # Fallback to local analysis if API fails
            return self._local_sentiment_analysis(text)
    
    def _process_sentiment(self, api_result, text):
        """Process API result into sentiment scores"""
        # Convert API result to our format
        sentiment_scores = {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "emotions": {
                "joy": 0,
                "sadness": 0,
                "anger": 0,
                "fear": 0,
                "surprise": 0
            }
        }
        
        # Process scores from API
        if isinstance(api_result, list) and len(api_result) > 0:
            for item in api_result[0]:
                label = item.get("label", "").lower()
                score = item.get("score", 0)
                
                if "positive" in label or "5" in label or "4" in label:
                    sentiment_scores["positive"] += score
                elif "negative" in label or "1" in label or "2" in label:
                    sentiment_scores["negative"] += score
                else:
                    sentiment_scores["neutral"] += score
        
        # Normalize scores
        total = sentiment_scores["positive"] + sentiment_scores["neutral"] + sentiment_scores["negative"]
        if total > 0:
            sentiment_scores["positive"] = (sentiment_scores["positive"] / total) * 100
            sentiment_scores["neutral"] = (sentiment_scores["neutral"] / total) * 100
            sentiment_scores["negative"] = (sentiment_scores["negative"] / total) * 100
        
        # Analyze emotions based on keywords
        sentiment_scores["emotions"] = self._analyze_emotions(text)
        
        return sentiment_scores
    
    def _analyze_emotions(self, text):
        """Analyze specific emotions from text"""
        text_lower = text.lower()
        emotions = {
            "joy": 0,
            "sadness": 0,
            "anger": 0,
            "fear": 0,
            "surprise": 0
        }
        
        # Keyword-based emotion detection
        joy_words = ["happy", "joy", "excited", "love", "wonderful", "amazing", "great"]
        sad_words = ["sad", "depressed", "lonely", "cry", "tears", "heartbroken"]
        anger_words = ["angry", "furious", "mad", "frustrated", "annoyed", "irritated"]
        fear_words = ["scared", "afraid", "anxious", "worried", "nervous", "terrified"]
        surprise_words = ["surprised", "shocked", "amazed", "astonished", "unexpected"]
        
        words = text_lower.split()
        for word in words:
            if any(jw in word for jw in joy_words):
                emotions["joy"] += 1
            if any(sw in word for sw in sad_words):
                emotions["sadness"] += 1
            if any(aw in word for aw in anger_words):
                emotions["anger"] += 1
            if any(fw in word for fw in fear_words):
                emotions["fear"] += 1
            if any(sw in word for sw in surprise_words):
                emotions["surprise"] += 1
        
        # Normalize emotion scores
        total_emotions = sum(emotions.values())
        if total_emotions > 0:
            for emotion in emotions:
                emotions[emotion] = (emotions[emotion] / total_emotions) * 100
        
        return emotions
    
    def _local_sentiment_analysis(self, text):
        """Fallback local sentiment analysis"""
        positive_words = ['happy', 'joy', 'love', 'excited', 'amazing', 'wonderful', 'great', 'fantastic', 'awesome', 'good', 'better', 'best', 'smile', 'laugh', 'grateful', 'thankful', 'blessed', 'peaceful']
        negative_words = ['sad', 'angry', 'hate', 'terrible', 'awful', 'bad', 'worse', 'worst', 'cry', 'upset', 'frustrated', 'anxious', 'depressed', 'lonely', 'worried', 'stressed']
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total = len(words)
        if total == 0:
            return {"positive": 33.3, "neutral": 33.3, "negative": 33.3}
        
        positive_score = (positive_count / total) * 100
        negative_score = (negative_count / total) * 100
        neutral_score = 100 - positive_score - negative_score
        
        return {
            "positive": max(0, min(100, positive_score)),
            "neutral": max(0, min(100, neutral_score)),
            "negative": max(0, min(100, negative_score)),
            "emotions": self._analyze_emotions(text)
        }