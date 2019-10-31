# Block Schema for Anonlink-Client

Required three elements:

```json
{
	'type': algorithm_name,
  'version': 1,
  'blocking_features': [1, 2, 3],
  'config': {}
}
```

where type / algorithm_name must be within:

* p-sig (supported)
* kann (not supported yet)

* kasn_sim (supported)
* kasn_size (supported)
* bflsh (not supported yet)
* kasn_2p_sim (not supported yet) 
* Hclust_2p (not supported yet)

`type` and `version` are generic fields. `config` is a dictionary of all customized parameters needed for different blocking methods.

### Schema for P-Sig

```json
{
	'type': 'p-sig',
	'version': 1,
	'config': {
      'number_hash_functions': 4,
      'bf_len': 4096,
      'default_features': [1, 2, 4, 5],
      'max_occur_ratio': 0.02,
      'min_occur_ratio': 0.001,
      'join': {},
      'signatures': [
        {"type": 'feature-value'},
        {"type": 'metaphone'},
        {"type": 'n-gram', 'config': {'n': 2}},
      ]
  }
}
```

* each element in `signatures` is one signature generation strategy
  * `type` : signature strategy name
  * `config`: parameters for signature strategy

### Schema for KASN (kasn_sim and kasn_size)

```json
{
	'type': 'kasn',
	'version': 1,
	'config': {
      'k': 10,
      'sim_measure': {'algorithm': 'Dice',
                      'ngram_len': '3',
                      'ngram_padding': True,
                      'padding_start_char': '\x01',
                      'padding_end_char': '\x01'},
      'min_sim_threshold': 0.8,
      'overlap': 3,
      'sim_or_size': 'SIZE',
      'default_features': [1, 2, 4, 5],
      'sorted_first_val': '\x01',
      'ref_data_config': {'path': 'data/2Parties/PII_reference.csv',
                          'header_line': True,
                          'default_features': [1, 2, 4, 5],
                          'num_vals': 10,
                          'random_seed': 0}
  }
}
```

* `sim_or_size` can only be either `SIZE` (kasn_size) or `SIM` (kasn_sim)
* Three-party Sorted neighbourhood clustering - `SIM` based merging (Vat13PAKDD - SNC3PSim)
* Three-party Sorted neighbourhood clustering - `SIZE` based merging (Vat13PAKDD - SNC3PSim)

### Schema for KANN

```json
{
	'type': 'kann',
	'version': 1,
	'config': {
      'k': 10,
      'sim_measure': {'algorithm': 'Dice',
                      'ngram_len': '3',
                      'ngram_padding': True,
                      'padding_start_char': '\x01',
                      'padding_end_char': '\x01'},
      'min_sim_threshold': 0.8,
      'default_features': [1, 2, 4, 5],
      'sorted_first_val': '\x01',
      'ref_data_config': {'path': 'data/2Parties/PII_reference.csv',
                          'header_line': True,
                          'default_features': [1, 2, 4, 5],
                          'num_vals': 10,
                          'random_seed': 0}
  }
}
```

* very similar with config of KASN except it does not have `overlap` and `sim_or_size`

### Schema for BFLSH

```json
{
	'type': 'bflsh',
	'version': 1,
	'config': {
      'number_hash_function': 10,
      'one_bit_set_perc': 50,
			'random_seed': 1,
      'default_features': [1, 2, 4, 5],
    	'default_bf_sample_perc': [50, 50, 50, 50],
    	'num_bits_hlsh': 45,
    	'num_iter_hash': 40
  }
}
```

* `one_bit_set_perc`: A percentage value between 1 and 99 (default is 50 percent) which gives the number of bits that should be set to 1 in a Bloom filter, based on the number of hash functions to be used and the average number of q-grams to be expected in attribute values.
* `default_bf_sample_perc`:A list with percentage numbers (one per selected attribute) which specifies the percentage of bits to sample from an attribute Bloom filter.
* `num_bits_hlsh`: Number of bits to sample from record Bloom filters to generate the locality sensitive hashing (LSH) values.
* `num_iter_hash`: Number of times a record Bloom filter is sampled.

### Schema for KASN_2P_SIM

```
{
	'type': 'snc2p',
	'version': 1,
	'config': {
      'k': 10,
      'w': 2,
      'sim_measure': {'algorithm': 'Dice',
                      'ngram_len': '3',
                      'ngram_padding': True,
                      'padding_start_char': '\x01',
                      'padding_end_char': '\x01'},
      'min_sim_threshold': 0.8,
      'overlap': 3,
      'sim_or_size': 'SIM',
      'default_features': [1, 2, 4, 5],
      'sorted_first_val': '\x01',
      'ref_data_config': {'path': 'data/2Parties/PII_reference.csv',
                          'header_line': True,
                          'default_features': [1, 2, 4, 5],
                          'num_vals': 10,
                          'random_seed': 0}
  }
}
```

* Very similar to KASN except the reference data is loaded by Bob and Alice individually

### Schema for HCLUST_2P

```
{
	'type': 'hclust_2p',
	'version': 1,
	'config': {
      'nb': 1000,
      'wn': 1000,
      'ep': 0.3,
      'sim_measure': {'algorithm': 'Edit',
                      'ngram_len': '3',
                      'ngram_padding': True,
                      'padding_start_char': '\x01',
                      'padding_end_char': '\x01'},
      'default_features': [1, 2, 4, 5],
      'sorted_first_val': '\x01',
      'ref_data_config': {'path': 'data/2Parties/PII_reference.csv',
                          'header_line': True,
                          'default_features': [1, 2, 4, 5],
                          'num_vals': 10,
                          'random_seed': 0
  }
}
```

