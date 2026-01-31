from __future__ import annotations

import os
import json
from dataclasses import dataclass
from typing import Any, Literal, Optional

import requests


class LLMError(Exception):
    pass


@dataclass
class LLMConfig:
    backend: Literal["openai", "anthropic"] = "openai"
    model: str = ""
    temperature: float = 0.2
    max_tokens: int = 1200


class LLMClient:
    def __init__(self, cfg: LLMConfig):
        self.cfg = cfg

    @staticmethod
    def from_env(prefix: str = "TOWN_") -> "LLMClient":
        backend = os.getenv(prefix + "LLM_BACKEND", "openai").strip().lower()
        model = os.getenv(prefix + "LLM_MODEL", "").strip()
        temperature = float(os.getenv(prefix + "LLM_TEMPERATURE", "0.2"))
        max_tokens = int(os.getenv(prefix + "LLM_MAX_TOKENS", "1200"))
        if backend not in {"openai", "anthropic"}:
            raise LLMError(f"Unsupported backend {backend!r}. Use openai or anthropic.")
        return LLMClient(LLMConfig(backend=backend, model=model, temperature=temperature, max_tokens=max_tokens))

    def complete(self, *, system: str, user: str) -> str:
        if self.cfg.backend == "openai":
            return self._openai_chat(system=system, user=user)
        if self.cfg.backend == "anthropic":
            return self._anthropic_messages(system=system, user=user)
        raise LLMError(f"Unsupported backend {self.cfg.backend}")

    def _openai_chat(self, *, system: str, user: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise LLMError("OPENAI_API_KEY is not set")
        model = self.cfg.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "temperature": self.cfg.temperature,
            "max_tokens": self.cfg.max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        if r.status_code >= 400:
            raise LLMError(f"OpenAI API error {r.status_code}: {r.text[:500]}")
        data = r.json()
        try:
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise LLMError(f"Unexpected OpenAI response: {data}") from e

    def _anthropic_messages(self, *, system: str, user: str) -> str:
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise LLMError("ANTHROPIC_API_KEY is not set")
        model = self.cfg.model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
        url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1/messages")
        headers = {
            "x-api-key": api_key,
            "anthropic-version": os.getenv("ANTHROPIC_VERSION", "2023-06-01"),
            "content-type": "application/json",
        }
        payload = {
            "model": model,
            "max_tokens": self.cfg.max_tokens,
            "temperature": self.cfg.temperature,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        if r.status_code >= 400:
            raise LLMError(f"Anthropic API error {r.status_code}: {r.text[:500]}")
        data = r.json()
        try:
            # data['content'] is a list of blocks; text blocks have {'type':'text','text':...}
            blocks = data.get("content", [])
            texts = []
            for b in blocks:
                if b.get("type") == "text":
                    texts.append(b.get("text", ""))
            return "\n".join(texts).strip()
        except Exception as e:
            raise LLMError(f"Unexpected Anthropic response: {data}") from e
