# Prompting Styles Evaluation

## Work flow
Run zero-shot, few-shot, and role-based prompts on support tickets with Groq (Llama 3.1 8B).

Setup:
  pip install groq python-dotenv
  export GROQ_API_KEY="your_api_key_here"

Run:
  python run.py

The script reads:
  styles_eval.csv
  prompts/zero_shot.txt
  prompts/few_shot.txt
  prompts/role_based.txt

It writes:
  styles_eval_predictions.csv

## Accuracy

Total tickets processed: 30

Accuracy per prompting method:
- zero_shot_pred: **29/30 (96.7%)**
- few_shot_pred: **29/30 (96.7%)**
- role_based_pred: **30/30 (100.0%)**

- Average accuracy across all methods: **97.8%**

Detailed output saved to styles_eval_with_flags.csv


## Conclusion

Role-based prompting achieved 100% accuracy, slightly better than zero-shot and few-shot (96.7% each). 
```
Model used was: llama-3.3-70b-versatile
```