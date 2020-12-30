"""
.. currentmodule: {{ cookiecutter.project_slug }}.inner.inner

Some stuff about this package
=============================


.. autosummary::
   :toctree: generated/

   tmp - a demo class
"""




class tmp:
    """header doc string"""

    def __init__(self, a):
        """init a class for stuff"""
        self.a = a

    @property
    def b(self):
        """prop doc string"""
        return self.a + 1
