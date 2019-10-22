
# Blocking POC 

A simple end to end demonstrator of blocking for record linkage.

Output should be candidate blocks.

```
{
  'records': [clks],
  'blocks': {
      'block id 1': [record ids]
  }
}
```

Two methods have been implemented that map to a list of records.

- index based blocking: creates a block for every high bit in the
  blocking filter.
- signature based blocking: creates a block for every individual
  signature.
  
## Software Components

- anonlink-client
- blocklib
- anonlink
- clkhash
