# src/ai/gemini.py
# src/ai/gemini.py
from typing import Optional

from google import genai   # ✅ 新 SDK 的用法
from .base import AIPlatform


class Gemini(AIPlatform):
    def __init__(self, api_key: str, system_prompt: Optional[str] = None):
        self.system_prompt = system_prompt
        # 建立 client，之後都用它呼叫 API
        self.client = genai.Client(api_key=api_key)

        # 只記住模型名稱字串，不要用舊的 GenerativeModel 物件
        self.model_name = "gemini-2.5-flash"  # 或 "gemini-2.5-pro"

    def chat(self, prompt: str) -> str:
        if self.system_prompt:
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        # 新 SDK 的寫法：client.models.generate_content(...)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
        )

        return response.text
