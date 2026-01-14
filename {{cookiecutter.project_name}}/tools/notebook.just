{% raw -%}
# * Notebook specific rules ----------------------------------------------------

import "shared.just"

NOTEBOOKS := "examples/usage"

_nbqa_typecheck checker *files:
    {{ UVX_WITH_OPTS }} \
    nbqa --nbqa-shell \
    "uv run --active --no-project {{ TYPECHECK }} {{ UVX_OPTS }} {{ checker }}" -- {{ files }}

[group("notebook")]
[group("typecheck")]
mypy-notebook *files=NOTEBOOKS: (_nbqa_typecheck "-cmypy" files)

[group("notebook")]
[group("typecheck")]
pyright-notebook *files=NOTEBOOKS: (_nbqa_typecheck "-cpyright" files)

[group("notebook")]
[group("typecheck")]
basedpyright-notebook *files=NOTEBOOKS: (_nbqa_typecheck "-cbasedpyright" files)

[group("notebook")]
[group("typecheck")]
ty-notebook *files=NOTEBOOKS: (_nbqa_typecheck "-cty" files)

[group("notebook")]
[group("typecheck")]
pyrefly-notebook *files=NOTEBOOKS: (_nbqa_typecheck "-cpyrefly" files)

[group("lint")]
[group("notebook")]
[group("typecheck")]
pylint-notebook *files=NOTEBOOKS:
    {{ UVX_WITH_OPTS }} nbqa --nbqa-shell \
    "uv run --active --no-project -m pylint {{ PYLINT_OPTS }}" {{ files }}

[group("notebook")]
[group("typecheck")]
typecheck-notebook *files=NOTEBOOKS: (_nbqa_typecheck "-cmypy -cbasedpyright" files)

[group("notebook")]
[group("test")]
test-notebook *files=NOTEBOOKS:
    {{ UVRUN }} --group="test-notebook" --no-dev \
    pytest --nbval --nbval-current-env \
    --nbval-sanitize-with=config/nbval.ini \
    --dist loadscope \
    -x {{ files }}

[group("notebook")]
install-ipykernel: (nox "-s install-ipykernel")

# Execute notebooks inplace using nbclient
[group("notebook")]
execute-notebooks *files="examples/usage/*.ipynb":
    {{ UVRUN }} --group="notebook" --no-dev \
    jupyter execute --inplace --allow-errors {{ files }}
    just pre-commit run nbstripout --all-files  || true
{%- endraw %}
