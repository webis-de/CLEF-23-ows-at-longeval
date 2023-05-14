#!/usr/bin/python3
import sys
from tira.rest_api_client import Client
import pandas as pd
from tqdm import tqdm
import ir_datasets
import json
from pathlib import Path
from tira.third_party_integrations import ensure_pyterrier_is_loaded, load_rerank_data, normalize_run

datasets = {
    'longeval/heldout': 'longeval-heldout-20230513-training',
    'longeval/b-long-september': 'longeval-long-september-20230513-training',
    'longeval/a-short-july': 'longeval-short-july-20230513-training',
    'longeval/train': 'longeval-train-20230513-training'
}

import pyterrier as pt

if not pt.started():
    # needed in the image so that pyterrier can find the shared libs
    !ln -s /usr/lib/jvm/java-11-openjdk/lib/server/libjvm.so /usr/lib/jvm/java-11-openjdk/lib/
    pt.init()

expansions = json.load(open('query-expansions.json', 'r'))['1']

def expanded_data(rerank_data):
    additional_rerank_data = []
    
    for _, i in tqdm(rerank_data.iterrows(), 'Add Expansion_queries'):
        expansions_for_query = expansions[i['query']]
        expansions_for_query = [i for i in expansions_for_query if len(i.split(' ')) > 1]
        
        if len(expansions_for_query) < 6:
            continue
        
        for expansion_id, expansion in zip(range(5), expansions_for_query[:5]):
            i_exp = i.to_dict().copy()
            i_exp['qid'] = i_exp['qid'] + '___' + str(expansion_id)
            i_exp['query'] = expansion
            additional_rerank_data += [i_exp]
        
    return pd.concat([rerank_data, pd.DataFrame(additional_rerank_data)])

def rerank_expansion(rerank_data, wmodel):
    output_directory = Path(rerank_data) / 'query-variant-runs-01'
    output_file =  output_directory / f'{wmodel}-run.txt.gz'
    print(f'Use output {output_file}')
    if output_file.exists():
        print('Already exists')
        return
    
    print(f'Load Data from {rerank_data} to re-rank with {wmodel}.')
    rerank_data = load_rerank_data(rerank_data)
    print(f'Length of re-rank data before expansion: {len(rerank_data)}')
    rerank_data = expanded_data(rerank_data)
    print(f'Length of re-rank data after expansion: {len(rerank_data)}')
    
    print('Re-rank Data')
    pipeline = pt.text.scorer(wmodel=wmodel, verbose=True, body_attr='text')
    
    rerank_data['query'] = rerank_data['query'].apply(lambda i: "".join([x if x.isalnum() else " " for x in i]))

    result = pipeline(rerank_data)

    print(f'writing run file to:\t{output_file}')
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    pt.io.write_results(normalize_run(result, 1000), output_file, run_name=wmodel)

if __name__ == '__main__':
    rerank_data = sys.argv[1]
    wmodel = sys.argv[2]
    rerank_expansion(rerank_data, wmodel)

