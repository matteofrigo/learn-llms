## Scenario
Hello world example that calls Mistral's chat API from Python. It asks the model who the best Italian and French painters are.

## How it works
- `hello-world.py` defines `get_response(question)` which sends a single user message to the `ministral-8b-latest` model via the `mistralai` client.
- It pulls the API key from `MISTRAL_API_KEY` and returns the first completion's content.

## Setup
1) Install the Mistral SDK: `pip install mistralai`
2) Export your API key: `export MISTRAL_API_KEY=your_key_here`

## Run it
- From the repo root: `python 00-hello-world/hello-world.py`
### Example
```
((venv) ) root@e663ea224db1:/home/learn-llms# /opt/venv/bin/python /home/learn-llms/00-hello-world/hello-world.py
Question: Who is the best Italian and French painter? Answer in one short sentence
Answer: The **best Italian painter** is **Leonardo da Vinci**, while the **best French painter** is **Claude Monet**.
```