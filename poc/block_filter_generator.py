from typing import Sequence

import numpy as np


def candidate_block_filter_from_signatures(signatures: Sequence[Sequence[str]], config):
    """

    :param signatures:
        A list of signatures for each record. Each signature is a list of
        strings.
    :param config:
    :return:
        A 2-tuple containing the candidate block filter (CBF) and
        a dict mapping block index (e.g. index in the cbf) to the list of
        signatures that are associated with that cbf location.
    """
    candidate_block_filter_type = config['type']
    if candidate_block_filter_type == 'dummy':
        return _dummy_candidate_block_filer_from_signature(signatures, config)
    else:
        raise ValueError("block_filter_from_signature type '{}' not implemented.".format(candidate_block_filter_type))


def _dummy_candidate_block_filer_from_signature(signatures, config):
    values = config['values']
    cbf_map = {}
    vector_output = np.zeros(len(values), dtype=np.int8)
    for value in set([x[0] for x in signatures]):
        if value in values:
            block_id = values.index(value)
            vector_output[block_id] = 1
            cbf_map[block_id] = value
        else:
            raise ValueError("Value '{}' not part of the configuration. Should be amongst '{}'.".format(value, values))
    return vector_output, cbf_map
