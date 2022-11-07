[![codecov](https://codecov.io/gh/data61/anonlink-client/branch/main/graph/badge.svg)](https://codecov.io/gh/data61/anonlink-client)
[![Documentation Status](https://readthedocs.org/projects/anonlink-client/badge/?version=latest)](http://anonlink-client.readthedocs.io/en/latest/?badge=latest)
[![Testing](https://github.com/data61/anonlink-client/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/data61/anonlink-client/actions/workflows/ci.yml)
[![Requirements Status](https://requires.io/github/data61/anonlink-client/requirements.svg?branch=main)](https://requires.io/github/data61/anonlink-client/requirements/?branch=main)
[![Downloads](https://pepy.tech/badge/anonlink-client)](https://pepy.tech/project/anonlink-client)
# Anonlink Client


Client-facing API to interact with anonlink system including command line tools and Rest API communication.
Anonlink system needs the following three components to work together:

* [clkhash](https://github.com/data61/clkhash)
* [blocklib](https://github.com/data61/blocklib)
* [anonlink-entity-service](https://github.com/data61/anonlink-entity-service)

This package provides an easy to use API to interact with the above packages to complete a record linkage job.

The way to interact with anonlink system is via Command Line Tool `anonlink`. You can hash data containing PI (Personal
 Identifying Information) locally using `anonlink hash`, generate candidate blocks locally to scale up record linkage 
 using `anonlink block`, create a record linkage job in entity service with `anonlink create-project` etc.

### Installation

Install with pip/poetry etc:

```python3
pip install anonlink-client
```

### Documentation

https://anonlink-client.readthedocs.io/en/stable/

### CLI Tool

After installation, you should have a `anonlink` program in your path. For
example, to hash PII data  `alice.csv` locally with schema `schema.json` and secret `horse`, run:
```bash
$ anonlink hash 'alice.csv' 'horse' 'schema.json' 'encoded-entities.json'
```

It will generate the CLK output and store in `clk.json`. To find out how to define the schema
for your PII data, please refer [this page](https://clkhash.readthedocs.io/en/stable/schema.html) for 
details.

