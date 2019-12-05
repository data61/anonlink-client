import io
from clkhash import clk
from clkhash.schema import Schema
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
    dataframe.to_csv(csv, index=False)
    csv.seek(0)
    return deserialize_filters(clk.generate_clk_from_csv(csv, secret_keys, schema))
