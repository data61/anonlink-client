import re
from typing import Sequence, Tuple

from blocklib import PPRLIndexPSignature
from blocklib import PPRLIndexKAnonymousSortedNeighbour
from poc.validation import validate_signature_config


def compute_candidate_blocks(data: Sequence[Tuple[str, ...]], signature_config):
    """
    :param data: list of tuples E.g. ('0', 'Kenneth Bain', '1964/06/17', 'M')
    :param signature_config:
        A description of how the signatures should be generated.

        A simple type is "feature-value" which simply takes the feature
        mentioned at `feature-index`::

            {
                'type': 'feature-value',
                'feature_idx': 3,
                'regex-pattern': ""
            }
        Schema for the signature config is found in
        ``docs/schema/signature-config-schema.json``

    :return: A 2-tuple containing
        A list of "signatures" per record in data.
        Internal state object from the signature generation (or None).

    """
    # validate config of blocking
    validate_signature_config(signature_config)

    # extract algorithm and its config
    algorithm = signature_config.get('type', 'not specified')
    config = signature_config.get('config', 'not specified')
    if config == 'not specified':
        raise ValueError('Please provide config for P-Sig from blocklib')

    # build corresponding PPLRIndex instance
    state = None
    if algorithm == 'not specified':
        raise ValueError("Compute signature type is not specified.")

    # Naive feature value
    elif algorithm == 'feature-value':
        dic_signatures_record = {}
        for index in range(len(data)):
            if algorithm == 'feature-value':
                signatures = _compute_feature_value_signature(data[index], signature_config)
                for signature in signatures:
                    if signature in dic_signatures_record:
                        dic_signatures_record[signature].append(index)
                    else:
                        dic_signatures_record[signature] = [index]

    # P-Sig from blocklib
    elif algorithm == 'p-sig':

        state = PPRLIndexPSignature(config)
        dic_signatures_record = state.build_inverted_index(data)
        state.summarize_invert_index(dic_signatures_record)

    # K Anonymous Sorted Nearest Neighbor
    elif algorithm == 'kasn':

        state = PPRLIndexKAnonymousSortedNeighbour(config)
        dic_signatures_record = state.build_inverted_index(data)

        state.summarize_invert_index(dic_signatures_record)

    else:
        msg = 'The algorithm {} is not implemented yet'.format(algorithm)
        raise NotImplementedError(msg)

    return dic_signatures_record, state


def _compute_feature_value_signature(record, feature_value_config):
    """

    :param record: a tuple of values from the dataset
    :param feature_value_config: the configuration for a single signature algorithm
    :return: a list of signatures for this record.
    """
    index = feature_value_config.get('feature-index', 'not specified')
    # By default, keep the whole value if no regex-pattern is provided
    pattern = feature_value_config.get('regex-pattern', '.*')

    if index == 'not specified':
        raise ValueError("Signature index is not specified.")

    index = int(index)
    prog = re.compile(pattern)

    prog_output = prog.search(record[index])
    if prog_output:
        return [prog_output.group()]
    return []
