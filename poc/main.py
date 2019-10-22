import clkhash
from poc.filter import filter_signatures
from poc.block_filter_generator import candidate_block_filter_from_signatures
from poc.server import compute_blocking_filter
from poc.signature_generator import compute_signatures
from recordlinkage.datasets import load_febrl4


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

    candidate_signatures = compute_signatures(data, signature_config)
    signatures = filter_signatures(candidate_signatures, filter_config)
    return candidate_block_filter_from_signatures(signatures, config)


def filter_reverse_index(block_filter, bf_map, sig_rec_map):
    """

    :param block_filter: The combined blocking filter - a numpy bool array.
    :param bf_map: Dict mapping block id to list of signatures.
    :param sig_rec_map: Dict mapping signatures to records.
    :return:
        Dict mapping block id to list of records.
    """
    return {}



def run_gender_blocking():

    blocking_config = {
        'signature': {
            'type': 'feature-value',
            'feature-index': 3
        },
        'filter': {
            'type': 'none'
            # 'type': 'frequency',
            # 'min': 2,
            # 'max': 1000
        },
        'candidate-blocking-filter': {
            'type': 'dummy',
            'filter-length': 2,
            'values': ['F', 'M']
        }

    }

    df1, df2 = load_febrl4()
    df1 = df1.fillna('')
    df2 = df2.fillna('')
    data1 = df1.to_dict(orient='split')['data']
    data2 = df2.to_dict(orient='split')['data']
    print("Example PII", data1[0])
    dp1_candidate_block_filter, cbf_map_1 = compute_candidate_block_filter(data1, blocking_config)
    dp2_candidate_block_filter, cbf_map_2 = compute_candidate_block_filter(data2, blocking_config)
    print("Candidate block filter dp1:", dp1_candidate_block_filter)
    print("Candidate block filter dp2:", dp2_candidate_block_filter)
    print("Candidate block filter map 1:", cbf_map_1)
    print("Candidate block filter map 2:", cbf_map_2)

    block_filter = compute_blocking_filter((dp1_candidate_block_filter, dp2_candidate_block_filter))
    print("Block filter:", block_filter)

    dp1_blocks = filter_reverse_index(block_filter, cbf_map_1, 'todo GS? signature -> record mapping')
    dp2_blocks = filter_reverse_index(block_filter, cbf_map_2, 'todo GS? signature -> record mapping')

    #for every dp_pair in ...
    for block_id in dp1_blocks:
        records_1 = dp1_blocks[block_id]
        records_2 = dp2_blocks[block_id]

        print(f"Block {block_id}")
        print("DP 1")
        print(records_1)

        print("DP 2")
        print(records_2)


if __name__ == '__main__':
    run_gender_blocking()
