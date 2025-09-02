Set up the backend:

bashcd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Configure environment variables:

bashcp .env.example .env
# Edit .env with your credentials

Run the application:

bashuvicorn main:app --reload

Open frontend/index.html in your browser