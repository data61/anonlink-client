"""Script to accept blocking job."""
from clkhash.schema import from_json_dict
from poc.block_filter_generator import candidate_block_filter_from_signatures
from poc.block_filter_generator import generate_block, generate_reverse_blocks
from poc.reverse_index import create_block_list_lookup
from poc.server import compute_blocking_filter, solve
from poc.candidate_block_generator import compute_candidate_blocks
from poc.block_result import CandidateBlockingResult
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


def generate_candidate_blocks(blocking_config, data):
    """Generate candidate blocks given config and data with help of blocklib."""
    # blocking with overlapping -> needs filter
    blocking_algorithm = blocking_config['signature']['type']
    if blocking_algorithm in {'p-sig'}:
        dp1_candidate_block_filter, cbf_map, sig_records_map = compute_candidate_block_filter(data, blocking_config)
        extra = dict(candidate_block_filter=dp1_candidate_block_filter,
                     cbf_map=cbf_map)
        block_obj = CandidateBlockingResult(sig_records_map, extra)

    # blocking without overlapping -> no need for filter
    elif blocking_algorithm in {'kasn'}:
        dp1_signatures, state = compute_candidate_blocks(data, blocking_config['signature'])
        extra = dict(state=state)
        block_obj = CandidateBlockingResult(dp1_signatures)

    # exception
    else:
        raise NotImplementedError('Blocking algorithm "{}" is not supported yet'.format(blocking_algorithm))

    return block_obj


def generate_final_blocks(blocking_config, block_obj1, block_obj2):
    """Generate final blocking."""
    blocking_algorithm = blocking_config['signature']['type']
    if blocking_algorithm in {'p-sig'}:
        dp1_candidate_block_filter = block_obj1.extra['candidate_block_filter']
        dp2_candidate_block_filter = block_obj2.extra['candidate_block_filter']
        sig_records_map_1 = block_obj1.blocks
        sig_records_map_2 = block_obj2.blocks
        cbf_map_1 = block_obj1.extra['cbf_map']
        cbf_map_2 = block_obj2.extra['cbf_map']

        block_filter = compute_blocking_filter((dp1_candidate_block_filter, dp2_candidate_block_filter))
        print("Block filter:", block_filter)

        dp1_blocks = create_block_list_lookup(block_filter, cbf_map_1, sig_records_map_1,
                                              blocking_config['reverse-index'])
        dp2_blocks = create_block_list_lookup(block_filter, cbf_map_2, sig_records_map_2,
                                          blocking_config['reverse-index'])

    elif blocking_algorithm in {'kasn'}:
        dp1_signatures = block_obj1.blocks
        dp2_signatures = block_obj2.blocks
        state = block_obj1.state
        dp1_signatures, dp2_signatures = generate_block(dp1_signatures, dp2_signatures, state.k, state.overlap,
                                                        state.ref_val_list)
        dp1_blocks, dp2_blocks = generate_reverse_blocks(dp1_signatures, dp2_signatures)

    # exception
    else:
        raise NotImplementedError('Blocking algorithm "{}" is not supported yet'.format(blocking_algorithm))

    return dp1_blocks, dp2_blocks


def _count_blocks(dp1_blocks):
    blockidset = set()
    for record_id in dp1_blocks:
        for block in dp1_blocks[record_id]:
            blockidset.add(block)
    num_blocks = len(blockidset)
    return num_blocks