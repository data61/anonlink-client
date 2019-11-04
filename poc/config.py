blocking_config = {
    'signature': {
        "type": "p-sig",
        "version": 1,
        "output": {
            "type": "reverse_index",
        },
        "config": {
            # "blocking_features": ["given_name", "surname", "address_1", "address_2"],
            "blocking_features": [1, 2, 4, 5],
            "filter": {
                "type": "ratio",
                "max_occur_ratio": 0.02,
                "min_occur_ratio": 0.001,
            },
            "blocking-filter": {
                "type": "bloom filter",
                "number_hash_functions": 4,
                "bf_len": 4096,
            },
            "map_to_block_algorithm": {
                "type": "signature-based-blocks",
            },
            "signatureSpecs": [
                [
                    {"type": "characters_at", "config": {"pos": [0, 3, "7:9", "12:"]}, "feature_idx": 3},
                    # {"type": "soundex", "feature_idx": 2},
                    {"type": "feature-value", "feature_idx": 5}
                ],
                [
                    {"type": "characters_at", "config": {"pos": [0]}, "feature_idx": 1},
                    {"type": "characters_at", "config": {"pos": [0]}, "feature_idx": 2},
                    {"type": "feature-value", "feature_idx": 5}
                ],
                [
                    {"type": "feature-value", "feature_idx": 2},
                ],
[
                    {"type": "characters_at", "config": {"pos": ["3:"]}, "feature_idx": 9},
                ],
                [
                    {"type": "metaphone", "feature_idx": 1},
                    # {"type": "metaphone", "feature_idx": 2}
                ],
                [
                    {"type": "metaphone", "feature_idx": 3},
                    {"type": "metaphone", "feature_idx": 4}
                ],

                [
                    {"type": "characters_at", "config": {"pos": ["0:3"]}, "feature_idx": 1},
                    {"type": "characters_at", "config": {"pos": ["0:3"]}, "feature_idx": 2},

                ],
                # [
                #     {"type": "characters_at", "config": {"pos": ["2:5"]}, "feature_idx": 1},
                # ],
                # [
                #     {"type": "characters_at", "config": {"pos": ["3:6"]}, "feature_idx": 1},
                # ],
                # [
                #     {"type": "characters_at", "config": {"pos": ["0:3"]}, "feature_idx": 2},
                # ],
                # [
                #     {"type": "characters_at", "config": {"pos": ["1:4"]}, "feature_idx": 2},
                # ],

            ],
        }
        # 'type': 'kasn',
        # 'version': 1,
        # 'config': {
        #     'k': 10,
        #     'sim_measure': {'algorithm': 'Edit',
        #                     'ngram_len': '3',
        #                     'ngram_padding': True,
        #                     'padding_start_char': '\x01',
        #                     'padding_end_char': '\x01'},
        #     'min_sim_threshold': 0.8,
        #     'overlap': 0,
        #     'sim_or_size': 'SIZE',
        #     'default_features': [1, 2, 4, 5],
        #     'sorted_first_val': '\x01',
        #     'ref_data_config': {'path': 'data/2Parties/PII_reference_200000.csv',
        #                         'header_line': True,
        #                         'default_features': [1, 2, 4, 5],
        #                         'num_vals': 500,
        #                         'random_seed': 0}
        # }
    },

    'candidate-blocking-filter': {
        'type': 'dummy'
    },
    'reverse-index': {
        'type': 'signature-based-blocks'
    }
}
