# [ACL'25 Main] Stealthy Disruption of Chain-of-Thought: A Stepwise Attack Framework for LLMs

Code implementation of ACL paper "Stealthy Disruption of Chain-of-Thought: A Stepwise Attack Framework for LLMs"

<p align='center'>
<img src="assets/method.png" style="width: 80%;" />
</p>


## Usage

### 1. Question Modification (`QuestionModification.py`)

This component modifies original questions while preserving their semantic meaning.

```bash
python QuestionModification.py \
    --llm_name <model_name> \
    --dataset <dataset_name> \
    --few_shot <True/False> \
```

### 2. Solution Generation (`GetSolutionofQuestionModified.py`)

Generates CoT solutions for modified questions.

```bash
python GetSolutionofQuestionModified.py \
    --llm_name <model_name> \
    --dataset <dataset_name> \
    --few_shot <True/False> \
```


### 3. SEED-P Attack (`SEEDpAttack.py`)

Performs the SEED-P attack by introducing prior reasoning steps of the modified question.

```bash
python SEEDpAttack.py \
    --llm_name <model_name> \
    --dataset <dataset_name> \
    --ratio <float> \
    --few_shot <True/False> \
```


### 4. Evaluation (`QuestionModification.py`)

Evaluation the Accuracy and Attack Success Rate.


Step1: Run baseline (no attack) for comparison:

```bash
python SEEDpAttack.py \
    --llm_name <model_name> \
    --dataset <dataset_name> \
    --ratio 0.0 \
    --few_shot <True/False> \
```


Step 2: Compute ASR and Accuracy:

```bash
python Evaluation.py 
    --llm_name <model_name> \
    --dataset <dataset_name> \
    --ratio <float> \
    --few_shot <True/False> \
```

