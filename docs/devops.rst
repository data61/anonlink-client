Devops
===========

Github Actions
--------------

``anonlink-client`` is automatically built and tested using Github Actions.


Testing Workflow
~~~~~~~~~~~~~~~~

The testing workflow is defined in the script `.github/workflows/ci.yml`.

There are 3 top level jobs in the pipeline:

- *Notebook Tests* - runs the Jupyter notebooks to ensure the tutorials docs are accurate.
- *Unit tests* - A template expands out into a number of jobs and tests for different
  version of python and operating systems.
- *Packaging* - Creates release artifacts

