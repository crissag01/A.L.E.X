from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Tuple

# Un evento es ("text", str) mientras se transmite texto,
# o ("done", {"full_text": str, "tool_calls": [...]}) al terminar el turno.
ProviderEvent = Tuple[str, Any]


class LLMProvider(ABC):
    """Interfaz común para cualquier backend de LLM (Anthropic, LM Studio, etc.)."""

    name: str = "base"

    @abstractmethod
    def stream_chat(
        self,
        system_prompt: str,
        history: List[Dict],
        tools_schema: List[Dict],
    ) -> Iterator[ProviderEvent]:
        """
        Recibe el historial en formato canónico (estilo OpenAI: role user/assistant/tool,
        tool_calls en mensajes assistant) y el schema de tools en formato Anthropic
        (name/description/input_schema). Traduce internamente a lo que su API necesite.
        """
        raise NotImplementedError
