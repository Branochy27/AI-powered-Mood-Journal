// Add this to connect frontend with backend API
const API_BASE_URL = 'http://localhost:8000';

async function analyzeWithAPI(text) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/mood/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ text, date, time })
        });
        
        if (!response.ok) throw new Error('API request failed');
        
        const data = await response.json();
        return data.sentiment;
    } catch (error) {
        console.error('API Error:', error);
        // Fallback to local analysis
        return localSentimentAnalysis(text);
    }
}