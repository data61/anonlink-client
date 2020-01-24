"""Test utils."""
import io
import os
import json
import pandas as pd
import tempfile
import unittest
from bitarray import bitarray
from clkhash.serialization import serialize_bitarray
from clkhash.clk import generate_clk_from_csv
from clkhash.schema import from_json_file
from blocklib import generate_candidate_blocks
from anonlinkclient.utils import deserialize_filters, generate_candidate_blocks_from_csv, combine_clks_blocks

from tests import *


class TestUtils(unittest.TestCase):

    def test_deserialize_bitarray(self):
        """Test deserialize bitarray."""
        # create simple bitarray bloom filter
        lst = [True, False, True, False] * 2
        bf = bitarray(lst)
        serialized_bf = serialize_bitarray(bf)
        deserialized_bf = deserialize_filters([serialized_bf])
        assert deserialized_bf == [bf]

    def test_generate_candidate_blocks_from_csv_exception(self):
        """Test exception case for generate candidate blocks from csv."""
        data = [[1, 'Joyce'],
                [2, 'Fred']]
        input_f = io.StringIO(str(data))
        schema_f = open(os.path.join(TESTDATA, 'bad-schema-v1.json'))

        # test invalid header
        header = 'Header'
        with self.assertRaises(ValueError):
            generate_candidate_blocks_from_csv(input_f, schema_f, header)

    def test_combine_clks_blocks(self):
        """Test combine clks and blocks."""
        _, fname_clks = tempfile.mkstemp(suffix='.json', text=True)
        _, fname_blks = tempfile.mkstemp(suffix='.json', text=True)
        _, dummy = tempfile.mkstemp(suffix='.csv', text=True)
        blocking_config = {
            "type": "lambda-fold",
            "version": 1,
            "config": {
                "blocking-features": [1, 2],
                "Lambda": 2,
                "bf-len": 1000,
                "num-hash-funcs": 5,
                "K": 5,
                "input-clks": False,
                "random_state": 0
            }
        }
        filename = os.path.join(TESTDATA, 'dirty_1000_50_1.csv')
        df = pd.read_csv(filename).set_index('rec_id')
        data = df.to_dict(orient='split')['data']
        blocking_obj = generate_candidate_blocks(data, blocking_config)
        blocks = blocking_obj.blocks
        for key in blocks:
            blocks[key] = [int(x) for x in blocks[key]]

        # convert block_key: row_index to a list of dict
        flat_blocks = []  # type: List[Dict[Any, List[int]]]
        for block_key, row_indices in blocks.items():
            flat_blocks.append(dict(block_key=block_key, indices=row_indices))
        result = {'blocks': flat_blocks}  # type: Dict[str, Dict[Any, Any]]

        # step2 - get all member variables in blocking state
        block_state_vars = {}  # type: Dict[str, Any]
        state = blocking_obj.state
        for name in dir(state):
            if '__' not in name and not callable(getattr(state, name)) and name != 'stats':
                block_state_vars[name] = getattr(state, name)
        result['state'] = block_state_vars

        # step3 - get config meta data
        result['config'] = blocking_config

        clks = generate_clk_from_csv(
            open(filename, 'r'), 'horse',
            from_json_file(schema_file=open(os.path.join(TESTDATA, 'dirty-data-schema.json'), 'r'))
        )
        json.dump({'clks': clks}, open(fname_clks, 'wt'))
        json.dump(result, open(fname_blks, 'wt'))

        # test exception
        with self.assertRaises(ValueError):
            df.to_csv(dummy)
            combine_clks_blocks(open(dummy, 'r'), open(dummy, 'r'))

        # test normal case
        cmb = combine_clks_blocks(open(fname_clks, 'r'), open(fname_blks, 'r'))
        assert len(cmb) == len(clks)


