from clkhash.schema import from_json_dict
from poc.filter import filter_signatures
from poc.block_filter_generator import candidate_block_filter_from_signatures
from poc.block_filter_generator import generate_block
from poc.reverse_index import create_block_list_lookup
from poc.server import compute_blocking_filter, solve
from poc.signature_generator import compute_signatures
from poc.clk_util import generate_clks
from poc.data_util import load_truth, download_data, download_reference_data
import json
import os
import pandas as pd
from poc.statistics import BlockStats
import numpy as np



def compute_candidate_block_filter(data, blocking_config):
    """

    :param data:
    :param blocking_config:
    :return:
        A 3-tuple containing:
        - the candidate block filter (CBF) and
        - a dict mapping block index (e.g. index in the cbf) to the list of
          signatures that are associated with that cbf location, and
        - candidate signatures a dict mapping signatures to records
    """
    signature_config = blocking_config['signature']
    filter_config = blocking_config['filter']

    candidate_signatures, signature_state = compute_signatures(data, signature_config)
    signatures = filter_signatures(candidate_signatures, filter_config)

    return tuple(
        [*candidate_block_filter_from_signatures(signatures, signature_state, blocking_config),
        candidate_signatures])


def run_gender_blocking(nb_parties, sizes, data_folder='./data'):

    blocking_config = {
        'signature': {
            # 'type': 'feature-value',
            #'config': {'feature-index': 3},
            # 'type': 'p-sig',
            # 'version': 1,
            # 'config': {
            #     'number_hash_functions': 4,
            #     'bf_len': 4096,
            #
            #     # Does it make sense to have a
            #     # common list of features to make
            #     # signatures from? Or should each
            #     # signature generation strategy
            #     # identify the features...?
            #     'default_features': [1, 2, 4, 5],
            #
            #     # could be under "filters" key?
            #     'max_occur_ratio': 0.02,
            #     'min_occur_ratio': 0.001,
            #
            #     # Maybe a config for how to join the
            #     # signatures back together?
            #     'join': {},
            #
            #     'signatures': [
            #         {"type": 'feature-value'},
            #         #{"type": 'soundex'},
            #         {"type": 'metaphone'},
            #         {"type": 'n-gram', 'config': {'n': 2}},
            #     ]
            # }
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
            'type': 'signature-based-blocks'
        }
    }

    path_file_1 = os.path.join(data_folder, "{}Parties".format(nb_parties),
                 "PII_{}_{}.csv".format(chr(0 + 97), sizes))
    df1 = pd.read_csv(path_file_1, skipinitialspace=True)
    path_file_2 = os.path.join(data_folder, "{}Parties".format(nb_parties),
                 "PII_{}_{}.csv".format(chr(1 + 97), sizes))
    df2 = pd.read_csv(path_file_2, skipinitialspace=True)
    """Use the entity_id column as index, but keep it as column too."""
    print(df1.index)
    df1 = df1.set_index('entity_id', drop=False).fillna('')
    df2 = df2.set_index('entity_id', drop=False).fillna('')
    data1 = df1.to_dict(orient='split')['data']
    data2 = df2.to_dict(orient='split')['data']
    print("Example PII", data1[0])

    # blocking with overlapping -> needs filter
    blocking_algorithm = blocking_config['signature']['type']
    if blocking_algorithm in {'p-sig'}:
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

        stats = BlockStats.get_stats(block_filter, (cbf_map_1, cbf_map_2), (sig_records_map_1, sig_records_map_2),
                           blocking_config['reverse-index'])
        print(f'total comparisons: {int(stats.total_comparisons()):,}')
        el_per_block = stats.elements_per_block()
        print(
            f'elements per block, max: {el_per_block.max()}, min: {el_per_block.min()}, mean: {el_per_block.mean()}, median: {np.median(el_per_block)}')
        print(f'number of blocks: {stats.number_of_blocks()}')

        num_blocks = _count_blocks(dp1_blocks)
        print(f"Number of blocks {num_blocks}")

    # blocking without overlapping -> no need for filter
    elif blocking_algorithm in {'kasn'} :
        dp1_signatures, _ = compute_signatures(data1, blocking_config['signature'])
        dp2_signatures, _ = compute_signatures(data2, blocking_config['signature'])
        dp1_blocks, dp2_blocks = generate_block(dp1_signatures, dp2_signatures)

    # exception
    else:
        raise NotImplementedError('Blocking algorithm "{}" is not supported yet'.format(blocking_algorithm))

    schema_json_fp = os.path.join(data_folder, 'schema.json')
    with open(schema_json_fp, "r") as read_file:
        schema_json = json.load(read_file)
    schema = from_json_dict(schema_json)
    encodings_dp1 = generate_clks(df1, schema=schema, secret_keys=("tick", "tock"))
    encodings_dp2 = generate_clks(df2, schema=schema, secret_keys=("tick", "tock"))

    solution = solve((encodings_dp1, encodings_dp2), (dp1_blocks, dp2_blocks), threshold=0.85)
    print('Found {} matches'.format(len(solution)))
    found_matches = set((a, b) for ((_, a), (_, b)) in solution)

    the_truth = load_truth(df1, df2, id_col='entity_id')

    tp = len(found_matches & the_truth)
    fp = len(found_matches - the_truth)
    fn = len(the_truth - found_matches)

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    print(f'precision: {precision}, recall: {recall}')


def _count_blocks(dp1_blocks):
    blockidset = set()
    for record_id in dp1_blocks:
        for block in dp1_blocks[record_id]:
            blockidset.add(block)
    num_blocks = len(blockidset)
    return num_blocks


if __name__ == '__main__':
    download_data(2, 10000)
    download_reference_data(2, 200000)
    run_gender_blocking(2, 10000)
