import io
from clkhash import clk, Schema
from clkhash.field_formats import Ignore, StringSpec, IntegerSpec, FieldHashingProperties, MissingValueSpec
from typing import Tuple
from pandas import DataFrame
from bitarray import bitarray
import base64


def deserialize_bitarray(bytes_data):
    ba = bitarray(endian='big')
    data_as_bytes = base64.decodebytes(bytes_data.encode())
    ba.frombytes(data_as_bytes)
    return ba


def deserialize_filters(filters):
    res = []
    for i, f in enumerate(filters):
        ba = deserialize_bitarray(f)
        res.append(ba)
    return res


def generate_clks(dataframe: DataFrame, schema: Schema, secret_keys: Tuple[str, str]):
    csv = io.StringIO()
    dataframe.to_csv(csv)
    csv.seek(0)
    return deserialize_filters(clk.generate_clk_from_csv(csv, secret_keys, schema))


def febrl4_schema():
    fields = [
        Ignore('rec_id'),
        StringSpec('given_name', FieldHashingProperties(ngram=2, num_bits=200)),
        StringSpec('surname', FieldHashingProperties(ngram=2, num_bits=200)),
        IntegerSpec('street_number', FieldHashingProperties(ngram=1, positional=True, num_bits=100,
                                                            missing_value=MissingValueSpec(sentinel=''))),
        StringSpec('address_1', FieldHashingProperties(ngram=2, num_bits=100)),
        StringSpec('address_2', FieldHashingProperties(ngram=2, num_bits=100)),
        StringSpec('suburb', FieldHashingProperties(ngram=2, num_bits=100)),
        IntegerSpec('postcode', FieldHashingProperties(ngram=1, positional=True, num_bits=100)),
        StringSpec('state', FieldHashingProperties(ngram=2, num_bits=100)),
        IntegerSpec('date_of_birth', FieldHashingProperties(ngram=1, positional=True, num_bits=200,
                                                            missing_value=MissingValueSpec(sentinel=''))),
        Ignore('soc_sec_id')
    ]
    return Schema(fields, 1024)