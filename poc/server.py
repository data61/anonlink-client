from typing import Sequence
import numpy as np


def compute_blocking_filter(candidate_blocking_filters: Sequence[np.ndarray], threshold: int = 2):
    cbf = np.sum(candidate_blocking_filters, axis=0)
    blocking_filter = cbf >= threshold
    return blocking_filter
