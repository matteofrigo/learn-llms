import logging

from src.agent import Agent
from src.llm import get_llm_chat_obj
from src.prompt_registry import PromptRegistry
from src.tools import get_weather_data_stub, get_weather_open_meteo

logger = logging.getLogger('WEATHER_AGENT')
logger.setLevel(logging.DEBUG)
# stream output of logger to stdout
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

registry = PromptRegistry(root="/home/learn-llms/01-agent-weather/prompts")
llm = get_llm_chat_obj()

# tools = {"get_weather_data": get_weather_data_stub}
tools = {"get_weather_data": get_weather_open_meteo}
skills = {"format_weather_data"}

agent = Agent(registry=registry, llm=llm, tools=tools)

question = "What's the weather like in Venezia?"
answer = agent.run(question)
print('Question:', question)
print('Answer:', answer)
