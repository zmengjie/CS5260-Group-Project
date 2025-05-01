from fastapi import FastAPI, UploadFile, File
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

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    try:
        ext = file.filename.split('.')[-1].lower()
        content = ""

        if ext == 'txt':
            content = (await file.read()).decode('utf-8')

        elif ext in ['png', 'jpg', 'jpeg']:
            image = Image.open(io.BytesIO(await file.read()))
            content = pytesseract.image_to_string(image)

        elif ext == 'pdf':
            pdf_reader = PdfReader(file.file)
            content = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])

        else:
            return {"feedback": f"Unsupported file type: {ext}. Please upload .txt, .png, .jpg, or .pdf"}

        if not content.strip():
            return {"feedback": "Could not extract any readable content from your file."}

        # Optional: Use LLM to provide feedback
        result = llm.invoke(f"Please analyze the following psychological test result and give a brief summary: {content}")
        return {"feedback": result.content}

    except Exception as e:
        print("❌ OCR or parsing error:", e)
        return {"feedback": "Something went wrong during analysis."}

# Future route placeholder (for Whisper audio transcription)
@app.post("/whisper-transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    return {"text": "Voice transcription coming soon!"}
