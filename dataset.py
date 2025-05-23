import json
import os

def load_data(dataset, path):
    questions = []
    answers = []
    decoder = json.JSONDecoder()

    if dataset == 'letter':
        with open(path) as f:
            json_data = json.load(f)
            json_data = json_data["examples"]
            for line in json_data:
                q = line["question"]
                a = line["answer"]
                questions.append(q)
                answers.append(a)
    elif dataset == 'gsm8k':
        from datasets import load_from_disk
        gsm8k = gsm8k = load_from_disk('data/gsm8k')
        gsm8k_test = gsm8k['test']
        questions = gsm8k_test['question']
        answers = gsm8k_test['answer']
    elif dataset == 'csqa':
        with open(path + '/csqa/dev_rand_split.jsonl') as f:
            lines = f.readlines()
            for line in lines:
                json_res = decoder.raw_decode(line)[0]
                choice = "Answer Choices:"
                for c in json_res["question"]["choices"]:
                    choice += " ("
                    choice += c["label"]
                    choice += ") "
                    choice += c["text"]
                questions.append(json_res["question"]["stem"].strip() + " " + choice)
                answers.append(json_res["answerKey"])
    elif dataset == 'strategyqa':
        with open(path+'/strategyqa/task.json') as f:
            json_data = json.load(f)["examples"]
            for line in json_data:
                q = line["input"].strip()
                a = int(line["target_scores"]["Yes"])
                if a == 1:
                    a = "yes"
                else:
                    a = "no"
                questions.append(q)
                answers.append(a)
    elif dataset == 'asdiv':
        with open(path) as f:
            json_data = json.load(f)["Instances"]
            for line in json_data:
                q = line['input'].strip()
                a = line['output'][0]
                questions.append(q)
                answers.append(a)
    elif dataset =='MATHQA':
        with open(path + '/MATHQA/MATHQA.jsonl') as f:
            data = []
            for line in f:
                data.append(json.loads(line.strip()))
            lines = f.readlines()
            for d in data:
                q = d["question"]
                a = d["answer"]
                questions.append(q)
                answers.append(a)
    elif dataset == 'MATH':
        math_algebra = []
        dir_name = path + '/MATH/test/algebra'
        for filename in os.listdir(dir_name):
            if (filename.endswith('.json')):
                d = json.load(open(dir_name + '/' + filename))
                math_algebra.append(d)

        # Partition the dataset into different levels
        math_algebra_by_level = {}
        for d in math_algebra:
            if (d['level'] in math_algebra_by_level):
                math_algebra_by_level[d['level']].append(d)
            else:
                math_algebra_by_level[d['level']] = [d]
        math_algebra_dev = math_algebra_by_level['Level 1'] + math_algebra_by_level['Level 2'] + math_algebra_by_level['Level 3']

        questions = []
        answers = []
        for d in math_algebra_dev:
            questions.append(d['problem'])
            answers.append(d['solution'])

    return questions, answers
