# Nomenclature related to blocking

## Candidate signatures

From a record, a method generate a list of candidates signatures based on a
set of configurations which specifies how to transform the values from the features
of the record.

Each record will have a variable number of candidate signatures.

## Signatures from candidate signatures

The candidate signatures become signatures after having being filtered.

For example, removing the too frequent signatures.

## Candidate blocking filter

From the signatures from all the records, a candidate blocking filter is generated, 
representing all the signatures from the local dataset.

## Blocking filter from canditate blocking filters

The blocking filter is generated from all the parties' candidate blocking filters. 
It will represent all the blocks having elements in common in a number of datasets.

From the blocking filter, each dataprovider can determine the number of blocks 
which will be generated and which records from their local dataset is included in each block.
Note that a record can be in a variable number of blocks (from 0 to the number of blocks 
to create).

## Blocks

A block represents a number of records from multiple datasets which have similar signatures
so could be potentially linked.
