import clkhash


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
    index = signature_config.get('feature_index', 'not specified')

    if algorithm == 'not specified':
        ValueError("Compute signature type is not specified.")
    elif index == 'not specified':
        ValueError("Signature index is not specified.")
    else:
        signatures = []
        index = int(index)
        if algorithm == 'feature-value':
            for dtuple in data:
                signature.append(dtuple[index])
        else:
            msg = 'The algorithm {} is not implemented yet'.format(algorithm)
            NotImplementedError(msg)


def filter_signatures(candidate_signatures, filter_config):
    typ = filter_config.get('type', 'not specified')
    if typ == 'none':
        return candidate_signatures
    else:
        NotImplementedError(f"filter type '{typ}' is not implemented, yet")


def candidate_block_filter_from_signatures(signatures, config):
    pass


def compute_candidate_block_filter(data, blocking_config):
    signature_config = blocking_config['signature']
    filter_config = blocking_config['filter']
    config = blocking_config['candidate-blocking-filter']

    candidate_signatures = compute_signatures(data, signature_config)
    signatures = filter_signatures(candidate_signatures, filter_config)
    return candidate_block_filter_from_signatures(signatures, config)



def run():
    data = list(clkhash.randomnames.NameList(100).names)

    print(data[0])

    blocking_config = {
        'signature': {
            'type': 'feature-value',
            'feature-index': 3
        },
        'filter': {
            'type': 'none'
            # 'type': 'frequency',
            # 'min': 2,
            # 'max': 1000
        },
        'candidate-blocking-filter': {
            'type': 'dummy',
            'filter-length': 2
        }

    }

    compute_candidate_block_filter(data, blocking_config)



if __name__ == '__main__':
    run()
