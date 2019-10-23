import pandas as pd
import os
import requests


def load_truth(df1, df2, id_col='entity_id'):
    df1 = df1.reset_index(drop=True)
    df2 = df2.reset_index(drop=True)
    a = pd.DataFrame({'ida': df1.index,
                      'link': df1[id_col]})
    b = pd.DataFrame({'idb': df2.index,
                      'link': df2[id_col]})
    dfj = a.merge(b, on='link', how='inner').drop(columns=['link'])
    the_truth = set()
    for row in dfj.itertuples(index=False):
        the_truth.add((row[0], row[1]))
    return the_truth


def _download_file_if_not_present(url_base, local_base, filename):
    os.makedirs(local_base, exist_ok=True)
    local_path = os.path.join(local_base, filename)
    if os.path.exists(local_path):
        print(f'Skipping already downloaded file: {filename}')
    else:
        print(f'Downloading {filename} to {local_base}')
        response = requests.get(url_base + filename, stream=True)
        assert response.status_code == 200, f"{response.status_code} was not 200"

        with open(local_path, 'wb') as f:
            for chunk in response:
                f.write(chunk)


def download_data(nb_parties, size, data_folder="./data"):
    """
    Download data used in the configured experiments.
    On S3, the data is organised in folders for the number of parties (e.g. folder `3Parties` for the data related to
    the 3 party linkage), and then a number a file following the format `PII_{user}_{size_data}.csv`, `clk_{user}_{size_data}_v2.bin`
    and `clk_{user}_{size_data}.json` where $user is a letter starting from `a` indexing the data owner, and `size_data`
    is a integer representing the number of data rows in the dataset (e.g. 10000). Note that the csv usually has a header.

    The data is stored in the folder provided from the configuration, following the same structure as the one on S3.
    """
    print('Downloading synthetic datasets from S3')
    base = 'https://s3-ap-southeast-2.amazonaws.com/n1-data/febrl/'
    os.makedirs(data_folder, exist_ok=True)
    _download_file_if_not_present(base, data_folder, 'schema.json')

    folder = os.path.join(base, "{}Parties/".format(nb_parties))
    local_data_folder = os.path.join(data_folder, "{}Parties/".format(nb_parties))

    for user in [chr(x + 97) for x in range(nb_parties)]:
        pii_file = f"PII_{user}_{size}.csv"
        _download_file_if_not_present(folder, local_data_folder, pii_file)

    print('Downloads complete')
