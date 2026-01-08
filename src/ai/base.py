# src/ai/base.py
from abc import ABC, abstractmethod

class AIPlatform(ABC):
    @abstractmethod
    def chat(self, prompt: str) -> str:
        """Generate text based on the given prompt."""
        pass

