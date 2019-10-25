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
        cbf, cbf_index_to_sig_map = signature_state.generate_bloom_filter(signatures)

        # have to massage the cbf into a numpy bool array from a set
        candidate_block_filter = np.zeros(config['signature']['config']['bf_len'], dtype=bool)
        candidate_block_filter[list(cbf)] = True

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


def generate_block(dp1_signatures, dp2_signatures):
    """Generate rec to block ID dict for blocking without overlapping."""
    dp1_blocks = defaultdict(list)
    dp2_blocks = defaultdict(list)

    for blk_id, rec_list in dp1_signatures.items():
        for rec in rec_list:
            dp1_blocks[rec].append(blk_id)
    for blk_id, rec_list in dp2_signatures.items():
        for rec in rec_list:
            dp2_blocks[rec].append(blk_id)

    return dp1_blocks, dp2_blocks
