# src/main.py
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.auth.throttling import apply_rate_limit
from src.ai.gemini import Gemini

app = FastAPI()

# --- CORS ---
# 你可以先用 onrender.com + 本機，等前端正式網域出來再收斂
origins = [
    "http://localhost:5173",
    "https://gemini-chatbot-demo-frontend.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_system_prompt() -> str | None:
    try:
        base_dir = Path(__file__).resolve().parent  # .../src
        prompt_path = base_dir / "prompts" / "system_prompt.md"
        return prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None

system_prompt = load_system_prompt()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# 注意：不要在 import 時 raise，避免 Render 啟動直接死掉
ai_platform = None
if gemini_api_key:
    ai_platform = Gemini(api_key=gemini_api_key, system_prompt=system_prompt)
else:
    print("⚠️ Warning: GEMINI_API_KEY is not set in environment variables.")

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    apply_rate_limit("global_unauthenticated_user")

    if not gemini_api_key or ai_platform is None:
        raise HTTPException(
            status_code=500, 
            detail="Gemini API is not configured. Please check environment variables."
        )

    try:
        response_text = await run_in_threadpool(ai_platform.chat, request.prompt)
        return ChatResponse(response=response_text)
    except Exception as e:
        print("Error in /chat:", repr(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    return {"message": "API is running!"}
