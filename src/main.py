# src\main.py
import os 
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
# from .ai.gemini import Gemini
from src.auth.throttling import apply_rate_limit
from src.ai.gemini import Gemini
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
origins = [
    "http://localhost:5173",  # Vite dev server
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # 正式環境不要用 ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_system_prompt() :
    try:
        with open("src/prompts/system_prompt.md", "r", encoding="utf-8") as file:
             return file.read().strip()
    except FileNotFoundError:
        return None
    
system_prompt = load_system_prompt()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

ai_platform = Gemini(api_key=gemini_api_key, system_prompt=system_prompt)

class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    response: str



from fastapi import HTTPException
# 上面 import 區塊記得多這一行

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    apply_rate_limit("global_unauthenticated_user")
    response_text = ai_platform.chat(request.prompt)
    return ChatResponse(response=response_text)
    try:
        response_text = await run_in_threadpool(ai_platform.chat, request.prompt)
        return ChatResponse(response=response_text)
    except Exception as e:
        # 先把錯誤內容印到 console，方便你在 terminal 看到
        print("Error in /chat:", repr(e))
        # 再把錯誤訊息回傳給客戶端，暫時用來 debug
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/")
async def root():
    return {"message": "API is running!"}


# system_prompt = load_system_prompt()
# gemini_api_key = os.getenv("GEMINI_API_KEY")

# ai_platform = Gemini(api_key=gemini_api_key, system_prompt=system_prompt)