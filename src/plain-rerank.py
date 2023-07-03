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

if not pt.started():
    # needed in the image so that pyterrier can find the shared libs
    pt.init()

def rerank(rerank_data, wmodel):
    output_directory = Path(rerank_data) / 'plain-runs'
    output_file =  output_directory / f'{wmodel}-run.txt.gz'
    print(f'Use output {output_file}')
    if output_file.exists():
        print('Already exists')
        return
    
    print(f'Load Data from {rerank_data} to re-rank with {wmodel}.')
    rerank_data = load_rerank_data(rerank_data)
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
    rerank(rerank_data, wmodel)
