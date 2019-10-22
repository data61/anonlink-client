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
        a list mapping index in the cbf to the list of signatures
        that are in that block.
    """
    candidate_block_filter_type = config['type']
    if candidate_block_filter_type == 'dummy':
        return _dummy_candidate_block_filer_from_signature(signatures, config)
    else:
        raise ValueError("block_filter_from_signature type '{}' not implemented.".format(candidate_block_filter_type))


def _dummy_candidate_block_filer_from_signature(signatures, config):
    values = config['values']
    vector_output = np.zeros(len(values), dtype=np.int8)
    for value in set([x[0] for x in signatures]):
        if value in values:
            vector_output[values.index(value)] = 1
        else:
            raise ValueError("Value '{}' not part of the configuration. Should be amongst '{}'.".format(value, values))
    return vector_output
