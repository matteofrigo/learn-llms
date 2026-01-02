import os

from mistralai import Mistral
from mistralai.chat import Chat

DEFAULT_MODEL = "ministral-8b-latest"


def get_llm_chat_obj() -> Chat:
    mistral = Mistral(api_key=os.getenv("MISTRAL_API_KEY", ""),)
    return mistral.chat


def get_response(
        question: str,
        model: str = DEFAULT_MODEL,
        memory: list = None) -> str:
    messages = [
        {"role": "user", "content": question}
    ]

    if memory:
        messages = memory + messages

    with Mistral(api_key=os.getenv("MISTRAL_API_KEY", ""),) as mistral:

        res = mistral.chat.complete(
            model=model,
            messages=messages,
            stream=False,
            response_format={
                "type": "text",
            })

    return res.choices[0].message.content
