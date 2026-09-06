import json
import os
from typing import Dict, Iterator, List

import anthropic

from .base import LLMProvider, ProviderEvent


def _convert_history_to_anthropic(history: List[Dict]) -> List[Dict]:
    """
    Convierte el historial canónico (role user/assistant/tool, tool_calls en
    mensajes assistant) al formato de mensajes de Anthropic (bloques de
    contenido, tool_use / tool_result).
    """
    messages: List[Dict] = []
    pending_tool_results: List[Dict] = []

    def flush_tool_results():
        if pending_tool_results:
            messages.append({"role": "user", "content": pending_tool_results.copy()})
            pending_tool_results.clear()

    for msg in history:
        role = msg.get("role")

        if role == "tool":
            pending_tool_results.append({
                "type": "tool_result",
                "tool_use_id": msg["tool_call_id"],
                "content": str(msg["content"]),
            })
            continue

        flush_tool_results()

        if role == "assistant":
            blocks = []
            content = msg.get("content")
            if content:
                blocks.append({"type": "text", "text": content})
            for tc in msg.get("tool_calls") or []:
                try:
                    args = json.loads(tc["function"]["arguments"] or "{}")
                except Exception:
                    args = {}
                blocks.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["function"]["name"],
                    "input": args,
                })
            if not blocks:
                # Anthropic rechaza bloques de texto vacíos: un turno assistant sin
                # contenido ni tool_calls (ej. un intento previo que falló del todo)
                # necesita un placeholder no-vacío para seguir siendo un mensaje válido.
                blocks = [{"type": "text", "text": "(sin respuesta)"}]
            messages.append({"role": "assistant", "content": blocks})
            continue

        # role == "user"
        content = msg.get("content")
        if isinstance(content, str):
            messages.append({"role": "user", "content": content or "(mensaje vacío)"})
        elif isinstance(content, list):
            blocks = []
            for item in content:
                if item.get("type") == "text":
                    if item["text"]:
                        blocks.append({"type": "text", "text": item["text"]})
                elif item.get("type") == "image_url":
                    url = item["image_url"]["url"]
                    if url.startswith("data:"):
                        header, b64data = url.split(",", 1)
                        media_type = header.split(";")[0].replace("data:", "")
                        blocks.append({
                            "type": "image",
                            "source": {"type": "base64", "media_type": media_type, "data": b64data},
                        })
                    else:
                        blocks.append({"type": "image", "source": {"type": "url", "url": url}})
            if not blocks:
                blocks = [{"type": "text", "text": "(mensaje vacío)"}]
            messages.append({"role": "user", "content": blocks})
        else:
            messages.append({"role": "user", "content": str(content) or "(mensaje vacío)"})

    flush_tool_results()
    return messages


class AnthropicProvider(LLMProvider):
    """Backend principal: API de Anthropic (Claude). Extended thinking activado."""

    name = "anthropic"

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
        self.max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", "8000"))
        self.effort = os.getenv("ANTHROPIC_EFFORT", "high")

    def stream_chat(self, system_prompt, history, tools_schema) -> Iterator[ProviderEvent]:
        messages = _convert_history_to_anthropic(history)

        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            thinking={"type": "adaptive", "display": "summarized"},
            output_config={"effort": self.effort},
            tools=tools_schema,
            messages=messages,
        ) as stream:
            for event in stream:
                if event.type == "content_block_delta" and event.delta.type == "text_delta":
                    yield ("text", event.delta.text)
            final_message = stream.get_final_message()

        full_text = "".join(b.text for b in final_message.content if b.type == "text")
        tool_calls = []
        for b in final_message.content:
            if b.type == "tool_use":
                tool_calls.append({
                    "id": b.id,
                    "type": "function",
                    "function": {"name": b.name, "arguments": json.dumps(b.input, ensure_ascii=False)},
                })

        yield ("done", {"full_text": full_text, "tool_calls": tool_calls})
