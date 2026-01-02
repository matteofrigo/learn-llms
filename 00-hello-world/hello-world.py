import os

from mistralai import Mistral


def get_response(question: str) -> str:
    if question is None:
        question = "Who is the best French painter? Answer in one short sentence"

    messages = [
        {"role": "user", "content": question}
    ]
    model = "ministral-8b-latest"

    with Mistral(api_key=os.getenv("MISTRAL_API_KEY", ""),) as mistral:

        res = mistral.chat.complete(
            model=model,
            messages=messages,
            stream=False,
            response_format={
                "type": "text",
            })

    return res.choices[0].message.content


if __name__ == "__main__":
    question = "Who is the best Italian and French painter? Answer in one short sentence"
    answer = get_response(question)
    print('Question:', question)
    print('Answer:', answer)
