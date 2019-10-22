from typing import Sequence
import numpy as np

import anonlink


def compute_blocking_filter(candidate_blocking_filters: Sequence[np.ndarray], threshold: int = 2):
    cbf = np.sum(candidate_blocking_filters, axis=0)
    blocking_filter = cbf >= threshold
    return blocking_filter


def mapping_from_clks(clks_a, clks_b, threshold):
    results_candidate_pairs = anonlink.candidate_generation.find_candidate_pairs(
            [clks_a, clks_b],
            anonlink.similarities.dice_coefficient,
            threshold
    )
    solution = anonlink.solving.greedy_solve(results_candidate_pairs)
    print('Found {} matches'.format(len(solution)))
    return {a:b for ((_, a),(_, b)) in solution}
