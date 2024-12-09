import json
from api import LLMCall
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import argparse
import random
import os
from few_shot_prompt import *



def read_jsonl(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data


def process_question(j, ratio, llm, few_shot,dataset):
    if dataset =='csqa' or dataset =='strategyqa' or dataset == 'MATHQA':
        prompt_selected = prompt_choice
    else:
        prompt_selected = prompt
    q = j['raw_question']
    a = j['answer']
    m_q = j['modified_q']
    m_s = j['solution']

    if 'The answer is:' in m_s:
        modified_ans = m_s.split('The answer is:')[1]
    elif 'the answer is:' in m_s:
        modified_ans = m_s.split('the answer is:')[1]
    elif 'The answer choice is:' in m_s:
        modified_ans = m_s.split('The answer choice is:')[1]
    else:
        modified_ans = ""

    steps = m_s.split('\n\n')
    len_sol = len(steps)
    idx = max(ratio * len_sol - 1, 0)

    


    s = '\n\n'.join(steps[:int(idx) + 1])
    if 'The answer is:' in s:
        s = s.split('The answer is:')[0]
    if 'the answer is:' in s:
        s = s.split('the answer is:')[0]
    if 'The answer choice is:' in s:
        s = s.split('The answer choice is:')[0]

    

    
    
    if few_shot:
        if dataset == 'MATH':
            query = FS_CoT_MATH.format(problem=q) +'The answer is:' + modified_ans +'\n\n[Solution] \n\n' + s
            
        elif dataset =='gsm8k':
            query = FS_CoT_GSM.format(problem=q)  + 'The answer is:' + modified_ans +'\n\n[Solution] \n\n' + s
        elif dataset == 'csqa':
            query = FS_CoT_CSQA.format(problem=q) +'The answer is:' + modified_ans + '\n\n[Solution] \n\n' + s
        elif dataset == 'strategyqa':
            query = FS_CoT_STRATEGYQA.format(problem=q) +'The answer is:' + modified_ans + '\n\n[Solution] \n\n' + s
        elif dataset == 'MATHQA':
            query = FS_CoT_MATHQA.format(problem=q) +'The answer is:' + modified_ans + '\n\n[Solution] \n\n' + s
        else:
            print("No support")
        messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role':'user', 'content':prompt_selected + query}]
    else:
        query = q +'\n\nThe answer is:' + modified_ans + '\n\n' + '[Solution]\n\n' + s
        messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role':'user', 'content':prompt_selected + query}]


        

    response = llm.call(messages)

    if ratio == 0.0:
        if few_shot:
            if dataset == 'MATH':
                query = FS_CoT_MATH.format(problem=q) + '[Solution] \n\n' 
            elif dataset =='gsm8k':
                query = FS_CoT_GSM.format(problem=q) + '[Solution] \n\n' 
            elif dataset == 'csqa':
                query = FS_CoT_CSQA.format(problem=q) + '[Solution] \n\n' 
            elif dataset == 'strategyqa':
                query = FS_CoT_STRATEGYQA.format(problem=q)  + '[Solution] \n\n' 
            elif dataset == 'MATHQA':
                query = FS_CoT_MATHQA.format(problem=q) + '[Solution] \n\n'
            else:
                print("No support")
            messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role':'user', 'content':prompt_selected + query}]
        else:
            query = '[Question] \n\n' + q + '[Solution] \n\n' + s
            messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role':'user', 'content':prompt_selected + query}]

        
        response_raw = llm.call(messages)
    
    
        ret = {'question':q, 'answer':a,'modified_q':m_q,'raw_solution':response_raw,'modified_solution':s, 'modified_question':j['modified_q'],'final_solution':response}
    else:
        ret = {'question':q, 'answer':a,'modified_q':m_q,'modified_solution':s, 'modified_question':j['modified_q'],'final_solution':response}
    return ret


def main(args):
    random.seed(args.seed)
    llm_name = args.llm_name
    dataset = args.dataset

    ratio = args.ratio
    
    llm = LLMCall('sk-8aa10cd1e98d4b0b95d6894e39771f6b', llm_name)
    if args.few_shot:
        input_file = './v2_2/raw_solution_modified_q_CoT_few_shot/' + dataset + '/' + llm_name + '/' + 'solution.jsonl'
        output_path = './v3_v22/final_solution_modified_q_CoT_few_shot/' + dataset + '/' + llm_name + '/'
        output_file = './v3_v22/final_solution_modified_q_CoT_few_shot/' + dataset + '/' + llm_name + '/' + 'ratio_' + str(args.ratio) + '_reasoning_steps.jsonl'

    else:
        input_file = './v2_2/raw_solution_modified_q_CoT/' + dataset + '/' + llm_name + '/' + 'solution.jsonl'
        output_path = './v3_v22/final_solution_modified_q_CoT/' + dataset + '/' + llm_name + '/'
        output_file = './v3_v22/final_solution_modified_q_CoT/' + dataset + '/' + llm_name + '/' + 'ratio_' + str(args.ratio) + '_reasoning_steps.jsonl'

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    js = read_jsonl(input_file)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for j in js:
            
            futures.append(executor.submit(process_question,j, ratio, llm, args.few_shot, dataset))
        
        with open(output_file, 'w') as f:
            for future in as_completed(futures):
                res = future.result()
                json.dump(res, f)
                f.write('\n')
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('--raw_llm_name', type=str, default='qwen-plus')
    # parser.add_argument('--modify_llm_name', type=str, default='qwen-plus')
    parser.add_argument('--llm_name', type=str, default='qwen')
    parser.add_argument('--dataset', type=str, default='MATH')
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--ratio', type=float, default=0.6)
    parser.add_argument('--few_shot', type=bool, default=False)
    args = parser.parse_args()

    main(args)