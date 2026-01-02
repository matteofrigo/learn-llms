import json
import logging
from typing import Literal, Optional

from pydantic import BaseModel, Field

from . import llm as llm_module
from .prompt_registry import PromptRegistry


class AgentConfig(BaseModel):
    env: str = "dev"
    max_steps: int = 5
    temperature: float = 0.2
    router_skill: str = "agent_router"


class AgentState(BaseModel):
    user_input: str
    memory: list = Field(default_factory=list)
    trace: list = Field(default_factory=list)


class AgentDecision(BaseModel):
    kind: Literal["final", "tool"]

    # if kind == "final", this field will be read
    final: Optional[str] = None

    # if kind == "tool", these fields will be read
    tool_name: Optional[str] = None
    tool_args: Optional[dict] = Field(default_factory=dict)


class Agent:
    def __init__(
            self,
            registry: PromptRegistry,
            llm: llm_module.Chat = None,
            tools: dict = None,
            skills: dict = None,
            config: AgentConfig = None):
        self.registry = registry
        self.llm = llm or llm_module.get_llm_chat_obj()
        self.tools = tools or {}
        self.skills = skills or {}
        self.config = config or AgentConfig()

        self.logger = logging.getLogger('WEATHER_AGENT')

    def _safe_json_parse(self, text: str) -> dict:
        # minimal: expect JSON in the response
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Model did not return valid JSON. Got:\n{text}") from e

    def run(self, user_input: str) -> str:
        state = AgentState(user_input=user_input)

        for step in range(self.config.max_steps):
            self.logger.info(f"{step=}, {state=}")

            # ask router what to do next
            router_prompt = self.registry.load_prompt(
                self.config.router_skill, env=self.config.env)

            messages = router_prompt.render_messages(
                user_input=state.user_input,
                memory=json.dumps(state.memory),
                trace=json.dumps(state.trace),
                step=step,
                max_steps=self.config.max_steps,
                available_tools=list(self.tools.keys()),
            )

            router_reply_raw = self.llm.complete(
                model=llm_module.DEFAULT_MODEL,
                messages=messages,
                temperature=self.config.temperature,
                stream=False,
                response_format={"type": "text"},
            )

            decision_dict = self._safe_json_parse(
                router_reply_raw.choices[0].message.content)
            decision = AgentDecision.model_validate(decision_dict)
            self.logger.info(f"Router decision: {decision_dict}")
            state.trace.append({"step": step, "decision": decision_dict})

            # execute the decision
            if decision.kind == "final":
                # if it's final, we expect the answer to be written in `final`
                if not decision.final:
                    raise ValueError(
                        "Decision kind=final but `final` is empty.")
                return decision.final

            if decision.kind == "tool":
                # if it's a tool, run it and UPDATE MEMORY, o/wise it's pointless to run the tool ...
                if not decision.tool_name:
                    raise ValueError(
                        "Decision kind=tool but `tool_name` is empty.")
                if decision.tool_name not in self.tools:
                    raise ValueError(f"Unknown tool: {decision.tool_name}")

                result = self.tools[decision.tool_name](
                    **(decision.tool_args or {}))
                state.memory.append({decision.tool_name: result})
                state.trace.append(
                    {"step": step, "tool": decision.tool_name, "result": result})
                self.logger.info(
                    f"Tool {decision.tool_name} returned: {result}")
                continue

            if decision.kind == "skill":
                # if it's a skill, load the corresponding prompt, complete it, and update memory
                if not decision.skill_name:
                    raise ValueError(
                        "Decision kind=skill but `skill_name` is empty.")
                if decision.skill_name not in self.skills:
                    raise ValueError(f"Unknown skill: {decision.skill_name}")

                skill_prompt = self.registry.load_prompt(
                    decision.skill_name, env=self.config.env)

                # Skill args come from router decision; also provide state.memory as context
                skill_args = dict(decision.skill_args or {})
                skill_args["user_input"] = state.user_input
                skill_args["memory"] = json.dumps(state.memory)
                skill_messages = skill_prompt.render_messages(**skill_args)

                skill_reply_raw = self.llm.complete(
                    model=llm_module.DEFAULT_MODEL,
                    messages=skill_messages,
                    temperature=self.config.temperature,
                    stream=False,
                    response_format={"type": "text"},
                )

                # Store skill output in memory under skill name (simple convention)
                state.memory.append({decision.skill_name: skill_reply_raw})
                state.trace.append(
                    {"step": step, "skill": decision.skill_name, "skill_raw": skill_reply_raw})
                self.logger.info(
                    f"Skill {decision.skill_name} returned: {skill_reply_raw}")
                continue
        raise TimeoutError(
            f"maxiter reached ({self.config.max_steps}) without final answer.")
