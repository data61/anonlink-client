import io
import json
import logging
import time
from clkhash.clk import generate_clk_from_csv
from clkhash.backports import unicode_reader, raise_from
from collections import defaultdict
from typing import Tuple, TextIO, Any, List, Dict
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


def generate_candidate_blocks_from_csv(input_f: TextIO,
                                       schema_f: TextIO,
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

    blocking_method = blocking_config['type']
    suffix_input = input_f.name.split('.')[-1]

    pii_data = []  # type: List[Any]
    # read from clks
    if blocking_method == 'lambda-fold' and blocking_config['config']['input-clks']:
        try:
            pii_data = json.load(input_f)['clks']
        except ValueError:  # since JSONDecodeError is inherited from ValueError
            raise TypeError(f'Upload should be CLKs not {suffix_input.upper()} file')

    # read from CSV file
    else:
        # # sentinel check for input
        # if suffix_input != 'csv':
        #     raise TypeError(f'Upload should be CSVs not {suffix_input.upper()} file')
        # else:
        reader = unicode_reader(input_f)
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

    # make encoding to blocks map
    encoding_to_blocks_map = defaultdict(list)
    for block_dict in flat_blocks:
        block_id = block_dict['block_key']
        for ind in block_dict['indices']:
            encoding_to_blocks_map[ind].append(block_id)
    result = {} # type: Dict[str, Any]
    result['blocks'] = encoding_to_blocks_map

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
    """Combine CLKs and blocks to produce a json stream of clknblocks.
       That's a list of lists, containing a CLK and its corresponding block IDs.

       Example output:
           {'clknblocks': [['UG9vcA==', '001', '211'],
                           [...]]}
    """
    try:
        blocks = json.load(block_f)['blocks']
        clks = json.load(clk_f)['clks']
    except ValueError as e:
        msg = 'Invalid CLKs or Blocks'
        raise_from(ValueError(msg), e)

    clknblocks = [[clk] for clk in clks]

    for rec_id, block_ids in blocks['blocks'].items():
        for block_key in block_ids:
            clknblocks[rec_id].append(block_key)
    out_stream = io.StringIO()
    json.dump({'clknblocks': clknblocks}, out_stream)
    out_stream.seek(0)
    return out_stream
