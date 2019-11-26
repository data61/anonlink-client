from typing import Sequence, List, Dict
from bitarray import bitarray
import anonlink


def solve(encodings: Sequence[List[bitarray]], rec_to_blocks: Sequence[Dict[int, list]], threshold: float = 0.8):
    """ entity resolution, baby

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
        blocking_f=my_blocking_f)
    # Need to use the probabilistic greedy solver to be able to remove the duplicate. It is not configurable
    # with the native greedy solver.
    return anonlink.solving.probabilistic_greedy_solve(candidate_pairs, merge_threshold=1.0)

