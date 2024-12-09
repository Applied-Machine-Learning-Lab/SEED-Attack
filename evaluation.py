import json
# from api import LLMCall
# from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import argparse
import random
import os
import re
import pickle
from evaluation_utils import *



def main(args):
    input_file = args.input_file

    success_save_path = '/'.join(args.input_file.split('/')[:-1]) + '/success.jsonl'
    fail_save_path = '/'.join(args.input_file.split('/')[:-1]) + '/fail.jsonl'
    abnormal_save_path = '/'.join(args.input_file.split('/')[:-1]) + '/abnormal.jsonl'

    if os.path.exists(success_save_path):
        os.remove(success_save_path)
    if os.path.exists(fail_save_path):
        os.remove(fail_save_path)

    raw_file = read_jsonl(args.raw_input_file)
    q2raw_s = {}
    for j in raw_file:
    
        q = j['question']
        raw_s = j['raw_solution']
        q2raw_s[q] = raw_s
    

    js = read_jsonl(input_file)
    if 'MATH' in input_file and 'MATHQA' not in input_file:
        success_incorrect = []
        raw_correct = []
        correct = []
        success = []
        correct_and_succss = 0

        for j in js:
            pred = j['final_solution']
            pred_raw = q2raw_s[j['question']]
            ans = j['answer']
            eval_ret = eval_answer_math(pred, ans, 1.0)
            eval_raw_ret = eval_answer_math(pred_raw, ans, 1.0)
            same_ret = eval2preds_math(pred, pred_raw)
            j['raw_solution'] = q2raw_s[j['question']]
            if eval_ret is not None:
                correct.append(eval_ret)
            if eval_raw_ret is not None:
                raw_correct.append(eval_raw_ret)
                
                if eval_raw_ret == True:
                    if eval_ret is None or eval_ret == False:
                        success.append(True)
                    else:
                        success.append(False)
                else:
                    if same_ret is not None:
                        success_incorrect.append(same_ret)

  

    

    elif 'gsm8k' in input_file:
        correct_and_succss = 0
        raw_correct = []
        correct = []
        success = []
        for j in js:
            pred = j['final_solution']
            pred_raw = q2raw_s[j['question']]
            ans = j['answer']
            eval_ret = eval_answer_gsm8k(pred, ans)
            eval_raw_ret = eval_answer_gsm8k(pred_raw, ans)
            same_ret = eval2preds_gsm8k(pred, pred_raw)
            if eval_ret is not None:
                correct.append(eval_ret)
            if eval_raw_ret is not None:
                raw_correct.append(eval_raw_ret)
                if eval_raw_ret == True:
                    if eval_ret is None or eval_ret == False:
                        success.append(True)
                    else:
                        success.append(False)
 
    elif 'csqa' in input_file:
        success_incorrect = []
        
        raw_correct = []
        correct = []
        success = []
        for j in js:
            pred = j['final_solution']
            pred_raw = q2raw_s[j['question']]
            ans = j['answer']
            eval_ret = eval_answer_cs_qa(pred, ans)
            eval_raw_ret = eval_answer_cs_qa(pred_raw, ans)
            same_ret = eval2preds_cs_qa(pred, pred_raw)
            if eval_ret is not None:
                correct.append(eval_ret)
            if eval_raw_ret is not None:
                raw_correct.append(eval_raw_ret)
                if eval_raw_ret == True:
                    if eval_ret is None or eval_ret == False:
                        success.append(True)
                    else:
                        success.append(False)
                else:
                    if same_ret is not None:
                        success_incorrect.append(same_ret)


    else:
        
        raw_correct = []
        correct = []
        success = []
        for j in js:
            pred = j['final_solution']
            pred_raw = q2raw_s[j['question']]
            ans = j['answer']
            eval_ret = eval_answer_math_qa(pred, ans)
            eval_raw_ret = eval_answer_math_qa(pred_raw, ans)
            same_ret = eval2preds_math_qa(pred, pred_raw)
            if eval_ret is not None:
                correct.append(eval_ret)
            if eval_raw_ret is not None:
                raw_correct.append(eval_raw_ret)
                if eval_raw_ret == True:
                    if eval_ret is None or eval_ret == False:
                        success.append(True)
                    else:
                        success.append(False)
            
    print('Raw Accuracy:', np.sum(raw_correct)/len(js))   
    print('Accuracy:', np.sum(correct)/len(js))
    print('ASR:', np.mean(success))
    print('ACC_Drop:', (np.mean(correct) - np.mean(raw_correct))/ np.mean(raw_correct))
    print("num of not NONE", len(correct))
    return np.mean(correct), np.mean(success)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--llm', type=str, default='qwen')
    parser.add_argument('--dataset', type=str, default='MATH')
    parser.add_argument('--few_shot', type=bool, default=True)

    args = parser.parse_args()

    for llm in ['qwen']:
        for dataset in ['csqa']:
            for few_shot in [False, True]:
                print('llm:', llm, 'dataset:', dataset, 'few_shot:', few_shot)

                args.llm = llm
                args.dataset = dataset
                args.few_shot = few_shot
                
                args.version = 'v3_v22'
                args.seed = ''
                for seed in ['']:
                    args.seed = seed


                    if args.few_shot:
                        args.raw_input_file = './v3_v22/final_solution_modified_q_CoT_few_shot/' + args.dataset + '/' + args.llm + '/ratio_0.0_reasoning_steps.jsonl'
                    else:
                        args.raw_input_file = './v3_v22/final_solution_modified_q_CoT/' + args.dataset + '/' + args.llm + '/ratio_0.0_reasoning_steps.jsonl'
                    for ratio in [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]:
                        print('ratio:', ratio)
                        if args.few_shot:
                            args.input_file = './'+args.version+'/final_solution_modified_q_CoT_few_shot/' + args.dataset + '/' + args.llm + '/' + args.seed + 'ratio_' + str(ratio) + '_reasoning_steps.jsonl'
                            
                        else:
                            args.input_file = './'+args.version+'/final_solution_modified_q_CoT/' + args.dataset + '/' + args.llm + '/'+ args.seed + 'ratio_' + str(ratio) + '_reasoning_steps.jsonl'
                        main(args)
                        print('-------')