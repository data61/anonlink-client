blocking_config = {
#     'signature': {
#         "type": "p-sig",
#         "version": 1,
#         "output": {
#             "type": "reverse-index",
#         },
#         "config": {
#             "blocking-features": [1, 2, 4, 5],
#             "filter": {
#                 "type": "ratio",
#                 "max": 0.02,
#                 "min": 0.001,
#             },
#             "blocking-filter": {      #  hyphen -> consistent
#                 "type": "bloom filter",
#                 "number-hash-functions": 4,
#                 "bf-len": 4096,
#             },
#             "map-to-block-algorithm": {
#                 "type": "signature-based-blocks",
#             },
#             "signatureSpecs": [
#                 [
#                     {"type": "characters-at", "config": {"pos": [0, 3, "7:9", "12:"]}, "feature-idx": 3},
#                     {"type": "feature-value", "feature-idx": 5}
#                 ],
#                 [
#                     {"type": "characters-at", "config": {"pos": [0]}, "feature-idx": 1},
#                     {"type": "characters-at", "config": {"pos": [0]}, "feature-idx": 2},
#                     {"type": "feature-value", "feature-idx": 5}
#                 ],
#                 [
#                     {"type": "feature-value", "feature-idx": 2},
#                 ],
# [
#                     {"type": "characters-at", "config": {"pos": ["3:"]}, "feature-idx": 9},
#                 ],
#                 [
#                     {"type": "metaphone", "feature-idx": 1},
#                 ],
#                 [
#                     {"type": "metaphone", "feature-idx": 2},
#                 ],
#                 [
#                     {"type": "metaphone", "feature-idx": 3},
#                     {"type": "metaphone", "feature-idx": 4}
#                 ],
#                 [
#                     {"type": "feature-value", "feature-idx": 10},
#                 ],
#                 [
#                     {"type": "characters-at", "config": {"pos": ["0:3"]}, "feature-idx": 1},
#                     {"type": "characters-at", "config": {"pos": ["0:3"]}, "feature-idx": 2},
#                 ],
#
#             ],
#         }
#     }
# #         'type': 'kasn',
# #         'version': 1,
# #         'config': {
# #             'k': 100,
# #             'sim-measure': {'algorithm': 'Dice',
# #                             'ngram-len': '2',
# #                             'ngram-padding': True,
# #                             'padding-start-char': chr(1),
# #                             'padding-end-char': chr(2)},
# #             'min-sim-threshold': 0.8,
# #             'overlap': 0,
# #             'sim-or-size': 'SIZE',
# #             'default-features': [1, 2],
# #             'sorted-first-val': '\x01',
# #             'ref-data-config': {'path': 'data/OZ-clean-with-gname.csv',
# #                                 'header-line': True,
# #                                 'default-features': [1, 2],
# #                                 'num-vals': 47,
# #                                 'random-seed': 0}
# #         }
#     },
    'signature': {
        "type": "lambda-fold",
        "version": 1,
        "config": {
            "blocking-features": [1, 2],
            "Lambda": 5,
            "bf-len": 2000,
            "num-hash-funcs": 10,
            "K": 30,
            "random_state": 0
        },
    },
}
