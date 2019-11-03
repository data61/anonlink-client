from typing import Sequence
from collections import defaultdict
import numpy as np


def candidate_block_filter_from_signatures(
        signatures: Sequence[Sequence[str]],
        signature_state,
        config):
    """

    :param signatures:
        TODO A list of signatures for each record. Each signature is a list of
        strings.
    :param signature_state:
        An object from :func:`compute_signatures`
    :param config:
    :return:
        A 2-tuple containing the candidate block filter (CBF) and
        a dict mapping blocking filter index to the list of
        signatures.
    """
    signature_algorithm = config['signature']['type']
    if signature_algorithm in {'p-sig'}:
        # blocklib can compute the candidate blocking filter using
        # the signature state (PPRLIndex instance).
        candidate_block_filter, cbf_index_to_sig_map = signature_state.generate_block_filter(signatures)
        return candidate_block_filter, cbf_index_to_sig_map
    else:
        candidate_block_filter_type = config['type']
        if candidate_block_filter_type == 'dummy':
            return _dummy_candidate_block_filer_from_signature(signatures, config)
        else:
            raise ValueError("block_filter_from_signature type '{}' not implemented.".format(candidate_block_filter_type))


def _dummy_candidate_block_filer_from_signature(signatures, config):
    values = config['values']
    cbf_map = {}
    vector_output = np.zeros(len(values), dtype=np.int8)
    for key in signatures:
        if key in values:
            blocking_filter_index = values.index(key)
            vector_output[blocking_filter_index] = 1
            cbf_map[blocking_filter_index] = [key]
        else:
            raise ValueError("Value '{}' not part of the configuration. Should be amongst '{}'.".format(key, values))
    return vector_output, cbf_map


def generate_block(dp1_signatures, dp2_signatures, k, overlap, ref_val_list):
    """Generate rec to block ID dict for blocking without overlapping."""
    dp1_blocks = {}
    dp2_blocks = {}

    dp2_block_lookup = {}
    for block_id in dp2_signatures:
        block_nums = block_id.split('_')
        blocks = block_nums[1:-1]
        for blk in blocks:
            dp2_block_lookup[blk] = block_id

    cand_blk_key = 0
    for block_id, block_vals in dp1_signatures.items():

        assert len(block_vals) >= k, (block_id, len(block_vals))

        block_nums_list = block_id.split('_')
        block_nums = block_nums_list[1:-1]

        lower_overlap_bound = int(min(block_nums)) - overlap
        upper_overlap_bound = int(max(block_nums)) + overlap

        if lower_overlap_bound > 0:
            block_nums.insert(0, str(lower_overlap_bound))
        if upper_overlap_bound < len(ref_val_list):
            block_nums.append(str(upper_overlap_bound))

        dp1_blk_list = block_vals
        dp2_blks = set([])
        dp2_blk_list = []

        for block_num in block_nums:
            block2 = dp2_block_lookup[block_num]
            dp2_blks.add(block2)

        for blk in dp2_blks:
            dp2_blk_list += dp2_signatures[blk]

        dp1_blocks[cand_blk_key] = dp1_blk_list
        dp2_blocks[cand_blk_key] = dp2_blk_list

    return dp1_blocks, dp2_blocks


def generate_reverse_blocks(dp1_signatures, dp2_signatures):
    dp1_blocks = defaultdict(list)
    dp2_blocks = defaultdict(list)

    for blk_id, rec_list in dp1_signatures.items():
        for rec in rec_list:
            dp1_blocks[rec].append(blk_id)
    for blk_id, rec_list in dp2_signatures.items():
        for rec in rec_list:
            dp2_blocks[rec].append(blk_id)

    return dp1_blocks, dp2_blocks
