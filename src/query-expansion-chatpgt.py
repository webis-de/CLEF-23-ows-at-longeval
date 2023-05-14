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


def process_query(query):
    import openai
    print(f'Process Query: {query}')
    
    
    request = prompts["1"].replace('<ORIGINAL_QUERY>', query)
    ret = request

    #ret = openai.ChatCompletion.create(
    #    model="gpt-3.5-turbo",
    #    messages=[
    #        {"role": "system", "content": "You are a helpful assistant."},
    #        {"role": "user", "content": "Who won the world series in 2020?"}
    #    ]
    #)

    print(f'Response: {ret}')
    
    return ret
    

def main(num=10):
    performed = 0
    ret = json.load(open(target_file))
    
    for query in queries:
        if query in ret.keys():
            continue
        
        print(f'Process Query: {query}')
        ret[query] = process_query(query)
        performed += 1
        
        if performed > num:
            break
    json.dump(ret, open(target_file, 'w'))


if __name__ == '__main__':
    test_candidate_extraction()
    main(10)
