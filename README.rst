pytest-pudb
===========

.. image:: https://github.com/alexfikl/pytest-pudb/actions/workflows/ci.yml/badge.svg
    :alt: Github Build Status
    :target: https://github.com/alexfikl/pytest-pudb/actions/workflows/ci.yml

`PuDB <https://pypi.org/project/pudb/>`__ debugger integration for
`pytest <https://pypi.org/project/pytest/>`__ based on the existing
`PDB integration <https://docs.pytest.org/en/stable/how-to/failures.html>`__. It
can be used with the ``--pudb`` flag directly as

.. code:: bash

    python -m pytest --pudb

This will open the debugger on any error in the tests. Alternatively, you can
also use `breakpoint <https://docs.python.org/3/library/functions.html#breakpoint>`__
command inside your Python code, which will automatically open the PuDB debugger
at that point.

.. code-block:: python

    def test_breakpoint_integration():
        breakpoint()
        assert 1 == 2

    def test_set_trace_integration():
        # equivalent to breakpoint()
        import pudb
        pudb.set_trace()

        assert 1 == 2

    def test_pudb_b_integration():
        import pudb.b
        # traceback is set up here
        assert 1 == 2
