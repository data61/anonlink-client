Devops
===========

Azure Pipeline
--------------

``anonlink-client`` is automatically built and tested using Azure Pipeline for Windows environment, in the project `Anonlink <https://dev.azure.com/data61/Anonlink>`_

Two pipelines are available:
- `Build pipeline <https://dev.azure.com/data61/Anonlink/_build?definitionId=6>`_,
- `Release pipeline <https://dev.azure.com/data61/Anonlink/_release?definitionId=5>`_.


Build Pipeline
~~~~~~~~~~~~~~

The build pipeline is described by the script `azurePipeline.yml`.

There are 3 top level stages in the build pipeline:

- *Static Checks* - runs `mypy` typechecking over the codebase. Also adds a Azure DevOps tag `"Automated"`
  if the build was triggered by a Git tag.
- *Unit tests* - A template expands out into a number of builds and tests for different
  version of python and system architecture.
- *Packaging* - Pulls together the created files into a single release artifact.


The *Build & Test* job does:

- install the requirements,
- package ``anonlink-client``,
- run tests as described in the following table,
- publish the test results,
- publish the code coverage (on Azure and codecov),
- publish the artifacts from the build using ``Python 3.7`` (i.e. the wheel, the sdist `tar.gz` and an exe for x86 and x64).

The build pipeline requires one environment variable provided by Azure environment:

- `CODECOV_TOKEN` which is used to publish the coverage to codecov.

Description of what is tested:

==================   ====================  ===============  ===========  ===================  =========
Python Version       Operating System      Standard pytest  INLCUDE_CLI  TEST_ENTITY_SERVICE  Notebooks
==================   ====================  ===============  ===========  ===================  =========
3.6                  ubuntu-18.04          Yes              No           No                   No
3.6                  macos-10.13           Yes              No           No                   No
3.6                  vs2017-win2016 (x64)  Yes              No           No                   No
3.6                  vs2017-win2016 (x86)  Yes              No           No                   No
------------------   --------------------  ---------------  -----------  -------------------  ---------
3.7                  ubuntu-18.04          Yes              Yes          Yes                  Yes
3.7                  macos-10.13           Yes              Yes          Yes                  Yes
3.7                  vs2017-win2016 (x64)  Yes              Yes          Yes                  No
3.7                  vs2017-win2016 (x86)  Yes              No           No                   No
------------------   --------------------  ---------------  -----------  -------------------  ---------
3.8                  ubuntu-18.04          Yes              Yes          Yes                  Yes
3.8                  macos-10.13           Yes              No           No                   No
==================   ====================  ===============  ===========  ===================  =========

The tests using the environment variable `TEST_ENTITY_SERVICE` will use the URL provided by the Azure pipeline
variable `ENTITY_SERVICE_URL` (which is by default set to `https://anonlink.easd.data61.xyz`),
which enables to run manually the pipeline with a different deployed service.
However, we note that the pipeline will send github updates to the corresponding commit for the chosen deployment, not
the default one if the variable has been overwritten.

Build Artifacts
~~~~~~~~~~~~~~~

A pipeline artifact named **Release** is created by the build pipeline which contains the universal wheel, source
distribution and Windows executables for x86 and x64 architectures. Other artifacts are created from each build,
including code coverage.


Release Pipeline
~~~~~~~~~~~~~~~~

The release pipeline can either be triggered manually, or automatically from
a successful build on master where the build is tagged `Automated`
(i.e. if the commit is tagged, cf previous paragraph). 

The release pipeline consists of two steps: 
- asking for a manual confirmation that the artifacts from the triggering build should be released,
- uses ``twine`` to publish the artifacts.

The release pipeline requires two environment variables provided by Azure environment:
- `PYPI_LOGIN`: login to push an artifact to ``anonlink-client`` ``Pypi`` repository,
- `PYPI_PASSWORD`: password to push an artifact to ``anonlink-client`` ``Pypi`` repository for the user `PYPI_LOGIN`.

