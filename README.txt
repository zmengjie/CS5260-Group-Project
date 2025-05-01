
🌸 Luma – Your Empathetic Companion
==================================

Luma is an AI-powered mental wellness chatbot that combines a soothing UI with emotional intelligence features like mood detection, calming themes, guided breathing and more.

🛠 Setup Instructions
---------------------

🚀 Running the Application
--------------------------

1. Start the Backend (FastAPI)

    cd langchain_server
    pip install -r requirements.txt
    
    uvicorn main:app --reload --port 8000
    or /opt/anaconda3/bin/python -m uvicorn main:app --reload --port 8000 to force uvicorn to run under your Anaconda Python


    > Ensure you have an `.env` file in `langchain_server` with your OpenAI key:
    OPENAI_API_KEY=sk-xxx

2. Start the Frontend (React)

    cd client
    npm install
    npm start

    > The frontend runs on http://localhost:3001 and talks to the backend on http://127.0.0.1:8000

✨ Features Overview
--------------------

| Feature                        | Description                                                                 |
|-------------------------------|-----------------------------------------------------------------------------|
| 🎨 Calming Themes             | Switch between gentle themes like Dream, Ocean, Forest, and Dusk.         |
| 🎵 Background Music           | Choose background audio like piano, ocean waves, or forest ambience.       |
| 👤 Avatar Support             | Visual avatars for the user and the AI companion ("Luma").                 |
| 💬 Empathetic Conversations   | Tone-softened replies tuned for emotional support.                         |
| 🌬 Breathing Guide            | Trigger short mindfulness breathing prompts.                               |
| 📈 Mood Detection             | Luma detects your mood and tracks it through session colors.               |
| 🧠 Onboarding Flow            | Intro animations & user-friendly guided entry screen with Lottie.          |
| 🌙 Dark Mode                  | Switch to a night-themed calming mode.         
                            

📂 Backend API Endpoints
-------------------------

| Route               | Method | Description                                      |
|--------------------|--------|--------------------------------------------------|
| `/chat`            | POST   | Send a message to Luma and receive a reply.      |



🤖 Tech Stack
--------------
- Frontend: React, Axios, Lottie, CSS
- Backend: FastAPI, LangChain, OpenAI API


