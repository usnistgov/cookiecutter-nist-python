"""Hooks for copier"""

from __future__ import annotations

import datetime
from typing import Any

from copier_templates_extensions import ContextHook


class CookiecutterNamespace(ContextHook):  # pylint: disable=abstract-method
    """Template hooks for copier"""

    def hook(self, context: dict[str, Any]) -> dict[str, Any]:  # noqa: PLR6301
        """Hook to create other variables."""
        context["__year"] = str(datetime.datetime.now(tz=None).year)  # noqa: DTZ005
        context["__answers"] = context["_copier_conf"]["answers_file"]
        return {"cookiecutter": context}
