Welcome to {{ cookiecutter.project_name }}'s documentation!
======================================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   readme
   installation
   usage
   demo
   {% if cookiecutter.sphinx_auto == 'autodoc' -%}modules
   {% elif cookiecutter.sphinx_auto == 'automodule' -%}api_automodule
   {% elif cookiecutter.sphinx_auto == 'autosummary' -%}api_autosummary
   {% endif -%}contributing
   {% if cookiecutter.create_author_file == 'y' -%}authors
   {% endif -%} history


Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
