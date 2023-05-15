#!/usr/bin/env python3
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

dataset_to_index = {
    'longeval-short-july-20230513-training': '/mnt/ceph/tira/data/runs/longeval-short-july-20230513-training/ows/2023-05-13-19-41-17/output/index/data.properties',
    'longeval-train-20230513-training': '/mnt/ceph/tira/data/runs/longeval-train-20230513-training/ows/2023-05-13-19-40-07/output/index/data.properties',
    'longeval-heldout-20230513-training': '/mnt/ceph/tira/data/runs/longeval-heldout-20230513-training/ows/./2023-05-13-19-40-24/output/index/data.properties',
    'longeval-long-september-20230513-training': '/mnt/ceph/tira/data/runs/longeval-long-september-20230513-training/ows/2023-05-13-19-40-47/output/index/data.properties',
}

import pyterrier as pt

if not pt.started():
    pt.init()

def expanded_data(rerank_data, expansion_prompt, num_expansions):
    rerank_data = pt.io.read_topics(f'/mnt/ceph/tira/data/datasets/training-datasets/ir-benchmarks/{rerank_data}/queries.xml', 'trecxml')
    additional_rerank_data = []
    expansions = json.load(open('query-variants.json', 'r'))[expansion_prompt]
    
    for _, i in rerank_data.iterrows():
        expansions_for_query = expansions.get(i['query'].strip(), [])
        expansions_for_query = [i for i in expansions_for_query if len(i.split(' ')) > 1]
        
        if len(expansions_for_query) < 6:
            continue
        
        expansions_for_query = expansions_for_query[:num_expansions]
        for expansion_id, expansion in zip(range(len(expansions_for_query)), expansions_for_query):
            i_exp = i.to_dict().copy()
            i_exp['qid'] = i_exp['qid'] + '___' + str(expansion_id)
            i_exp['query'] = expansion
            additional_rerank_data += [i_exp]
        
    return pd.concat([rerank_data, pd.DataFrame(additional_rerank_data)])

def rerank_expansion(rerank_data, wmodel, query_variants, expansion_prompt):
    output_directory = Path(rerank_data) / 'query-variant-runs'
    output_file =  output_directory / f'{wmodel}-{query_variants}-variants-prompt-{expansion_prompt}-run.txt.gz'
    
    print(f'Use output {output_file}')
    if output_file.exists():
        print('Already exists')
        return
    
    index = pt.IndexFactory.of(dataset_to_index[rerank_data])
    
    print(f'Load Data from {rerank_data} to re-rank with {wmodel}.')
    rerank_data = expanded_data(rerank_data, expansion_prompt, query_variants)
    rerank_data['query'] = rerank_data['query'].apply(lambda i: "".join([x if x.isalnum() else " " for x in i]))
    
    print('Ranking...')
    pipeline = pt.text.scorer(wmodel=wmodel, verbose=True, body_attr='text')

    pipeline = pt.BatchRetrieve(index, wmodel=wmodel, verbose=True)
    
    result = pipeline(rerank_data)

    print(f'writing run file to:\t{output_file}')
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    pt.io.write_results(normalize_run(result, 1000), output_file, run_name=wmodel)


if __name__ == '__main__':
    rerank_data = sys.argv[1]
    wmodel = sys.argv[2]
    for prompt in ['1', '2']:
        for num_query_variants in [3, 5, 10]:
            rerank_expansion(rerank_data, wmodel, num_query_variants, prompt)

