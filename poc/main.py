
from poc.filter import filter_signatures
from poc.block_filter_generator import candidate_block_filter_from_signatures
from poc.reverse_index import create_block_list_lookup
from poc.server import compute_blocking_filter, solve
from poc.signature_generator import compute_signatures
from recordlinkage.datasets import load_febrl4
from poc.clk_util import generate_clks, febrl4_schema


def compute_candidate_block_filter(data, blocking_config):
    """

    :param data:
    :param blocking_config:
    :return:
        A 3-tuple containing:
        - the candidate block filter (CBF) and
        - a dict mapping block index (e.g. index in the cbf) to the list of
          signatures that are associated with that cbf location, and
        - a dict mapping signatures to records
    """
    signature_config = blocking_config['signature']
    filter_config = blocking_config['filter']
    config = blocking_config['candidate-blocking-filter']

    candidate_signatures, signature_state = compute_signatures(data, signature_config)
    signatures = filter_signatures(candidate_signatures, filter_config)
    return tuple([candidate_block_filter_from_signatures(signatures, config)[0],
                 candidate_block_filter_from_signatures(signatures, config)[1],
                  candidate_signatures])


def run_gender_blocking():

    blocking_config = {
        'signature': {
            # 'type': 'feature-value',
            #'config': {'feature-index': 3},
            'type': 'p-sig',
            'version': 1,
            'config': {
                'number_hash_functions': 5,
                'bf_len': 4096,

                # Does it make sense to have a
                # common list of features to make
                # signatures from? Or should each
                # signature generation strategy
                # identify the features...?
                'default_features': [0, 1, 3, 4],

                # could be under "filters" key?
                'max_occur_ratio': 1.0,
                'min_occur_ratio': 0.001,

                # Maybe a config for how to join the
                # signatures back together?
                'join': {},

                'signatures': [
                    {"type": 'feature-value'},
                    #{"type": 'soundex'},
                    {"type": 'metaphone'},
                    {"type": 'n-gram', 'config': {'n': 2}},
                ]
            }
        },
        'filter': {
            'type': 'none'
            # 'type': 'frequency',
            # 'min': 2,
            # 'max': 1000
        },
        'candidate-blocking-filter': {
            'type': 'dummy'
        },
        'reverse-index': {
            'type': 'group-single-index'
        }
    }

    df1, df2 = load_febrl4()
    df1 = df1.fillna('')
    df2 = df2.fillna('')
    data1 = df1.to_dict(orient='split')['data']
    data2 = df2.to_dict(orient='split')['data']
    print("Example PII", data1[0])
    dp1_candidate_block_filter, cbf_map_1, sig_records_map_1 = compute_candidate_block_filter(data1, blocking_config)
    dp2_candidate_block_filter, cbf_map_2, sig_records_map_2 = compute_candidate_block_filter(data2, blocking_config)
    print("Candidate block filter dp1:", dp1_candidate_block_filter)
    print("Candidate block filter dp2:", dp2_candidate_block_filter)
    print("Candidate block filter map 1:", cbf_map_1)
    print("Candidate block filter map 2:", cbf_map_2)

    block_filter = compute_blocking_filter((dp1_candidate_block_filter, dp2_candidate_block_filter))
    print("Block filter:", block_filter)

    dp1_blocks = create_block_list_lookup(block_filter, cbf_map_1, sig_records_map_1, blocking_config['reverse-index'])
    dp2_blocks = create_block_list_lookup(block_filter, cbf_map_2, sig_records_map_2, blocking_config['reverse-index'])

    encodings_dp1 = generate_clks(df1, schema=febrl4_schema(), secret_keys=("tick", "tock"))
    encodings_dp2 = generate_clks(df2, schema=febrl4_schema(), secret_keys=("tick", "tock"))

    solution = solve((encodings_dp1, encodings_dp2), (dp1_blocks, dp2_blocks))
    print('Found {} matches'.format(len(solution)))
    mapping = {a: b for ((_, a), (_, b)) in solution}
    print(f'the mapping: {mapping}')


if __name__ == '__main__':
    run_gender_blocking()
