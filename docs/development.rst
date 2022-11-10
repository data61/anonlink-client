Development
===========

Testing
-------

Make sure you have all the required modules before running the tests
(modules that are only needed for tests are not included during
installation)::


    $ pip install -r requirements.txt


Now run the unit tests and print out code coverage with `pytest`::

    $ python -m pytest --cov=anonlinkclient


Type Checking
-------------


``anonlink-client`` uses static typechecking with ``mypy``. To run the type checker (in Python 3.5 or later)::

    $ pip install mypy
    $ mypy anonlinkclient --ignore-missing-imports --strict-optional --no-implicit-optional --disallow-untyped-calls


Packaging
---------

The ``anonlink`` command line tool can be frozen into an exe using
`PyInstaller <https://pyinstaller.readthedocs.io>`_::

    pyinstaller cli.spec


Look for `anonlink.exe` in the `dist` directory.
