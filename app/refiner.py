"""GPT-4o-mini refinement of transcribed text."""

import os
from openai import OpenAI

_client: OpenAI | None = None

SYSTEM_PROMPT = (
    "Você é um revisor especializado em transcrições de áudio em português. "
    "Corrija erros ortográficos e semânticos mantendo fidelidade máxima ao original. "
    "Preserve todos os marcadores `[...]` exatamente onde estão. "
    "Não acrescente nem remova conteúdo."
)


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(api_key=api_key)
    return _client


def refine(text: str) -> str:
    """Send text to GPT-4o-mini for orthographic/semantic correction.

    Preserves all [...] pause markers and does not add or remove content.
    """
    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content or text
