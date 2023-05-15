#!/usr/bin/python3
import json
import re


# Regex that looks for lines in enumerated list:
#   1. [CANDIDATE 1]
#   ...
#   N. [CANDIDATE n]
CANDIDATE_ENUM_PATTERN = re.compile(r'^\s*\d+\.\s*(.*)$', re.MULTILINE)



# Regex that looks for lines in lists:
#   - [CANDIDATE 1]
#   ...
#   - [CANDIDATE n]
CANDIDATE_LIST_PATTERN = re.compile(r'^\s*\- (.*)$', re.MULTILINE)

# Regex that looks for lines in lists:
#   "X" or "Y"
CANDIDATE_QUOTE_PATTERN = re.compile(r'"([^"]*)"', re.MULTILINE)

PATTERNS = [CANDIDATE_ENUM_PATTERN, CANDIDATE_LIST_PATTERN, CANDIDATE_QUOTE_PATTERN]

def extract_candidate_expansions(response: str):
    ret = []

    for pattern in PATTERNS:
        ret += pattern.findall(response)
        
    ret2 = []
    for i in ret:
        c = CANDIDATE_QUOTE_PATTERN.findall(i)
        if len(c) > 0:
            ret2 += c
        else:
            ret2 += [i]

    return sorted(list(set([i.strip() for i in ret2 if i.strip().lower() != 'or'])))


def test_candidate_extraction():
    test_data = json.load(open('chatgpt-suggestions.json'))

    for test_entry in test_data:
        extracted_expansions = extract_candidate_expansions(test_entry['response'])
        expected = sorted(list(set(test_entry['candidates'])))
        
        if extracted_expansions != expected:
            for i in extracted_expansions:
                if i not in expected:
                    print(f'Extracted but not expected: "{i}"')

            for i in expected:
                if i not in extracted_expansions:
                    print(f'Expected but not extracted: "{i}"')
        
            raise ValueError(f'{extracted_expansions} != {expected}')

    print('Candidate expansions correctly extracted.')

def main():
   files = ['query-expansions-from-chatgpt-raw-prompt-01.json', 'query-expansions-from-chatgpt-raw-prompt-02.json']
   ret = {}
   
   for f in files:
       for k,v in json.load(open(f, 'r')).items():
           request_prompt = v['request_prompt']
           if request_prompt not in ret:
               ret[request_prompt] = {}
           assert k not in ret[request_prompt]
           
           ret[request_prompt][k] = extract_candidate_expansions(v['gpt-3.5-turbo-response']['choices'][0]['message']['content'])
   
   json.dump(ret, open('../query-variants.json', 'w'), indent=2)
   

if __name__ == '__main__':
    test_candidate_extraction()
    main()

