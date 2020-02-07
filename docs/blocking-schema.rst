.. _blocking-schema:

Blocking Schema
===============
There are various blocking methods available suits various problems. To make our API as generic as possible to use
different blocking methods, we designed a blocking schema to specify which blocking method to use and its
configurations.

Currently we support two blocking methods:

* Probability signature
* LSH based :math:`\lambda`-fold

which are proposed by the following publication:

* `Scalable Entity Resolution Using Probabilistic Signatures on Parallel Databases <https://arxiv.org/abs/1712.09691>`_
* `An LSH-Based Blocking Approach with a Homomorphic Matching Technique for Privacy-Preserving Record Linkage <https://www.computer.org/csdl/journal/tk/2015/04/06880802/13rRUxASubY>`_

The format of the linkage schema is defined in a separate
`JSON Schema <https://json-schema.org/specification.html>`_ specification document -
`blocking-schema.json <https://github.com/data61/anonlink-client/blob/master/docs/schemas/blocking-schema.json>`_.

Basic Structure
---------------

A linkage schema consists of three parts:

* :ref:`type <blocking-schema/type>`, the blocking method to be used
* :ref:`version <blocking-schema/version>`, the version number of the hashing schema.
* :ref:`config <blocking-schema/config>`, an json configuration of that blocking method that varies with different blocking methods


Example Schema
--------------

::

    {
      "type": "lambda-fold",
      "version": 1,
      "config": {
        "blocking-features": [1, 2],
        "Lambda": 30,
        "bf-len": 2048,
        "num-hash-funcs": 5,
        "K": 20,
        "input-clks": true,
        "random_state": 0
      }
    }

Schema Components
-----------------
.. _blocking-schema/type:

type
~~~~
String value which describes the blocking method.

================= ================================
name              detailed description
================= ================================
psig              Probability Signature blocking method from `Scalable Entity Resolution Using Probabilistic Signatures on Parallel Databases <https://arxiv.org/abs/1712.09691>`_
lambda-fold       LSH based Lambda Fold Redundant blocking method from `Scalable Entity Resolution Using Probabilistic Signatures on Parallel Databases <https://arxiv.org/abs/1712.09691>`_
================= ================================

.. _blocking-schema/version:

version
~~~~~~~

Integer value that indicates the version of blocking schema

.. _blocking-schema/config:

config
~~~~~~

A dictionary of configuration to use different blocking methods
