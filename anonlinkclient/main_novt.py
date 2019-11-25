from clkhash.schema import from_json_dict
from anonlinkclient.block_filter_generator import candidate_block_filter_from_signatures
from anonlinkclient.block_filter_generator import generate_block, generate_reverse_blocks
from anonlinkclient.reverse_index import create_block_list_lookup
from anonlinkclient.server import compute_blocking_filter, solve
from anonlinkclient.candidate_block_generator import compute_candidate_blocks
from anonlinkclient.clk_util import generate_clks
from anonlinkclient.data_util import load_truth, download_data, download_reference_data
from anonlinkclient.config import blocking_config
import json
from blocklib import generate_blocks as blocklib_genearte_blocks
import os
import pandas as pd
from anonlinkclient.block_statistics import BlockStats, assess_blocks
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


def run_novt_blocking(sizes, data_folder='./data'):
    """Run example blocking."""
    # load datasets
    df1 = pd.read_csv("data/{}_50_overlap_no_mod_alice.csv".format(sizes)).set_index("recid")
    df2 = pd.read_csv("data/{}_50_overlap_no_mod_alice.csv".format(sizes)).set_index("recid")
    data1 = df1.to_dict(orient='split')['data']
    data2 = df2.to_dict(orient='split')['data']
    print("Example PII", data1[0])
    # create subdata that only includes index and entity_id
    subdata1 = [[x[0]] for x in data1]
    subdata2 = [[x[0]] for x in data2]
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
    elif blocking_algorithm in {'lambda-fold'}:
        dp1_signatures, _ = compute_candidate_blocks(data1, blocking_config['signature'])
        dp2_signatures, _ = compute_candidate_blocks(data2, blocking_config['signature'])
        filtered_indices = blocklib_genearte_blocks([dp1_signatures, dp2_signatures], blocking_config['signature'])
        dp1_signatures = filtered_indices[0]
        dp2_signatures = filtered_indices[1]
        assess_blocks([dp1_signatures, dp2_signatures], [subdata1, subdata2])

        # dp1_blocks = create_rec_block_map(dp1_signatures)
        # dp2_blocks = create_rec_block_map(dp2_signatures)

    # exception
    else:
        raise NotImplementedError('Blocking algorithm "{}" is not supported yet'.format(blocking_algorithm))


def _count_blocks(dp1_blocks):
    blockidset = set()
    for record_id in dp1_blocks:
        for block in dp1_blocks[record_id]:
            blockidset.add(block)
    num_blocks = len(blockidset)
    return num_blocks


if __name__ == '__main__':
    # download_data(2, 10000)
    # download_reference_data(2, 200000)
    # run_blocking(2, 10000)
    run_novt_blocking(4611)