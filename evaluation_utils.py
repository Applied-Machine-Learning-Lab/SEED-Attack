import json
import re


def read_jsonl(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def find_answer(s):
    assert ('boxed' in s)
    ans = s.split('boxed')[-1]
    if (ans[0] == '{'):
        stack = 1
        a = ''
        for c in ans[1:]:
            if (c == '{'):
                stack += 1
                a += c
            elif (c == '}'):
                stack -= 1
                if (stack == 0): break
                a += c
            else:
                a += c
    else:
        a = ans.split('$')[0].strip()
    return a

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def eval_answer_cs_qa(pred_str, ans_str):
    if ('The answer is:' in pred_str):
        pred = pred_str.split('The answer is:')[-1].strip()
    elif ('the answer is:' in pred_str):
        pred = pred_str.split('the answer is:')[-1].strip()
    elif ('The answer choice is:' in pred_str):
        pred = pred_str.split('The answer choice is:')[-1].strip()
    else:
        return None
    pred = re.findall(r'A|B|C|D|E|F', pred)
    gold = re.findall(r'A|B|C|D|E', ans_str)[-1]

    if len(pred) == 1:
        return pred[0] == gold
    else:

        return False

def eval2preds_cs_qa(pred_str_1, pred_str_2):
    def get_pred(pred_str):
        if pred_str is None:
            return None
        if ('The answer is:' in pred_str):
            pred = pred_str.split('The answer is:')[-1].strip()
            return pred
        elif ('the answer is:' in pred_str):
            pred = pred_str.split('the answer is:')[-1].strip()
            return pred
        elif ('The answer choice is:' in pred_str):
            pred = pred_str.split('The answer choice is:')[-1].strip()
            return pred
        else:
            return None
    if pred_str_1 is None or pred_str_2 is None:
        return None
    pred_str_1 = get_pred(pred_str_1)
    pred_str_2 = get_pred(pred_str_2)
    if pred_str_1 is None or pred_str_2 is None:
        return None
    pred_1 = re.findall(r'A|B|C|D|E|F', pred_str_1)
    pred_2 = re.findall(r'A|B|C|D|E|F', pred_str_2)
    if len(pred_1) == 1 and len(pred_2) == 1:
        return pred_1[0] == pred_2[0]
    else:
        return False



def eval_answer_st_qa(pred_str, ans_str):
    if ('The answer is:' in pred_str):
        pred = pred_str.split('The answer is:')[-1].strip()
    elif ('the answer is:' in pred_str):
        pred = pred_str.split('the answer is:')[-1].strip()
    else:
        return None
    pred_str = pred_str.lower()
    pred_str = re.sub("\"|\'|\n|\.|\s|\:|\,", " ", pred_str)
    pred_str = pred_str.split(" ")
    pred = [i for i in pred_str if i in ("yes", "can", "no", "not", "cannot")]
    if len(pred) == 0:
        return None

    ans_str = ans_str.lower()
    ans_str = re.sub("\"|\'|\n|\.|\s|\:|\,", " ", ans_str)
    ans_str = ans_str.split(" ")
    gold = [j for j in ans_str if j in ("yes", "no")]

    pred = pred[-1]
    if pred in ['not', 'cannot']:
        pred = 'no'
    if pred in ['can']:
        pred = 'yes'
    gold = gold[-1]
    return pred == gold

def eval2preds_st_qa(pred_str_1, pred_str_2):
    def get_pred(pred_str):
        if pred_str is None:
            return None
        if ('The answer is:' in pred_str):
            pred = pred_str.split('The answer is:')[-1].strip()
            return pred
        elif ('the answer is:' in pred_str):
            pred = pred_str.split('the answer is:')[-1].strip()
            return pred
        else:
            return None
    if pred_str_1 is None or pred_str_2 is None:
        return None
    pred_str_1 = get_pred(pred_str_1)
    pred_str_2 = get_pred(pred_str_2)

    if pred_str_1 is None or pred_str_2 is None:
        return None
    


    pred_str_1 = pred_str_1.lower()
    pred_str_1 = re.sub("\"|\'|\n|\.|\s|\:|\,", " ", pred_str_1)
    pred_str_1 = pred_str_1.split(" ")
    pred_1 = [i for i in pred_str_1 if i in ("yes", "can", "no", "not", "cannot")]
    if len(pred_1) == 0:
        return None
    pred_str_2 = pred_str_2.lower()
    pred_str_2 = re.sub("\"|\'|\n|\.|\s|\:|\,", " ", pred_str_2)
    pred_str_2 = pred_str_2.split(" ")
    pred_2 = [i for i in pred_str_2 if i in ("yes", "can", "no", "not", "cannot")]
    if len(pred_2) == 0:
        return None
    pred_1 = pred_1[-1]
    pred_2 = pred_2[-1]
    if pred_1 in ['not', 'cannot']:
        pred_1 = 'no'
    if pred_1 in ['can']:
        pred_1 = 'yes'
    if pred_2 in ['not', 'cannot']:
        pred_2 = 'no'
    if pred_2 in ['can']:
        pred_2 = 'yes'
    return pred_1 == pred_2





def eval_answer_math(pred_str, ans_str, factor):
    if ('The answer is:' in pred_str):
        pred = pred_str.split('The answer is:')[-1].strip()
    elif ('the answer is:' in pred_str):
        pred = pred_str.split('the answer is:')[-1].strip()
    else:

        return None
 
    if pred != '':
      
        if (pred[:2] == '$$'):
            pred = pred.split('$$')[1]
       
        if (pred[0] == '$') and (pred[:3] != '$\$'):
            pred = pred.split('$')[1]
        # if (repr(pred[:3]) == r'$\$'): # may fix potential bug
     
        if (pred[:3] == '$\$'):
            if pred[:4] == '$\$$':
                pred = pred.split('$')[3]
            else:
                pred = pred.split('$')[2]
    
        if (pred[-1] == '.'):
            pred = pred.split('.')[0]
        if ('boxed{' in pred) and ('}' in pred):
            pred = pred.split('boxed{')[1].strip()
            pred = pred.split('}')[0].strip()
    gold = find_answer(ans_str)
    gold = gold.replace(',', '')
    pred = pred.replace(',', '')
    gold = gold.replace(' ', '')
    pred = pred.replace(' ', '')

    if isfloat(gold) and isfloat(pred):
        gold = float(gold) * factor
        pred = float(pred)
        if gold >= 0:
            return (pred > gold * 0.99999) and (pred < gold * 1.00001)
        else:
            return (pred < gold * 0.99999) and (pred > gold * 1.00001)
    else:
        if factor != 1.0:
            return False
        else:
            return gold in pred
        
def eval2preds_math(pred_str_1, pred_str_2):
    def get_pred(pred_str):
        if ('The answer is:' in pred_str):
            pred = pred_str.split('The answer is:')[-1].strip()
        elif ('the answer is:' in pred_str):
            pred = pred_str.split('the answer is:')[-1].strip()
        else:
            return None
        if pred != '':
            if (pred[:2] == '$$'):
                pred = pred.split('$$')[1]

            if (pred[0] == '$') and (pred[:3] != '$\$'):
                pred = pred.split('$')[1]
            # if (repr(pred[:3]) == r'$\$'): # may fix potential bug
            if (pred[:3] == '$\$'):
                if pred[:4] == '$\$$':
                    pred = pred.split('$')[3]
                else:
                    pred = pred.split('$')[2]
            if (pred[-1] == '.'):
                pred = pred.split('.')[0]
            if ('boxed{' in pred) and ('}' in pred):
                pred = pred.split('boxed{')[1].strip()
                pred = pred.split('}')[0].strip()
        pred = pred.replace(',', '')
        pred = pred.replace(' ', '')
        
        return pred
    pred_1 = get_pred(pred_str_1)
    pred_2 = get_pred(pred_str_2)
    if pred_1 is None or pred_2 is None:
        return None
    if isfloat(pred_1) and isfloat(pred_2):
        pred_1 = float(pred_1)
        pred_2 = float(pred_2)
        if pred_1 >= 0:
            return (pred_2 > pred_1 * 0.99999) and (pred_2 < pred_1 * 1.00001)
        else:
            return (pred_2 < pred_1 * 0.99999) and (pred_2 > pred_1 * 1.00001)
    else:
        return pred_1 in pred_2


def find_answer_gsm8k(s):
    ans_str = s.split('#### ')[-1]
    ans_str = ans_str.replace(',', '')
    return ans_str

def eval_answer_gsm8k(pred_str, ans_str):
    ans_str = find_answer_gsm8k(ans_str)
    if pred_str is None:
        return None
    if ('The answer is:' in pred_str):
        pred = pred_str.split('The answer is:')[-1].strip()
    elif ('the answer is:' in pred_str):
        pred = pred_str.split('the answer is:')[-1].strip()
    else:
        return None
    pred = pred.replace(',', '')
    preds = re.findall(r'-?\d+(?:\.\d+)?', pred)
    if preds == []:
        return None
    final_pred = preds[-1]
    if final_pred[-3:] == '.00':
        final_pred = final_pred[:-3]

    if ans_str == final_pred:
        return True
    else:
        return False

def eval2preds_gsm8k(pred_str_1, pred_str_2):
    def get_pred(pred_str):
        if pred_str is None:
            return None
        if ('The answer is:' in pred_str):
            pred = pred_str.split('The answer is:')[-1].strip()
        elif ('the answer is:' in pred_str):
            pred = pred_str.split('the answer is:')[-1].strip()
        else:
            return None
        pred = pred.replace(',', '')
        preds = re.findall(r'-?\d+(?:\.\d+)?', pred)
        if preds == []:
            return None
        final_pred = preds[-1]
        if final_pred[-3:] == '.00':
            final_pred = final_pred[:-3]
        return final_pred
    pred_1 = get_pred(pred_str_1)
    pred_2 = get_pred(pred_str_2)
    if pred_1 is None or pred_2 is None:
        return None
    return pred_1 == pred_2



# def read_jsonl(file_path):
#     data = []
#     with open(file_path, 'r') as f:
#         for line in f:
#             data.append(json.loads(line.strip()))
#     return data

# def find_answer(s):
#     assert ('boxed' in s)
#     ans = s.split('boxed')[-1]
#     if (ans[0] == '{'):
#         stack = 1
#         a = ''
#         for c in ans[1:]:
#             if (c == '{'):
#                 stack += 1
#                 a += c
#             elif (c == '}'):
#                 stack -= 1
#                 if (stack == 0): break
#                 a += c
#             else:
#                 a += c
#     else:
#         a = ans.split('$')[0].strip()
#     return a

# def isfloat(num):
#     try:
#         float(num)
#         return True
#     except ValueError:
#         return False

def eval_answer_math_qa(pred_str, ans_str):
    if ('The answer is:' in pred_str):
        pred = pred_str.split('The answer is:')[-1].strip()
    elif ('the answer is:' in pred_str):
        pred = pred_str.split('the answer is:')[-1].strip()
    elif ('The answer choice is:' in pred_str):
        pred = pred_str.split('The answer choice is:')[-1].strip()
    else:
        return None
    # pred = re.findall(r'a|b|c|d|e|f', pred)
    # gold = re.findall(r'a|b|c|d|e|f', ans_str)[-1]

    # if len(pred) >= 1:
    #     return pred[0] == gold
    # else:
    #     return None
    if len(pred) ==0:
        return None
    if pred[0] >= 'a' and pred[0] <= 'f':
        if pred[0] == ans_str[0]:
            return True
        else:
            return False
    else:
        return None

def eval2preds_math_qa(pred_str_1, pred_str_2):
    def get_pred(pred_str):
        if pred_str is None:
            return None
        if ('The answer is:' in pred_str):
            pred = pred_str.split('The answer is:')[-1].strip()
            return pred
        elif ('the answer is:' in pred_str):
            pred = pred_str.split('the answer is:')[-1].strip()
            return pred
        elif ('The answer choice is:' in pred_str):
            pred = pred_str.split('The answer choice is:')[-1].strip()
            return pred
        else:
            return None
    if pred_str_1 is None and pred_str_2 is None:
        return None
    pred_str_1 = get_pred(pred_str_1)
    pred_str_2 = get_pred(pred_str_2)
    if pred_str_1 is None or pred_str_2 is None:
        return None
    if len(pred_str_1) == 0 or len(pred_str_2) == 0:
        return None
    if pred_str_1[0] >= 'a' and pred_str_1[0] <= 'f':
        if pred_str_1[0] == pred_str_2[0]:
            return True
        else:
            return False
    else:
        return None
    # pred_1 = re.findall(r'a|b|c|d|e|f', pred_str_1)
    # pred_2 = re.findall(r'a|b|c|d|e|f', pred_str_2)
    # if len(pred_1) >= 1 and len(pred_2) >= 1:
    #     return pred_1[0] == pred_2[0]
    # else:
    #     return False





# def eval_answer_cs_qa(pred_str, ans_str):
#     if ('The answer is:' in pred_str):
#         pred = pred_str.split('The answer is:')[-1].strip()
#     elif ('the answer is:' in pred_str):
#         pred = pred_str.split('the answer is:')[-1].strip()
#     elif ('The answer choice is:' in pred_str):
#             pred = pred_str.split('The answer choice is:')[-1].strip()
#     else:
#         return None
#     pred = re.findall(r'A|B|C|D|E|F', pred)
#     gold = re.findall(r'A|B|C|D|E', ans_str)[-1]

#     if len(pred) >= 1:
#         return pred[0] == gold
#     else:

#         return False

# def eval2preds_cs_qa(pred_str_1, pred_str_2):
#     def get_pred(pred_str):
#         if pred_str is None:
#             return None
#         if ('The answer is:' in pred_str):
#             pred = pred_str.split('The answer is:')[-1].strip()
#             return pred
#         elif ('the answer is:' in pred_str):
#             pred = pred_str.split('the answer is:')[-1].strip()
#             return pred
#         elif ('The answer choice is:' in pred_str):
#             pred = pred_str.split('The answer choice is:')[-1].strip()
#             return pred
#         else:
#             return None
#     if pred_str_1 is None or pred_str_2 is None:
#         return None
#     pred_str_1 = get_pred(pred_str_1)
#     pred_str_2 = get_pred(pred_str_2)
#     if pred_str_1 is None or pred_str_2 is None:
#         return None
#     pred_1 = re.findall(r'A|B|C|D|E|F', pred_str_1)
#     pred_2 = re.findall(r'A|B|C|D|E|F', pred_str_2)
#     if len(pred_1) == 1 and len(pred_2) == 1:
#         return pred_1[0] == pred_2[0]
#     else:
#         return False



# def eval_answer_st_qa(pred_str, ans_str):
#     if ('The answer is:' in pred_str):
#         pred = pred_str.split('The answer is:')[-1].strip()
#     elif ('the answer is:' in pred_str):
#         pred = pred_str.split('the answer is:')[-1].strip()
#     else:
#         return None
#     pred_str = pred_str.lower()
#     pred_str = re.sub("\"|\'|\n|\.|\s|\:|\,", " ", pred_str)
#     pred_str = pred_str.split(" ")
#     pred = [i for i in pred_str if i in ("yes", "can", "no", "not", "cannot")]
#     if len(pred) == 0:
#         return None

#     ans_str = ans_str.lower()
#     ans_str = re.sub("\"|\'|\n|\.|\s|\:|\,", " ", ans_str)
#     ans_str = ans_str.split(" ")
#     gold = [j for j in ans_str if j in ("yes", "no")]

#     pred = pred[-1]
#     if pred in ['not', 'cannot']:
#         pred = 'no'
#     if pred in ['can']:
#         pred = 'yes'
#     gold = gold[-1]
#     return pred == gold

# def eval2preds_st_qa(pred_str_1, pred_str_2):
#     def get_pred(pred_str):
#         if pred_str is None:
#             return None
#         if ('The answer is:' in pred_str):
#             pred = pred_str.split('The answer is:')[-1].strip()
#             return pred
#         elif ('the answer is:' in pred_str):
#             pred = pred_str.split('the answer is:')[-1].strip()
#             return pred
#         else:
#             return None
#     if pred_str_1 is None or pred_str_2 is None:
#         return None
#     pred_str_1 = get_pred(pred_str_1)
#     pred_str_2 = get_pred(pred_str_2)

#     if pred_str_1 is None or pred_str_2 is None:
#         return None
    


#     pred_str_1 = pred_str_1.lower()
#     pred_str_1 = re.sub("\"|\'|\n|\.|\s|\:|\,", " ", pred_str_1)
#     pred_str_1 = pred_str_1.split(" ")
#     pred_1 = [i for i in pred_str_1 if i in ("yes", "can", "no", "not", "cannot")]
#     if len(pred_1) == 0:
#         return None
#     pred_str_2 = pred_str_2.lower()
#     pred_str_2 = re.sub("\"|\'|\n|\.|\s|\:|\,", " ", pred_str_2)
#     pred_str_2 = pred_str_2.split(" ")
#     pred_2 = [i for i in pred_str_2 if i in ("yes", "can", "no", "not", "cannot")]
#     if len(pred_2) == 0:
#         return None
#     pred_1 = pred_1[-1]
#     pred_2 = pred_2[-1]
#     if pred_1 in ['not', 'cannot']:
#         pred_1 = 'no'
#     if pred_1 in ['can']:
#         pred_1 = 'yes'
#     if pred_2 in ['not', 'cannot']:
#         pred_2 = 'no'
#     if pred_2 in ['can']:
#         pred_2 = 'yes'
#     return pred_1 == pred_2





# def eval_answer_math(pred_str, ans_str, factor):
#     if ('The answer is:' in pred_str):
#         pred = pred_str.split('The answer is:')[-1].strip()
#     elif ('the answer is:' in pred_str):
#         pred = pred_str.split('the answer is:')[-1].strip()
#     else:

#         return None
 
#     if pred != '':
      
#         if (pred[:2] == '$$'):
#             pred = pred.split('$$')[1]
       
#         if (pred[0] == '$') and (pred[:3] != '$\$'):
#             pred = pred.split('$')[1]
#         # if (repr(pred[:3]) == r'$\$'): # may fix potential bug
     
#         if (pred[:3] == '$\$'):
#             if pred[:4] == '$\$$':
#                 pred = pred.split('$')[3]
#             else:
#                 pred = pred.split('$')[2]
    
#         if (pred[-1] == '.'):
#             pred = pred.split('.')[0]
#         if ('boxed{' in pred) and ('}' in pred):
#             pred = pred.split('boxed{')[1].strip()
#             pred = pred.split('}')[0].strip()
#     gold = find_answer(ans_str)
#     gold = gold.replace(',', '')
#     pred = pred.replace(',', '')
#     gold = gold.replace(' ', '')
#     pred = pred.replace(' ', '')

#     if isfloat(gold) and isfloat(pred):
#         gold = float(gold) * factor
#         pred = float(pred)
#         if gold >= 0:
#             return (pred > gold * 0.99999) and (pred < gold * 1.00001)
#         else:
#             return (pred < gold * 0.99999) and (pred > gold * 1.00001)
#     else:
#         if factor != 1.0:
#             return False
#         else:
#             return gold == pred
        
# def eval2preds_math(pred_str_1, pred_str_2):
#     def get_pred(pred_str):
#         if ('The answer is:' in pred_str):
#             pred = pred_str.split('The answer is:')[-1].strip()
#         elif ('the answer is:' in pred_str):
#             pred = pred_str.split('the answer is:')[-1].strip()
#         else:
#             return None
#         if pred != '':
#             if (pred[:2] == '$$'):
#                 pred = pred.split('$$')[1]

#             if (pred[0] == '$') and (pred[:3] != '$\$'):
#                 pred = pred.split('$')[1]
#             # if (repr(pred[:3]) == r'$\$'): # may fix potential bug
#             if (pred[:3] == '$\$'):
#                 if pred[:4] == '$\$$':
#                     pred = pred.split('$')[3]
#                 else:
#                     pred = pred.split('$')[2]
#             if (pred[-1] == '.'):
#                 pred = pred.split('.')[0]
#             if ('boxed{' in pred) and ('}' in pred):
#                 pred = pred.split('boxed{')[1].strip()
#                 pred = pred.split('}')[0].strip()
#         pred = pred.replace(',', '')
#         pred = pred.replace(' ', '')
        
#         return pred
#     pred_1 = get_pred(pred_str_1)
#     pred_2 = get_pred(pred_str_2)
#     if pred_1 is None or pred_2 is None:
#         return None
#     if isfloat(pred_1) and isfloat(pred_2):
#         pred_1 = float(pred_1)
#         pred_2 = float(pred_2)
#         if pred_1 >= 0:
#             return (pred_2 > pred_1 * 0.99999) and (pred_2 < pred_1 * 1.00001)
#         else:
#             return (pred_2 < pred_1 * 0.99999) and (pred_2 > pred_1 * 1.00001)
#     else:
#         return pred_1 == pred_2


# def find_answer_gsm8k(s):
#     ans_str = s.split('#### ')[-1]
#     ans_str = ans_str.replace(',', '')
#     return ans_str

# def eval_answer_gsm8k(pred_str, ans_str):
#     ans_str = find_answer_gsm8k(ans_str)
#     if pred_str is None:
#         return None
#     if ('The answer is:' in pred_str):
#         pred = pred_str.split('The answer is:')[-1].strip()
#     elif ('the answer is:' in pred_str):
#         pred = pred_str.split('the answer is:')[-1].strip()
#     else:
#         return None
#     pred = pred.replace(',', '')
#     preds = re.findall(r'-?\d+(?:\.\d+)?', pred)
#     if preds == []:
#         return None
#     final_pred = preds[-1]
#     if final_pred[-3:] == '.00':
#         final_pred = final_pred[:-3]

#     if ans_str == final_pred:
#         return True
#     else:
#         return False

# def eval2preds_gsm8k(pred_str_1, pred_str_2):
#     def get_pred(pred_str):
#         if pred_str is None:
#             return None
#         if ('The answer is:' in pred_str):
#             pred = pred_str.split('The answer is:')[-1].strip()
#         elif ('the answer is:' in pred_str):
#             pred = pred_str.split('the answer is:')[-1].strip()
#         else:
#             return None
#         pred = pred.replace(',', '')
#         preds = re.findall(r'-?\d+(?:\.\d+)?', pred)
#         if preds == []:
#             return None
#         final_pred = preds[-1]
#         if final_pred[-3:] == '.00':
#             final_pred = final_pred[:-3]
#         return final_pred
#     pred_1 = get_pred(pred_str_1)
#     pred_2 = get_pred(pred_str_2)
#     if pred_1 is None or pred_2 is None:
#         return None
#     return pred_1 == pred_2