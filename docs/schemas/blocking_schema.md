# Block Schema for Anonlink-Client

### Schema for P-Sig

```json
{
    "type": "p-sig",
    "version": 1,
    "output": {
        "type":  "reverse_index",
    },
    "config": {
        "blocking_features": ["first name", "last name", "birthday", "suburb"],
        "filter": {
            "type": "ratio",  
            "max_occur_ratio": 0.02, 
             "min_occur_ratio": 0.001,
        },
        "blocking-filter": {
            "type": "bloom filter",
            "number_hash_functions": 4,
            "bf_len": 4096,
        },
        "map_to_block_algorithm": {
            "type": "signature-based-blocks",
        },
        "signatureSpecs": [
          [
            {"type": "characters_at", "args": {"pos": [0, 3, "7:9", "12:"]}, "feature_idx": 3},
            {"type": "soundex", "feature_idx": 2},
            {"type": "value", "feature_idx": 5}
          ],
          [
            {"type": "metaphone", "feature_idx": 1},
            {"type": "metaphone", "feature_idx": 2}
          ],
          [
            {"type": "characters_at", "config": {"pos": [0, 1]}, "feature_idx": 1},
            {"type": "characters_at", "args": {"pos": [0, 1]}, "feature_idx": 2},
            {"type": "feature-value", "feature_idx": 5}
          ]
        ],
    }
}
```
#### Example for the signatureSpecs:
```
example data: 1, 'Paul', 'Simonson', 'Victoria Avenue', 12, 2405, ...
produces something like this:
'Vta nue', 'S52', '2405'
'SM0XMT', 'XMTSMT'
'Pa', 'Si', '2405'
```
#### Note
It doesn't really matter how we join the different parts of a signature. As long as we always do the same thing. E.g.:

```" ".join(signature_parts)```

We can do something similar to our current privacy protection techniques. In order to hide the PII from the linkage unit,
we cannot send the signatures as-is. Instead we run them through a keyed hash function, (BLAKE hash, or HMAC) where only 
the data provider know the secret (same thing as inserting tokens into CLK). 

### Schema for KASN (kasn_sim and kasn_size)

```json
{
	"type": "kasn",
	"version": 1,
    "output": {
            "type":  "reverse_index",
    },
	"config": {
        "blocking_features": ["first name", "last name", "birthday", "suburb"],
        "k": 10,
        "sim_measure": {
            "algorithm": "Dice",
            "ngram_len": "3",
            "ngram_padding": "True",
            "padding_start_char": "\x01",
            "padding_end_char": "\x01",
        },
        "min_sim_threshold": 0.8,
        "overlap": 3,
        "sim_or_size": "SIZE",
        "sorted_first_val": "\x01",
        "ref_data_config": {
            "path": "data/2Parties/PII_reference.csv",
            "header_line": "True",
            "reference_features": ["first name", "last name", "birthday", "suburb"],            
            "num_vals": 10,
            "random_seed": 0}
  }
}
```

* `sim_or_size` can only be either `SIZE` (kasn_size) or `SIM` (kasn_sim)
* Three-party Sorted neighbourhood clustering - `SIM` based merging (Vat13PAKDD - SNC3PSim)
* Three-party Sorted neighbourhood clustering - `SIZE` based merging (Vat13PAKDD - SNC3PSim)
