from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import ollama

from app.testing.utils import extract_json_text


@dataclass
class LocalAgentLLM:
    model: str
    temperature: float = 0.2
    num_predict: int = 1200

    def complete(self, system_prompt: str, user_prompt: str, *, as_json: bool = False) -> str:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.num_predict,
            },
        }
        if as_json:
            kwargs["format"] = "json"

        response = ollama.chat(**kwargs)
        return response["message"]["content"]

    def complete_json(self, system_prompt: str, user_prompt: str) -> Any:
        raw = self.complete(system_prompt, user_prompt, as_json=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return json.loads(extract_json_text(raw))

