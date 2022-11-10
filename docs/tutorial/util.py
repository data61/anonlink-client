"""This module provides some helper functions for tutorial Notebooks."""

from collections import defaultdict

import anonlink


def solve(encodings, rec_to_blocks, threshold: float = 0.8):
    """entity resolution, baby

    calls anonlink to do the heavy lifting.

    :param encodings: a sequence of lists of Bloom filters (bitarray). One for each data provider
    :param rec_to_blocks: a sequence of dictionaries, mapping a record id to the list of blocks it is part of. Again,
                          one per data provider, same order as encodings.
    :param threshold: similarity threshold for solving
    :return: same as the anonlink solver.
             An sequence of groups. Each group is an sequence of
             records. Two records are in the same group iff they represent
             the same entity. Here, a record is a two-tuple of dataset index
             and record index.
    """

    def my_blocking_f(ds_idx, rec_idx, _):
        return rec_to_blocks[ds_idx][rec_idx]

    candidate_pairs = anonlink.candidate_generation.find_candidate_pairs(
        encodings,
        anonlink.similarities.dice_coefficient,
        threshold=threshold,
        blocking_f=my_blocking_f,
    )
    # Need to use the probabilistic greedy solver to be able to remove the duplicate. It is not configurable
    # with the native greedy solver.
    return anonlink.solving.probabilistic_greedy_solve(
        candidate_pairs, merge_threshold=1.0
    )


def naive_solve(encodings, threshold: float = 0.8):
    """entity resolution, baby

    calls anonlink to do the heavy lifting.

    :param encodings: a sequence of lists of Bloom filters (bitarray). One for each data provider
    :param threshold: similarity threshold for solving
    :return: same as the anonlink solver.
             An sequence of groups. Each group is an sequence of
             records. Two records are in the same group iff they represent
             the same entity. Here, a record is a two-tuple of dataset index
             and record index.
    """
    candidate_pairs = anonlink.candidate_generation.find_candidate_pairs(
        encodings, anonlink.similarities.dice_coefficient, threshold=threshold
    )
    # Need to use the probabilistic greedy solver to be able to remove the duplicate. It is not configurable
    # with the native greedy solver.
    return anonlink.solving.probabilistic_greedy_solve(
        candidate_pairs, merge_threshold=1.0
    )


def evaluate(found_groups, true_matches):
    tp = len([x for x in found_groups if x in true_matches])
    fp = len([x for x in found_groups if x not in true_matches])
    fn = len([x for x in true_matches if x not in found_groups])

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    return precision, recall


def reduction_ratio(filtered_reverse_indices, data, K):
    """Assess reduction ratio for multiple parties."""
    naive_num_comparison = 1
    for d in data:
        naive_num_comparison *= len(d)

    filtered_reversed_indices_dict = []
    block_keys = defaultdict(int)  # type: Dict[Any, int]
    for reversed_index in filtered_reverse_indices:
        fdict = defaultdict(list)
        for index, blks in reversed_index.items():
            for blk in blks:
                block_keys[blk] += 1
                fdict[blk].append(index)
        filtered_reversed_indices_dict.append(fdict)
    final_block_keys = [key for key, count in block_keys.items() if count >= K]

    reduced_num_comparison = 0
    for key in final_block_keys:
        num_comparison = 1
        for reversed_index in filtered_reversed_indices_dict:
            index = reversed_index.get(key, [0])
            num_comparison *= len(index)
        reduced_num_comparison += num_comparison
    rr = 1 - reduced_num_comparison / naive_num_comparison
    return rr, reduced_num_comparison, naive_num_comparison


def set_completeness(filtered_reverse_indices, truth, K):
    """Assess reduction ratio for multiple parties."""
    block_keys = defaultdict(int)  # type: Dict[Any, int]
    filtered_reversed_indices_dict = []
    for reversed_index in filtered_reverse_indices:
        fdict = defaultdict(list)
        for index, blks in reversed_index.items():
            for blk in blks:
                block_keys[blk] += 1
                fdict[blk].append(int(index))
        filtered_reversed_indices_dict.append(fdict)
    final_block_keys = [key for key, count in block_keys.items() if count >= K]

    sets = defaultdict(set)
    for i, reversed_index in enumerate(filtered_reversed_indices_dict):
        for key in final_block_keys:
            index = reversed_index.get(key, None)
            if index is not None:
                for ind in index:
                    sets[key].add((i, ind))

    num_true_matches = 0
    for true_set in truth:
        check = False
        true_set = set(true_set)
        for s in sets.values():
            if true_set.intersection(s) == true_set:
                check = True
        if check:
            num_true_matches += 1

    sc = num_true_matches / len(truth)
    return sc
