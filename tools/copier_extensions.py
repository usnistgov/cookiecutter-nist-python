"""Hooks for copier"""

import datetime
from typing import Any

from copier_templates_extensions import ContextHook  # type: ignore


class CookiecutterNamespace(ContextHook):
    """Template hooks for copier"""

    def hook(self, context: dict[str, Any]) -> dict[str, Any]:
        # context["__project_slug"] = (
        #     context["project_name"].lower().replace("-", "_").replace(".", "_")
        # )
        # context["__type"] = (
        #     "compiled"
        #     if context["backend"] in ["pybind11", "skbuild", "mesonpy", "maturin"]
        #     else "pure"
        # )
        # context["__answers"] = context["_copier_conf"]["answers_file"]
        # context["__ci"] = "github" if "github.com" in context["url"] else "gitlab"
        context["__year"] = str(datetime.datetime.today().year)
        context["__answers"] = context["_copier_conf"]["answers_file"]
        return {"cookiecutter": context}
