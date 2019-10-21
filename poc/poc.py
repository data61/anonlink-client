import clkhash
from poc.filter import filter_signatures
from poc.block_filter_generator import candidate_block_filter_from_signatures
from poc.signature_generator import compute_signatures


def compute_candidate_block_filter(data, blocking_config):
    signature_config = blocking_config['signature']
    filter_config = blocking_config['filter']
    config = blocking_config['candidate-blocking-filter']

    candidate_signatures = compute_signatures(data, signature_config)
    signatures = filter_signatures(candidate_signatures, filter_config)
    return candidate_block_filter_from_signatures(signatures, config)


def run():
    data = list(clkhash.randomnames.NameList(2).names)
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
            'filter-length': 2,
            'values': ['F', 'M']
        }

    }

    res = compute_candidate_block_filter(data, blocking_config)
    print(res)


if __name__ == '__main__':
    run()
