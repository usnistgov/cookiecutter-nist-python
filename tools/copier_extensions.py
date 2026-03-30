"""Hooks for copier"""
# pyright: reportImplicitOverride=false, reportUnusedFunction=false

from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from copier_template_extensions import ContextHook

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    Func = Callable[..., Any]


class SmartDict(Mapping[Any, Any]):
    """A mapping."""

    _computed_keys: dict[Any, Any]

    def __init_subclass__(cls) -> None:
        cls._computed_keys = {}

    def __init__(self, init: Mapping[str, Any]) -> None:
        self._init = init

    @classmethod
    def register(cls, func: Func) -> Func:
        cls._computed_keys[func.__name__] = func
        return func

    def __getitem__(self, item: Any) -> Any:
        if item in self._computed_keys:
            return self._computed_keys[item](self._init)

        return self._init[item]

    def __contains__(self, item: Any) -> bool:
        return item in self._init or item in self._computed_keys

    def __iter__(self) -> Iterator[str]:
        yield from self._init
        yield from self._computed_keys

    def __len__(self) -> int:
        return len(self._computed_keys) + len(self._init)


class CookiecutterContext(SmartDict):
    pass


@CookiecutterContext.register
def __year(_: Any) -> str:
    return str(datetime.datetime.now(tz=None).year)  # noqa: DTZ005


@CookiecutterContext.register
def __answers(context: Mapping[str, Any]) -> Any:
    return context["_copier_conf"]["answers_file"]


@CookiecutterContext.register
def __copier(context: Mapping[str, Any]) -> bool:  # noqa: ARG001
    return True


class CookiecutterNamespace(ContextHook):
    def hook(self, context: dict[str, Any]) -> None:
        context["cookiecutter"] = CookiecutterContext(context)
