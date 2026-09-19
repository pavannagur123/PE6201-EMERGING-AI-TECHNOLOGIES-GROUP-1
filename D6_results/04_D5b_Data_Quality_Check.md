# D5(b) data-quality check

## Outcome

The five model outputs are sufficient to finish the D6 comparison. Each reports 60 trials and a distinct model identifier.

| Submission | Model | Confirmed evidence | Strength |
|---|---|---|---|
| `d5b/deepseek__deepseek-v4-flash_summary.csv` | deepseek/deepseek-v4-flash | 60 trials; 68.3% decision accuracy, 65.0% complete-record accuracy, average tokens, tool errors, timing | Summary-level |
| result chart2.xlsx + model_gpt5.6luna.ipynb | openai/gpt-5.6-luna | 60 trials; summary accuracy, tokens, tool errors, timing | Summary-level |
| inception__mercury-2.5_summary.csv + Mercury2.5.ipynb | inception/mercury-2.5 | 60 trials; summary accuracy, tokens, tool errors, timing | Summary-level |
| result-final.xlsx + glm.ipynb | z-ai/glm-5.3-flash | 40 cases, 60 trial rows, 44 complete-record passes, 644,510 tokens | Strongest received evidence |
| codea2 (3).ipynb | qwen/qwen-2.5-7b-instruct | V2: 60 trials, 61.7% decision accuracy, 55.0% complete-record accuracy, token and cost summary, 5/5 guardrails | Saved notebook output |

## Checks passed

- Five distinct D5(b) model identifiers are present.
- Every model summary contains 60 trials; 300 summarized trials in total.
- Accuracy values are within 0%–100% and reconcile to plausible integer pass counts out of 60.
- Average input and output tokens reconcile to average total tokens, subject to rounding.
- Qwen's notebook total estimated cost (US$0.101044) is consistent with its 60-run average after rounding.
- No included saved notebook contains an execution-error object in its final result evidence.

## Important separation

The D5b DeepSeek summary CSV, not the older `model_deepseek(1).ipynb` output, supplies the final DeepSeek figures. Pavan's Qwen V2 result is the fifth D5(b) model used in the cost ranking. Quincy's downloaded `D2b_results.zip` is a separate Qwen V1 controlled-comparison pass. It demonstrates Quincy's individual work but must not be counted as a sixth live model in D6.

## Limitations

- GLM has the strongest explicitly verified 60-row evidence. Other models are supported mainly by saved summaries/notebook outputs.
- Listed prices are evaluation assumptions, not invoices; routing, caching, discounts, and free endpoints can change actual charges.
- `1 − complete-record accuracy` is the assignment's fallback proxy, not an observed escalation rate.
