"""pre-generate hook"""

import re
import sys

PACKAGE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9-]+$"
package_name = "{{ cookiecutter.project_name }}"

if not re.match(PACKAGE_REGEX, package_name):
    print(  # noqa: T201
        f"ERROR: The project name {package_name} is not a valid Python package name.  Please use letters and - or _ only."
    )

    # Exit to cancel project
    sys.exit(1)

MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"
module_name = "{{ cookiecutter.project_slug}}"

if not re.match(MODULE_REGEX, module_name):
    print(  # noqa: T201
        f"ERROR: The project slug {module_name} is not a valid Python module name. Please do not use a - and use _ instead."
    )

    # Exit to cancel project
    sys.exit(1)
