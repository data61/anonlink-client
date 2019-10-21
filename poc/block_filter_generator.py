import numpy as np

def candidate_block_filter_from_signatures(signatures, config):
    candidate_block_filter_type = config['type']
    if candidate_block_filter_type == 'dummy':
        return _dummy_candidate_block_filer_from_signature(signatures, config)
    else:
        raise ValueError("block_filter_from_signature type '{}' not implemented.".format(candidate_block_filter_type))


def _dummy_candidate_block_filer_from_signature(signatures, config):
    values = config['values']
    vector_output = np.ndarray(len(values), dtype=np.int8)
    #vector_output = [0] * len(values)
    for value in set([x[0] for x in signatures]):
        if value in values:
            vector_output[values.index(value)] = 1
        else:
            raise ValueError("Value '{}' not part of the configuration. Should be amongst '{}'.".format(value, values))
    return vector_output
