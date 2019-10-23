import numpy as np
from typing import Tuple
from functools import reduce


class BlockStats:
    """ provides statistics of the blocks after combining the candidate blocking filters

    :ivar block_filter the combined blocking filter
    :ivar cbf_maps for each data provider, a dict containing the mapping from record id to the corresponding block ids
    :ivar sig_records_maps for each data provider, a dict containing the mapping from block id to corresponding record ids.
    :ivar config the 'reverse-index' section of the config.
    """
    def __init__(self,
                 block_filter: np.ndarray,
                 cbf_maps: Tuple[dict],
                 sig_records_maps: Tuple[dict],
                 config: dict):
        self.block_filter = block_filter
        self.cbf_maps = cbf_maps
        self.sig_record_maps = sig_records_maps
        self.counts_per_block = []
        method_type = config.get('type', 'not provided')
        if method_type == 'group-single-index':
            # build arrays (for each dp) where the index denotes a block and the value is the count of the records in that block
            for cbf_map, sig_records_map in zip(cbf_maps, sig_records_maps):
                counts = np.zeros(block_filter.shape[0])
                for i in range(block_filter.shape[0]):
                    if block_filter[i]:
                        counts[i] = sum(len(sig_records_map[x]) for x in cbf_map[i])
                self.counts_per_block.append(counts)
        else:
            raise ValueError("reverse index type '{}' is not recognized.".format(method_type))

    def total_comparisons(self):
        comp_per_block = reduce(lambda x, y: x * y, self.counts_per_block)
        return comp_per_block.sum()

    def elements_per_block(self):
        el_per_block = reduce(lambda x, y: x + y, self.counts_per_block)
        return el_per_block[np.nonzero(el_per_block)]

    def number_of_blocks(self):
        return self.elements_per_block().shape[0]
