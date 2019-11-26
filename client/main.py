from clkhash.schema import from_json_dict
from client.clk_util import generate_clks
from client.data_util import load_truth, download_data, download_reference_data
from client.config import blocking_config
from blocklib import generate_candidate_blocks, generate_blocks_2party, generate_reverse_blocks, assess_blocks_2party
import json
import os
import pandas as pd
from client.server import solve


def run_blocking(nb_parties, sizes, data_folder='./data'):
    """Run example blocking."""
    # load datasets
    path_file_1 = os.path.join(data_folder, "{}Parties".format(nb_parties),
                               "PII_{}_{}.csv".format(chr(0 + 97), sizes))
    df1 = pd.read_csv(path_file_1, skipinitialspace=True)
    path_file_2 = os.path.join(data_folder, "{}Parties".format(nb_parties),
                               "PII_{}_{}.csv".format(chr(1 + 97), sizes))
    df2 = pd.read_csv(path_file_2, skipinitialspace=True)
    """Use the entity_id column as index, but keep it as column too."""
    print(df1.index)
    df1 = df1.set_index('entity_id', drop=False).fillna('')
    df2 = df2.set_index('entity_id', drop=False).fillna('')
    data1 = df1.to_dict(orient='split')['data']
    data2 = df2.to_dict(orient='split')['data']
    print("Example PII", data1[0])

    # create subdata that only includes index and entity_id
    subdata1 = [[x[0]] for x in data1]
    subdata2 = [[x[0]] for x in data2]

    # blocking with overlapping -> needs filter
    blocking_algorithm = blocking_config['signature']['type']
    if blocking_algorithm in {'p-sig', 'lambda-fold'}:

        candidate_block_obj1 = generate_candidate_blocks(data1, blocking_config['signature'])
        candidate_block_obj2 = generate_candidate_blocks(data2, blocking_config['signature'])
        filtered_reversed_indices = generate_blocks_2party((candidate_block_obj1, candidate_block_obj2))
        dp1_signatures, dp2_signatures = filtered_reversed_indices
        dp1_blocks, dp2_blocks = generate_reverse_blocks([dp1_signatures, dp2_signatures])
        assess_blocks_2party([dp1_signatures, dp2_signatures], [subdata1, subdata2])

    # exception
    else:
        raise NotImplementedError('Blocking algorithm "{}" is not supported yet'.format(blocking_algorithm))

    # encoding
    schema_json_fp = os.path.join(data_folder, 'schema.json')
    with open(schema_json_fp, "r") as read_file:
        schema_json = json.load(read_file)
    schema = from_json_dict(schema_json)
    encodings_dp1 = generate_clks(df1, schema=schema, secret_keys=("tick", "tock"))
    encodings_dp2 = generate_clks(df2, schema=schema, secret_keys=("tick", "tock"))

    # pass to anonlink solver
    solution = solve((encodings_dp1, encodings_dp2), (dp1_blocks, dp2_blocks), threshold=0.85)
    print('Found {} matches'.format(len(solution)))
    found_matches = set((a, b) for ((_, a), (_, b)) in solution)

    the_truth = load_truth(df1, df2, id_col='entity_id')

    tp = len(found_matches & the_truth)
    fp = len(found_matches - the_truth)
    fn = len(the_truth - found_matches)

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    print(f'precision: {precision}, recall: {recall}')


def _count_blocks(dp1_blocks):
    blockidset = set()
    for record_id in dp1_blocks:
        for block in dp1_blocks[record_id]:
            blockidset.add(block)
    num_blocks = len(blockidset)
    return num_blocks


if __name__ == '__main__':
    download_data(2, 10000)
    download_reference_data(2, 200000)
    run_blocking(2, 10000)