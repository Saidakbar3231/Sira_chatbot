import asyncio
import itertools
import logging
from groq import Groq, RateLimitError

from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are SIRA (Specialized Intelligent Research Assistant), \
created by Sobirov Saidakbar, Biotechnology Master's student \
at National University of Uzbekistan, specializing in \
"Nematodalarga qarshi biopreparat yaratish texnologiyasi".

Rules:
- Always respond in the same language as the user
- I am an AI model specialized in the topic of "Nematodalarga qarshi biopreparat yaratish texnologiyasi" (Biopesticide creation technology against nematodes)
- Use RAG context when provided
- If off-topic, politely redirect to your specialty
"""

# Cyclic iterator over 3 Groq clients
_clients = [
    Groq(api_key=settings.GROQ_API_KEY_1),
    Groq(api_key=settings.GROQ_API_KEY_2),
    Groq(api_key=settings.GROQ_API_KEY_3),
]
_client_cycle = itertools.cycle(_clients)
_current_client = next(_client_cycle)


def _next_client() -> Groq:
    global _current_client
    _current_client = next(_client_cycle)
    return _current_client


async def ask_gemini(
    user_message: str,
    history: list[dict] | None = None,
    context: str = "",
) -> str:
    """Send a message to Groq with automatic key rotation on 429 errors."""
    system = SYSTEM_PROMPT
    if context:
        system += f"\n\nRelevant context from knowledge base:\n{context}"

    messages = [{"role": "system", "content": system}]
    if history:
        for entry in history:
            messages.append({"role": entry["role"], "content": entry["content"]})
    messages.append({"role": "user", "content": user_message})

    def _sync_call():
        global _current_client
        last_error = None
        for attempt in range(len(_clients)):
            try:
                response = _current_client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=messages,
                )
                return response.choices[0].message.content
            except RateLimitError as e:
                logger.warning(f"Rate limit on key #{attempt + 1}, rotating to next key.")
                last_error = e
                _current_client = _next_client()
        raise RuntimeError("All Groq API keys exhausted (rate limited).")

    return await asyncio.to_thread(_sync_call)
