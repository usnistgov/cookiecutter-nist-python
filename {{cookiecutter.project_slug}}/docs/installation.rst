.. highlight:: shell

============
Installation
============


Stable release
--------------

To install {{ cookiecutter.project_name }}, run this command in your terminal:

.. code-block:: console

    $ pip install {{ cookiecutter.project_slug }}

or

.. code-block:: console

   $ conda install -c {{ cookiecutter.conda_channel }} {{ cookiecutter.project_slug }}


This is the preferred method to install {{ cookiecutter.project_name }}, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for {{ cookiecutter.project_name }} can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}


Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ pip install .

To install dependecies with conda/mamba, use::

.. code-block:: console

   $ conda/mamba env create -n {name} -f environment.yaml
   $ pip install . --no-deps

To install an editable version, add the `-e` option to pip.

.. _Github repo: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}
