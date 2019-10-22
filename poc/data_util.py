import pandas as pd


def load_truth(df1, df2, id_col='rec_id'):
    df1 = df1.reset_index()
    df2 = df2.reset_index()
    a = pd.DataFrame({'ida': df1.index,
                      'link': df1[id_col]})
    b = pd.DataFrame({'idb': df2.index,
                      'link': df2[id_col]})
    dfj = a.merge(b, on='link', how='inner').drop(columns=['link'])
    the_truth = set()
    for row in dfj.itertuples(index=False):
        the_truth.add((row[0], row[1]))
    return the_truth
