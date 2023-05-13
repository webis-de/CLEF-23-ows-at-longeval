#!/usr/bin/python3
import json
import ir_datasets
target_file = 'query-expansions-from-chatgpt-raw.json'
prompts = json.load(open('query-expansion-prompts.json'))
datasets = ['longeval/heldout', 'longeval/a-short-july', 'longeval/b-long-september']
queries = sorted(list(set([q.text.strip() for d in datasets for q in ir_datasets.load(d).queries_iter()])))

def main(num):

    for query in queries:
        print(query)


if __name__ == '__main__':

