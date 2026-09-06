from typing import Dict, Iterator, List

from .base import LLMProvider, ProviderEvent


class ProviderManager:
    """
    Orquesta una lista ordenada de providers (primario primero). Si el
    primario falla antes de producir cualquier salida, cambia automáticamente
    al siguiente. Si falla a mitad de una respuesta ya iniciada, reporta el
    error en vez de reintentar (para no duplicar/corromper la respuesta).
    """

    def __init__(self, providers: List[LLMProvider]):
        if not providers:
            raise ValueError("ProviderManager necesita al menos un provider")
        self.providers = providers

    def stream_chat(self, system_prompt: str, history: List[Dict], tools_schema: List[Dict]) -> Iterator[ProviderEvent]:
        last_error = None

        for i, provider in enumerate(self.providers):
            is_last = i == len(self.providers) - 1
            gen = provider.stream_chat(system_prompt, history, tools_schema)

            try:
                first = next(gen)
            except StopIteration:
                continue
            except Exception as e:
                last_error = e
                if is_last:
                    yield ("text", f"\n[Error: todos los providers fallaron. Último ({provider.name}): {e}]\n")
                    yield ("done", {"full_text": "", "tool_calls": []})
                    return
                yield ("text", f"[{provider.name} no disponible ({e}), usando fallback...]\n")
                continue

            yield first
            try:
                for item in gen:
                    yield item
            except Exception as e:
                yield ("text", f"\n[Error a mitad de respuesta con {provider.name}: {e}]\n")
                yield ("done", {"full_text": "", "tool_calls": []})
            return

        # Todos los providers agotaron su generador sin producir nada.
        yield ("done", {"full_text": "", "tool_calls": []})
