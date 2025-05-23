import os
import random
from dataset import load_data
from api import LLMCall
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from FewShotPrompt import *

def read_jsonl(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data


def process_question( j, llm, few_shot, dataset):
    if dataset =='csqa' or dataset =='strategyqa' or dataset == 'MATHQA':
        prompt_selected = prompt_choice
    else:
        prompt_selected = prompt
    q = j['raw_question']
    m_q = j['modified_question']
    a = j['answer']
    query = ""
    if few_shot:
        if dataset == 'MATH':
            query = FS_CoT_MATH.format(problem=m_q) + '[Solution] \n\n'
        elif dataset =='gsm8k':
            query = FS_CoT_GSM.format(problem=m_q) + '[Solution] \n\n'
        elif dataset == 'csqa':
            query = FS_CoT_CSQA.format(problem=m_q) + '[Solution] \n\n'
        elif dataset == 'strategyqa':
            query = FS_CoT_STRATEGYQA.format(problem=m_q)  + '[Solution] \n\n'
        elif dataset == 'MATHQA':
            query = FS_CoT_MATHQA.format(problem=m_q) + '[Solution] \n\n'
        else:
            print("No support")
        messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role':'user', 'content':prompt_selected + query}]
    else:
        query = '[Question] \n\n' + m_q + '[Solution] \n\n'
        messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role':'user', 'content':prompt_selected + query}]

    response = llm.call(messages)

    ret = {'raw_question': q, 'answer': a, 'modified_q':m_q, 'solution':response,'query':query}
    return ret


def run(args):
    random.seed(args.seed)
    llm_name = args.llm_name
    dataset = args.dataset
    llm = LLMCall('', llm_name)
    input_file = './modified_question/' + dataset + '/' + llm_name + '/' + 'questions.jsonl'
    if args.few_shot:
        output_path = './raw_solution_modified_q_CoT_few_shot/' + dataset + '/' + llm_name + '/'
        output_file = './raw_solution_modified_q_CoT_few_shot/' + dataset + '/' + llm_name + '/' + 'solution.jsonl'
    else:
        output_path = './raw_solution_modified_q_CoT/' + dataset + '/' + llm_name + '/'
        output_file = './raw_solution_modified_q_CoT/' + dataset + '/' + llm_name + '/' + 'solution.jsonl'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    js = read_jsonl(input_file)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []

        for j in js:
            
            futures.append(executor.submit(process_question, j, llm, args.few_shot, dataset))

        with open(output_file, 'w') as f:
            for future in as_completed(futures):
                res = future.result()
                json.dump(res, f)
                f.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--llm_name', type=str, default='qwen')
    parser.add_argument('--dataset', type=str, default='MATH')
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--few_shot', type=bool, default=False)
    
    args = parser.parse_args()

    run(args)
