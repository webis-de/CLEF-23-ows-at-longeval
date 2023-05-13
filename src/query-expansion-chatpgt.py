#!/usr/bin/python3
import json
import ir_datasets
import re

target_file = 'query-expansions-from-chatgpt-raw.json'
prompts = json.load(open('query-expansion-prompts.json'))
datasets = ['longeval/heldout', 'longeval/a-short-july', 'longeval/b-long-september']
queries = sorted(list(set([q.text.strip() for d in datasets for q in ir_datasets.load(d).queries_iter()])))

# Regex that looks for lines in enumerated list:
#   1. [CANDIDATE 1]
#   ...
#   N. [CANDIDATE n]
CANDIDATE_PATTERN = re.compile(r'^\s*\d+\.\s*(.*)$', re.MULTILINE)


def extract_candidate_expansions(response: str):
    return CANDIDATE_PATTERN.findall(response)


def test_candidate_extraction():
    with open('chatgpt-suggestions.json') as _file:
        test_data = json.load(_file)

    for test_entry in test_data:
        assert extract_candidate_expansions(test_entry['response']) == test_entry['candidates']

    print('Candidate expansions correctly extracted.')


def main(num):

    for query in queries:
        print(query)


if __name__ == '__main__':
    test_candidate_extraction()
