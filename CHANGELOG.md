# Change Log

## new version

## 0.1.6
- Migrate from Azure pipeline to Github Actions #169
- Set env vars for codecov action #173
- Update testing badge #170

## 0.1.5
- addressed deprecated code #106
- fixed broken setup.py file #123
- added CI testing for Python 3.9 #126

## 0.1.4
- Fixed setup.py, install via 'pip install' should now install all required dependencies (#70)
- Added 'compare' command to CLI which allows comparisons of schema files. (#73)
- Better input sanity checks for the 'block' command (#75)
- CI now also tests on Windows (#78)
- Consistency check for uploads (#83)
- The block file now contains CLK count and blocking statistics as metadata. (#87)
- Adapted to API changes of clkhash. We now require clkhash>=0.16.0 (#89)
- Adapted to API changes of minio. We now require minio>=6.0.0 (#94)
- removed redundant work in the tests (#99)

## 0.1.3
Support upload to object store
Add progress bar for upload command
Print info about destination of upload

## 0.1.2
Add input format check to uploaded data when combining with blocks

## 0.1.1
Update requirements

## 0.1.0

First release of command line tool `anonlink` which enables following tasks:

* Encode data into CLKs given linkage schema
* Generate blocks from data given blocking schema
* Talk to entity service Rest API to create project, upload files, and get results back

