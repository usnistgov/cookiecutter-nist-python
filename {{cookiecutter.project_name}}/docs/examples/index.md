# User guide

<!-- NOTE: Any references like `usage/...`
Are links to the top level `/examples/usage/...`.
To Generate these links, run

$ nox -s docs -- -d symlink
-->

```{toctree}
:maxdepth: 2

example-usage
{% if cookiecutter.use_jupyter %}
usage/demo
{% endif %}
```
