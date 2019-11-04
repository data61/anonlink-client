from clkhash.schema import from_json_dict
from poc.block_filter_generator import candidate_block_filter_from_signatures
from poc.block_filter_generator import generate_block, generate_reverse_blocks
from poc.reverse_index import create_block_list_lookup
from poc.server import compute_blocking_filter, solve
from poc.candidate_block_generator import compute_candidate_blocks
from poc.clk_util import generate_clks
from poc.data_util import load_truth, download_data, download_reference_data
from poc.config import blocking_config
import json
import os
import pandas as pd
from poc.block_statistics import BlockStats, assess_blocks
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

    candidate_signatures, signature_state = compute_candidate_blocks(data, signature_config)

    return tuple(
        [*candidate_block_filter_from_signatures(candidate_signatures, signature_state, blocking_config),
         candidate_signatures])


def run_blocking(nb_parties, sizes, data_folder='./data'):
    """Run example blocking."""
    # load datasets
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
        dp1_candidate_block_filter, cbf_map_1, sig_records_map_1 = compute_candidate_block_filter(data1,
                                                                                                  blocking_config)
        dp2_candidate_block_filter, cbf_map_2, sig_records_map_2 = compute_candidate_block_filter(data2,
                                                                                                  blocking_config)
        print("Candidate block filter dp1:", dp1_candidate_block_filter)
        print("Candidate block filter dp2:", dp2_candidate_block_filter)
        print("Candidate block filter map 1:", cbf_map_1)
        print("Candidate block filter map 2:", cbf_map_2)

        block_filter = compute_blocking_filter((dp1_candidate_block_filter, dp2_candidate_block_filter))
        print("Block filter:", block_filter)

        dp1_blocks = create_block_list_lookup(block_filter, cbf_map_1, sig_records_map_1,
                                              blocking_config['reverse-index'])
        dp2_blocks = create_block_list_lookup(block_filter, cbf_map_2, sig_records_map_2,
                                              blocking_config['reverse-index'])

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
    elif blocking_algorithm in {'kasn'}:
        dp1_signatures, state = compute_candidate_blocks(data1, blocking_config['signature'])
        dp2_signatures, _ = compute_candidate_blocks(data2, blocking_config['signature'])
        dp1_signatures, dp2_signatures = generate_block(dp1_signatures, dp2_signatures, state.k, state.overlap,
                                                        state.ref_val_list)
        assess_blocks(dp1_signatures, dp2_signatures, data1, data2)

        dp1_blocks, dp2_blocks = generate_reverse_blocks(dp1_signatures, dp2_signatures)

    # exception
    else:
        raise NotImplementedError('Blocking algorithm "{}" is not supported yet'.format(blocking_algorithm))

    # encoding
    schema_json_fp = os.path.join(data_folder, 'schema.json')
    with open(schema_json_fp, "r") as read_file:
        schema_json = json.load(read_file)
    schema = from_json_dict(schema_json)
    encodings_dp1 = generate_clks(df1, schema=schema, secret_keys=("tick", "tock"))
    encodings_dp2 = generate_clks(df2, schema=schema, secret_keys=("tick", "tock"))

    # pass to anonlink solver
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
    run_blocking(2, 10000)
