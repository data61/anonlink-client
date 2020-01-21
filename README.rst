
.. image:: https://codecov.io/gh/data61/anonlink-client/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/data61/anonlink-client

Anonlink Client
================


Client-facing API to interact with anonlink system including command line tools and Rest API communication.
Anonlink system needs the following three components to work together:

* [clkhash](https://github.com/data61/clkhash)
* [blocklib](https://github.com/data61/blocklib)
* [anonlink-entity-service](https://github.com/data61/anonlink-entity-service)

This package provides an easy to use API to interact with the above packages to complete a record linkage job.

The way to interact with anonlink system is via Command Line Tool `anonlink`. You can hash data containing PII (Personal
 Identifying Information) locally using `anonlink hash`, generate candidate blocks locally to scale up record linkage 
 using `anonlink block`, create a record linkage job in entity service with `anonlink create-project` etc.

Installation
============
Currently manual install:

```python3
pip install git+https://https://github.com/data61/anonlink-client
```

Documentation
=============
https://clkhash.readthedocs.io/en/stable/cli.html
Note that the documentation are for clkhash now, we will add a readthedocs page for anonlink-client very soon.

CLI Tool
========
After installation, you should have a `anonlink` program in your path. For
example, to hash PII data  `alice.csv` locally with schema `schema.json` and secret `horse`, run:
```bash
$ anonlink hash 'alice.csv' 'horse' 'schema.json' 'encoded-entities.json'
```

It will generate the CLK output and store in `clk.json`. To find out how to define the schema
for your PII data, please refer [this page](https://clkhash.readthedocs.io/en/stable/schema.html) for 
details.

