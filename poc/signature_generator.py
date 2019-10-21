def compute_signatures(data, signature_config):
    """
    :param data: list of tuples E.g. ('0', 'Kenneth Bain', '1964/06/17', 'M')
    :param signature_config:
        A description of how the filters should be generated.
        A simple type is "feature-value" which simply takes the feature
        mentioned at `feature-index`.

        'type': 'feature-value',
        'feature-index': 3
    :return: A list of "signatures" per record in data
    """
    algorithm = signature_config.get('type', 'not specified')
    index = signature_config.get('feature-index', 'not specified')

    if algorithm == 'not specified':
        ValueError("Compute signature type is not specified.")
    elif index == 'not specified':
        ValueError("Signature index is not specified.")
    else:
        signatures = []
        index = int(index)
        if algorithm == 'feature-value':
            for dtuple in data:
                signatures.append([dtuple[index]])
            return signatures
        else:
            msg = 'The algorithm {} is not implemented yet'.format(algorithm)
            NotImplementedError(msg)