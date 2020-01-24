"""Test utils."""
import io
import os
import unittest
from bitarray import bitarray
from clkhash.serialization import serialize_bitarray

from anonlinkclient.utils import deserialize_filters, generate_candidate_blocks_from_csv


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
        schema_f = open(os.path.join(
            os.path.dirname(__file__),
            'testdata/bad-schema-v1.json'))


        # test invalid header
        header = 'Header'
        with self.assertRaises(ValueError):
            generate_candidate_blocks_from_csv(input_f, schema_f, header)
