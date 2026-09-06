import json
import os
from typing import Dict, Iterator, List

import requests

from .base import LLMProvider, ProviderEvent


class LMStudioProvider(LLMProvider):
    """Backend local vía LM Studio (API compatible con OpenAI). Usado como fallback."""

    name = "lmstudio"

    def __init__(self):
        self.base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
        self.model = os.getenv("LMSTUDIO_MODEL", "qwen/qwen3-4b-thinking-2507")
        self.max_tokens = int(os.getenv("LMSTUDIO_MAX_TOKENS", "4000"))

    @staticmethod
    def _tools_to_openai(tools_schema: List[Dict]) -> List[Dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t["input_schema"],
                },
            }
            for t in tools_schema
        ]

    def stream_chat(self, system_prompt, history, tools_schema) -> Iterator[ProviderEvent]:
        messages = [{"role": "system", "content": system_prompt}] + history
        tools = self._tools_to_openai(tools_schema)
        tool_accum: Dict[int, Dict] = {}
        full_response = ""

        with requests.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "max_tokens": self.max_tokens,
                "stream": True,
            },
            stream=True,
            timeout=120,
        ) as resp:
            resp.raise_for_status()

            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if not payload or payload == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                except Exception:
                    continue
                if chunk.get("error"):
                    raise RuntimeError(f'LM Studio: {chunk["error"]}')
                choices = chunk.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}

                text = delta.get("content")
                if text:
                    full_response += text
                    yield ("text", text)

                for tc in delta.get("tool_calls") or []:
                    idx = tc.get("index", 0)
                    entry = tool_accum.setdefault(idx, {"id": None, "name": "", "arguments": ""})
                    if tc.get("id"):
                        entry["id"] = tc["id"]
                    fn = tc.get("function") or {}
                    if fn.get("name"):
                        entry["name"] = fn["name"]
                    if fn.get("arguments"):
                        entry["arguments"] += fn["arguments"]

        tool_calls = []
        for idx in sorted(tool_accum):
            e = tool_accum[idx]
            if not e["name"]:
                continue
            tool_calls.append({
                "id": e["id"] or f"call_{idx}",
                "type": "function",
                "function": {"name": e["name"], "arguments": e["arguments"] or "{}"},
            })

        yield ("done", {"full_text": full_response, "tool_calls": tool_calls})
