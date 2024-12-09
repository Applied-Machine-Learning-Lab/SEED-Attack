import os
import random
from dataset import load_data
from api import LLMCall
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from few_shot_prompt import *


# messages = [{'role': 'user', 'content': 'Modify the given question by changing a digital or word leading to different answer. Return only the modified question without any explanation or note.\n' + q}]
def process_question(q, a, llm, args):
    if args.dataset =='csqa' or args.dataset == 'MATHQA':
        prompt_selected = prompt_choice
     

        messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role': 'user', 'content':prompt_selected + q}]
        response = llm.call(messages)
        messages.append({'role':'assistant','content':response})
        messages.append({'role':'user','content':"Select a different answer choice and create a new question that logically and strictly leads to the selected answer. Output the selected target answer choice after the `[Target]`, and the constructed question after the `[Question]` without any explanation or note.\n"})
        response = llm.call(messages)



    else:
        prompt_selected = prompt
        messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role': 'user', 'content':prompt_selected + q}]
        response = llm.call(messages)
        messages.append({'role':'assistant','content':response})
        messages.append({'role':'user','content':"Create a new question that logically and strictly leads to a different answer. Output the constructed question after the `[Question]` without any explanation or note.\n"})
        response = llm.call(messages)


    modified_q = response.split('[Question]')[-1].strip()

    if args.dataset == 'csqa':
        if 'Answer Choices:' not in modified_q:
            modified_q = modified_q + ' Answer Choices:' + q.split('Answer Choices:')[-1]
    elif args.dataset == 'MATHQA':
        if '\na )' not in modified_q:
            modified_q = modified_q + '\na )' + q.split('\na )')[-1]


    ret = {'raw_question':q, 'answer':a, 'modified_question':modified_q}
    return ret


def run(args):
    random.seed(args.seed)
    llm_name = args.llm_name
    dataset = args.dataset
    llm = LLMCall('', llm_name)
    output_path = './v2_2/modified_question/' + dataset + '/' + llm_name + '/'
    output_file = './v2_2/modified_question/' + dataset + '/' + llm_name + '/' + 'questions.jsonl'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    questions, answers = load_data(dataset, './data')
    


    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []

        # Create tasks for each question-answer pair
        for i in tqdm(range(min(len(questions),500))):
            q = questions[i]
            a = answers[i]
            futures.append(executor.submit(process_question, q, a, llm, args))

        # Write each result as a line in the JSONL file
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
    
    args = parser.parse_args()

    run(args)
