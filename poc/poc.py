import clkhash


def compute_signatures(data, signature_config):
    pass


def filter_signatures(candidate_signatures, filter_config):
    pass


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
