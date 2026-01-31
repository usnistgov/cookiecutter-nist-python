"""Hooks for copier"""

from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any

from copier_template_extensions import ContextHook


class SmartDict(Mapping[Any, Any]):
    """A mapping."""

    def __init_subclass__(cls):
        cls._computed_keys = {}

    def __init__(self, init):
        self._init = init

    @classmethod
    def register(cls, func):
        cls._computed_keys[func.__name__] = func
        return func

    def __getitem__(self, item):
        if item in self._computed_keys:
            return self._computed_keys[item](self._init)

        return self._init[item]

    def __contains__(self, item):
        return item in self._init or item in self._computed_keys

    def __iter__(self):
        yield from self._init
        yield from self._computed_keys

    def __len__(self):
        return len(self._computed_keys) + len(self._init)


class CookiecutterContext(SmartDict):
    pass


@CookiecutterContext.register
def __year(_):
    return str(datetime.datetime.now(tz=None).year)  # noqa: DTZ005


@CookiecutterContext.register
def __answers(context):
    return context["_copier_conf"]["answers_file"]


class CookiecutterNamespace(ContextHook):
    def hook(self, context):
        context["cookiecutter"] = CookiecutterContext(context)
