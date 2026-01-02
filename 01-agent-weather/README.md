## Scenario
* AI Agent that answers weather questions by calling a weather tool.
* Uses Mistral's chat API.
* Example of RAG (Retrieval-Augmented Generation) pattern that uses an API to get real weather data in real time.

## How it works
- `main.py` loads a `PromptRegistry`, creates a Mistral chat client, registers the `get_weather_data` tool into the agent, and runs the agent on “What's the weather like in Nice (France)?”.
- `src/agent.py` loops by asking asks the `agent_router` prompt what to do, parses the JSON decision, either returns a final answer or calls a tool, and logs each step.
- `src/tools.py#get_weather_data` is a stub that returns fake weather data; swap it with a real API call to make the agent useful.
- `prompts/registry.yaml` maps environments to prompt versions.

## Setup
1) Install dependencies: `pip install mistralai pydantic pyyaml`
2) Export your key: `export MISTRAL_API_KEY=your_key_here`

## Run
- From the repo root: `python 01-agent-weather/main.py`
- To ask a different question, edit the `agent.run(...)` call in `main.py`.
