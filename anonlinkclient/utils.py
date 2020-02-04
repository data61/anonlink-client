import json
import logging
import time
from tqdm import tqdm
from clkhash.clk import generate_clks
from clkhash.schema import Schema
from clkhash.stats import OnlineMeanVariance
from clkhash.backports import unicode_reader, raise_from
from clkhash.validate_data import  validate_header, validate_row_lengths
from typing import Tuple, TextIO, Any
from bitarray import bitarray
from blocklib import generate_candidate_blocks
import base64

log = logging.getLogger('anonlink')


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


def generate_clk_from_csv(input_f,  # type: TextIO
                          secret,  # type: AnyStr
                          schema,  # type: Schema
                          validate=True,  # type: bool
                          header=True,  # type: Union[bool, AnyStr]
                          progress_bar=True  # type: bool
                          ):
    # type: (...) -> List[str]
    """ Generate Bloom filters from CSV file, then serialise them.

        This function also computes and outputs the Hamming weight
        (a.k.a popcount -- the number of bits set to high) of the
        generated Bloom filters.

        :param input_f: A file-like object of csv data to hash.
        :param secret: A secret.
        :param schema: Schema specifying the record formats and
            hashing settings.
        :param validate: Set to `False` to disable validation of
            data against the schema. Note that this will silence
            warnings whose aim is to keep the hashes consistent between
            data sources; this may affect linkage accuracy.
        :param header: Set to `False` if the CSV file does not have
            a header. Set to `'ignore'` if the CSV file does have a
            header but it should not be checked against the schema.
        :param bool progress_bar: Set to `False` to disable the progress
            bar.
        :return: A list of serialized Bloom filters and a list of
            corresponding popcounts.
    """
    if header not in {False, True, 'ignore'}:
        raise ValueError("header must be False, True or 'ignore' but is {!s}."
                         .format(header))

    log.info("Hashing data")

    # Read from CSV file
    reader = unicode_reader(input_f)

    if header:
        column_names = next(reader)
        if header != 'ignore':
            validate_header(schema.fields, column_names)

    start_time = time.time()

    # Read the lines in CSV file and add it to PII
    pii_data = []
    for line in reader:
        pii_data.append(tuple(element.strip() for element in line))

    validate_row_lengths(schema.fields, pii_data)

    if progress_bar:
        stats = OnlineMeanVariance()
        with tqdm(desc="generating CLKs", total=len(pii_data), unit='clk', unit_scale=True,
                  postfix={'mean': stats.mean(), 'std': stats.std()}) as pbar:
            def callback(tics, clk_stats):
                stats.update(clk_stats)
                pbar.set_postfix(mean=stats.mean(), std=stats.std(), refresh=False)
                pbar.update(tics)

            results = generate_clks(pii_data,
                                    schema,
                                    secret,
                                    validate=validate,
                                    callback=callback)
    else:
        results = generate_clks(pii_data,
                                schema,
                                secret,
                                validate=validate)

    log.info("Hashing took {:.2f} seconds".format(time.time() - start_time))
    return results


def generate_candidate_blocks_from_csv(input_f: TextIO,
                                       schema_f: str,
                                       header: bool = True):
    """ Generate candidate blocks from CSV file

         This function also computes and outputs the Hamming weight
         (a.k.a popcount -- the number of bits set to high) of the
         generated Bloom filters.

         :param input_f: A file-like object of csv data to hash.
         :param schema_f: Schema specifying the blocking configuration
         :param header: Set to `False` if the CSV file does not have
             a header. Set to `'ignore'` if the CSV file does have a
             header but it should not be checked against the schema.
         :return: A dictionary of blocks, state and config
     """
    if header not in {False, True, 'ignore'}:
        raise ValueError("header must be False, True or 'ignore' but is {!s}."
                         .format(header))

    log.info("Hashing data")

    # read blocking config as a dictionary
    start_time = time.time()
    try:
        blocking_config = json.load(schema_f)
    except ValueError as e:
        msg = 'The schema is not a valid JSON file'
        raise_from(ValueError(msg), e)

    # read from clks
    if blocking_config['config'].get('input-clks', False):
        pii_data = json.load(input_f)['clks']
    else:  # read from CSV file
        reader = unicode_reader(input_f)
        pii_data = []  # type: Tuple[str]

        if header:
            next(reader)
        for line in reader:
            pii_data.append(tuple(element.strip() for element in line))

    # generate candidate blocks
    blocking_obj = generate_candidate_blocks(pii_data, blocking_config)
    log.info("Blocking took {:.2f} seconds".format(time.time() - start_time))

    # save results to dictionary
    # step1 - get blocks (need to convert numpy.int64 to normal int
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
    return result


def combine_clks_blocks(clk_f: TextIO, block_f: TextIO):
    """Combine CLKs and blocks to produce a dictionary of CLK to list of block IDs."""
    try:
        blocks = json.load(block_f)['blocks']
        clks = json.load(clk_f)['clks']
    except ValueError as e:
        msg = 'Invalid CLKs or Blocks'
        raise_from(ValueError(msg), e)

    output = [[clk] for clk in clks]

    for blk in blocks:
        block_key = blk['block_key']
        rec_ids = blk['indices']
        for rid in rec_ids:
            output[rid].append(block_key)
    return output