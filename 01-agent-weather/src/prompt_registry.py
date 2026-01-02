from typing import Dict

import yaml
from pydantic import BaseModel


def _read_yaml(path: str) -> dict:
    with open(path, "r") as f:
        content = yaml.safe_load(f)
    return content


class PromptFile(BaseModel):
    name: str
    version: str
    prompt: Dict[str, str]


def render_template(prompt_template: str, variables: dict) -> str:
    out = prompt_template
    for k, v in variables.items():
        out = out.replace(f"{{{{{k}}}}}", str(v))
    return out


class Prompt(BaseModel):
    name: str
    version: str
    system: str
    user: str

    def render_messages(self, **variables) -> list[dict]:
        system_msg = render_template(self.system, variables)
        user_msg = render_template(self.user, variables)
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]


class PromptRegistry(BaseModel):
    root: str

    def pf_from_version(self, name: str, version: str = "1.0.0") -> PromptFile:
        prompt_path = f"{self.root}/{name}/{version}.yaml"
        prompt_data = _read_yaml(prompt_path)
        return PromptFile.model_validate(prompt_data)

    def pf_from_env(self, name: str, env: str = "dev") -> PromptFile:
        registry_path = f"{self.root}/registry.yaml"
        registry = _read_yaml(registry_path)
        version = registry["environments"][env][name]
        return self.pf_from_version(name, version)

    def load_prompt(self, name: str, env: str = "dev") -> Prompt:
        pf = self.pf_from_env(name, env)
        return Prompt(
            name=pf.name,
            version=pf.version,
            system=pf.prompt["system"],
            user=pf.prompt["user"],
        )
