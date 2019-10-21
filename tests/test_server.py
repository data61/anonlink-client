import numpy as np
from poc.server import compute_blocking_filter

def test_compute_filters():
    filter1 = np.ones(10)
    filter2 = np.ones(10)
    common = compute_blocking_filter((filter1, filter2), 1)
    assert common.sum() == 10
    common = compute_blocking_filter((filter1, filter2), 2)
    assert common.sum() == 10
    common = compute_blocking_filter((filter1, filter2), 3)
    assert common.sum() == 0
    filter1 = np.array([0,1,0,1,0,1])
    filter2 = np.array([0,1,1,0,1,1])
    filter3 = np.array([0,1,0,0,1,1])
    common = compute_blocking_filter((filter1, filter2, filter3), threshold=3)
    assert common[1] == common[5] == 1
    assert common.sum() == 2
