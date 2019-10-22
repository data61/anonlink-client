from typing import Sequence

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
        return cbf, cbf_index_to_sig_map
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
