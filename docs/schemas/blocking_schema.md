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
        "signatures": [
            {"type": "feature-value"},
            {"type": "soundex"},
            {"type": "metaphone"},
            {"type": "n-gram", "config": {"n": 2},
        ],
    }
}
```

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
