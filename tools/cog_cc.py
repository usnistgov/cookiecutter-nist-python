"""Helpers for creating copier.yml from cookiecutter.json"""

from __future__ import annotations

import dataclasses
import json
from itertools import starmap
from pathlib import Path
from typing import Any


@dataclasses.dataclass
class Choice:
    """Choices class."""

    name: str
    description: str = ""


@dataclasses.dataclass(frozen=True)
class Option:
    """Options class"""

    name: str
    default: str
    prompt: str
    type_: str
    choices: list[Choice]

    def yaml(self, default: bool = False, when: Any = None) -> str:
        """Create yaml output"""
        result: list[str] = [f"{self.name}:"]
        if self.type_:
            result.append(f"  type: {self.type_}")
        result.append(f"  help: {self.prompt}")

        if self.choices:
            result.append("  choices:")
            for choice in self.choices:
                result.append(  # noqa: PERF401
                    f'    "{choice.description}": {choice.name}'
                    if choice.description
                    else f"    - {choice.name}"
                )

            default_val = self.choices[0].name

        else:
            default_val = self.default

        if default and default_val:
            if isinstance(default_val, bool):  # pyright: ignore[reportUnnecessaryIsInstance]
                default_val = "yes" if default_val else "no"

            if not isinstance(default_val, str):  # pyright: ignore[reportUnnecessaryIsInstance]
                msg = f"received {default_val} of type {type(default_val)}"
                raise TypeError(msg)

            d = default_val

            if "{{" in d or "{%" in d:
                if "cookiecutter" in d:
                    d = d.replace("cookiecutter.", "")
                d = f'  default: "{d}"'
            else:
                d = f"  default: {d}"

            result.append(d)

        if when is not None:
            result.append(f"  when: {when}")

        return "\n".join(result)


class CC:
    """Cookiecutter to copier helper class."""

    def __init__(self, filename: str) -> None:
        with Path(filename).open(encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)

        self.options: dict[str, Option] = {}

        for name, value in data.items():
            if name.startswith("_"):
                continue
            prompts = data.get("__prompts__", {}).get(name, name)
            if isinstance(prompts, dict):
                prompt = prompts.pop("__prompt__")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                choices = list(starmap(Choice, prompts.items()))  # pyright: ignore[reportUnknownArgumentType]
                # Work around to enable " thing - thing" alignment:
                for choice in choices[9:]:
                    choice.description = choice.description.replace(" - ", "  - ")

            elif isinstance(value, list):
                prompt = prompts
                choices = [Choice(v) for v in value]  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
            else:
                prompt = prompts
                choices = []

            self.options[name] = Option(
                name=name,
                default=value,  # pyright: ignore[reportGeneralTypeIssues, reportArgumentType]
                prompt=prompt,  # pyright: ignore[reportUnknownArgumentType]
                type_=(
                    "str"
                    if isinstance(value, str)
                    else "bool"
                    if isinstance(value, bool)
                    else ""
                ),
                choices=choices,
            )

    def __getattr__(self, attr: str) -> Any:
        if attr in self.options:
            return self.options[attr]
        msg = f"{self.__class__.__name__} object has no attribute {attr}"
        raise AttributeError(msg)

    def __getitem__(self, item: str) -> Option:
        return self.options[item]

    def to_yaml(
        self, *keys: str, join: str = "\n\n", default: bool = False, when: Any = None
    ) -> str:
        """Create yaml output."""
        out = [self[key].yaml(default=default, when=when) for key in keys]

        return join.join(out)
