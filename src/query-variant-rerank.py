#!/usr/bin/env python3
import sys
from tira.rest_api_client import Client
import pandas as pd
from tqdm import tqdm
import ir_datasets
import json
from pathlib import Path
from tira.third_party_integrations import ensure_pyterrier_is_loaded, load_rerank_data, normalize_run
import pyterrier as pt
from trectools import TrecRun, fusion
import pandas as pd
import os
sep = '___'

ensure_pyterrier_is_loaded()


def to_trec_run(r):
    from trectools import TrecRun
    import pandas as pd
    tr = TrecRun()
    tr.run_data = r.copy()
    tr.run_data['query'] = tr.run_data['qid'].apply(lambda i: i.split(sep)[0])
    tr.run_data['docid'] = tr.run_data['docno']
    
    print(f'Created run with {len(tr.run_data)} lines')
    
    return tr


def reciprocal_rank_fusion(run, num_runs=20):
    all_runs = []
    
    print(f'Process run with {len(run)} lines.')
    
    r = []
    
    all_runs += [to_trec_run(run[~run['qid'].str.contains(sep)])]
    assert len(all_runs[0].run_data) > 0
    
    for run_id in range(0, num_runs +1):
        r = run[run['qid'].str.endswith(f'{sep}{run_id}')]

        if len(r) < 1:
            continue

        all_runs += [to_trec_run(r)]
        print(f'Run with id {run_id} has {len(r)} documents')

    print(f'Fuse {len(all_runs)} runs')
    fused_run = fusion.reciprocal_rank_fusion(all_runs)
    fused_run = fused_run.run_data

    fused_run['qid'] = fused_run['query']
    del fused_run['query']
    fused_run['docno'] = fused_run['docid']
    del fused_run['docid']
    return fused_run


def expanded_data(queries, input_run, num_expansions):
    additional_rerank_data = []
    expansions = json.load(open(Path(input_run) / '1' / 'predictions.jsonl', 'r'))
    
    for _, i in queries.iterrows():
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
        
    return pd.concat([queries, pd.DataFrame(additional_rerank_data)])


def run_retrieval(queries, input_run, wmodel, query_variants, output_directory):
    output_file =  Path(output_directory) / 'run.txt'
    index_directory = Path(input_run) / '2' / 'index'
    import os
    print(os.listdir(index_directory))
    index = pt.IndexFactory.of(str(os.path.abspath(str(index_directory)))
    
    print(f'Load Data from {index_directory} to re-rank with {wmodel}.')
    rerank_data = expanded_data(queries, input_run, query_variants)
    rerank_data['query'] = rerank_data['query'].apply(lambda i: "".join([x if x.isalnum() else " " for x in i]))
    rerank_data.to_json(Path(output_directory) / 'rerank-data.jsonl', lines=True, orient='records')
    
    print('Ranking...')
    pipeline = pt.text.scorer(wmodel=wmodel, verbose=True, body_attr='text')

    pipeline = pt.BatchRetrieve(index, wmodel=wmodel, verbose=True)
    
    result = pipeline(rerank_data)
    
    print('Fuse results...')
    result = reciprocal_rank_fusion(result)
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    print(f'writing run file to:\t{output_file}')
    pt.io.write_results(normalize_run(result, 1000), Path(output_directory) / 'run.txt', run_name=f'ows-{wmodel}-{query_variants}-variants')


if __name__ == '__main__':
    queries = pt.io.read_topics(f'{sys.argv[1]}/queries.xml', 'trecxml')
    input_run = sys.argv[2]
    wmodel = sys.argv[3]
    num_query_variants = int(sys.argv[4])
    output_directory = sys.argv[5]
    run_retrieval(queries, input_run, wmodel, num_query_variants, output_directory)

