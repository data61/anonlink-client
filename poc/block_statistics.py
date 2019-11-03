import abc
from functools import reduce
from typing import Tuple
from itertools import combinations
import numpy as np


class BlockStats(abc.ABC):

    @classmethod
    def get_stats(cls,
                  block_filter: np.ndarray,
                  cbf_maps: Tuple[dict],
                  sig_records_maps: Tuple[dict],
                  config: dict):
        method_type = config.get('type', 'not provided')
        if method_type == 'index-based-blocks':
            return _IndexBasedBlockStats(block_filter, cbf_maps, sig_records_maps)
        elif method_type == 'signature-based-blocks':
            return _SignatureBasedBlockStats(block_filter, cbf_maps, sig_records_maps)
        else:
            raise ValueError("reverse index type '{}' is not recognized.".format(method_type))

    @abc.abstractmethod
    def total_comparisons(self):
        pass

    @abc.abstractmethod
    def elements_per_block(self):
        pass

    @abc.abstractmethod
    def number_of_blocks(self):
        pass


class _IndexBasedBlockStats(BlockStats):
    """ provides statistics of the blocks after combining the candidate blocking filters

        :ivar block_filter the combined blocking filter
        :ivar cbf_maps for each data provider, a dict containing the mapping from record id to the corresponding block ids
        :ivar sig_records_maps for each data provider, a dict containing the mapping from block id to corresponding record ids.
        """

    def __init__(self,
                 block_filter: np.ndarray,
                 cbf_maps: Tuple[dict],
                 sig_records_maps: Tuple[dict]):
        self.block_filter = block_filter
        self.cbf_maps = cbf_maps
        self.sig_record_maps = sig_records_maps
        self.counts_per_block = []
        for cbf_map, sig_records_map in zip(cbf_maps, sig_records_maps):
            counts = np.zeros(block_filter.shape[0])
            for i in range(block_filter.shape[0]):
                if block_filter[i]:
                    counts[i] = sum(len(sig_records_map[x]) for x in cbf_map[i])
            self.counts_per_block.append(counts)

    def total_comparisons(self):
        comp_per_block = reduce(lambda x, y: x * y, self.counts_per_block)
        return comp_per_block.sum()

    def elements_per_block(self):
        el_per_block = reduce(lambda x, y: x + y, self.counts_per_block)
        return el_per_block[np.nonzero(el_per_block)]

    def number_of_blocks(self):
        return self.elements_per_block().shape[0]


class _SignatureBasedBlockStats(BlockStats):
    """ provides statistics of the blocks after combining the candidate blocking filters

        :ivar block_filter the combined blocking filter
        :ivar cbf_maps for each data provider, a dict containing the mapping from record id to the corresponding block ids
        :ivar sig_records_maps for each data provider, a dict containing the mapping from block id to corresponding record ids.
        """

    def __init__(self,
                 block_filter: np.ndarray,
                 cbf_maps: Tuple[dict],
                 sig_records_maps: Tuple[dict]):
        self.block_filter = block_filter
        self.cbf_maps = cbf_maps
        self.sig_record_maps = sig_records_maps
        self.sig_counts = [{sig: len(v) for sig, v in sig_records_map.items()} for sig_records_map in sig_records_maps]

    def total_comparisons(self):
        comparisons = 0
        for a, b in combinations(self.sig_counts, 2):
            common_sigs = set(a.keys()).intersection(set(b.keys()))
            for sig in common_sigs:
                comparisons += a[sig] * b[sig]
        return comparisons

    def elements_per_block(self):
        block_sizes = []
        for a, b in combinations(self.sig_counts, 2):
            common_sigs = set(a.keys()).intersection(set(b.keys()))
            for sig in common_sigs:
                block_sizes.append(a[sig] + b[sig])
        return np.array(block_sizes)

    def number_of_blocks(self):
        """
        the number of blocks that gets compared in the solver. This can be less then the total number of blocks uploaded.
        """
        num_blocks = 0
        for a, b in combinations(self.sig_counts, 2):
            common_sigs = set(a.keys()).intersection(set(b.keys()))
            num_blocks += len(common_sigs)
        return num_blocks


def assess_blocks(dp1_signature, dp2_signature, dp1_data, dp2_data, ent_col=0):
    """Assess pair completeness and reduction ratio of blocking result."""
    cand_pairs = {}
    num_block_true_matches = 0
    num_block_false_matches = 0

    for key in dp1_signature:
        dp1_recs = dp1_signature[key]
        dp2_recs = dp2_signature[key]
        for d1 in dp1_recs:
            d1_entity = dp1_data[d1][ent_col]
            d1_cache = cand_pairs.get(d1_entity, set())
            for d2 in dp2_recs:
                d2_entity = dp2_data[d2][ent_col]
                if d2_entity not in d1_cache:
                    d1_cache.add(d2_entity)
                    if d2_entity == d1_entity:
                        num_block_true_matches += 1
                    else:
                        num_block_false_matches += 1
            cand_pairs[d1] = d1_cache

    num_cand_rec_pairs = num_block_true_matches + num_block_false_matches
    total_rec = len(dp1_data) * len(dp2_data)

    entity1 = [r[ent_col] for r in dp1_data]
    entity2 = [r[ent_col] for r in dp2_data]
    num_all_true_matches = len(np.intersect1d(entity1, entity2))

    rr = 1.0 - float(num_cand_rec_pairs) / total_rec
    pc = float(num_block_true_matches) / num_all_true_matches
    print('rr = {}'.format(round(rr, 4)))
    print('pc = {}'.format(round(pc, 4)))

