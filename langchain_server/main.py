from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import pytesseract
from PIL import Image
import io
from PyPDF2 import PdfReader
from chatAgent import MentalHealthChatAgent

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# llm = ChatOpenAI(
#     model="gpt-3.5-turbo",
#     temperature=0,
#     api_key=os.getenv("OPENAI_API_KEY")
# )

class ChatInput(BaseModel):
    message: str

agent=MentalHealthChatAgent()


@app.post("/chat")
async def chat(input: ChatInput):
    try:
        # response = llm.invoke(input.message)
        # return {"reply": response.content}
        return {"reply": agent.get_reply(input.message)}
    except Exception as e:
        print("❌ Error:", e)
        return {"reply": "Sorry, I encountered an error."}



@app.post("/end_session")
async def end_session(request: Request):
    try:
        body = await request.json()
        username = body.get('username', 'Unknown')  
        print(f"Session ended for user: {username}") 
        return {"reply": agent.end_session()}
    except Exception as e:
        print("❌ Error:", e)
        return {"reply": "Sorry, I encountered an error."}


