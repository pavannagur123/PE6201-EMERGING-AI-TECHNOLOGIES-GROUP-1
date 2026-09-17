# 4. Evaluation Economics and Cost to Serve

## 4.1 Method and assumptions

Problem A uses 8,000 claims per month. Human review is valued at US$38 per hour and each escalation takes 12 minutes, giving a fallback cost of US$7.60 per escalation.

For each live model, cost to serve has three layers: AI variable cost, expected human fallback, and operating cost. AI variable cost is `(average input tokens × input price + average output tokens × output price) / 1,000,000`. Expected fallback is `(1 − P) × US$7.60`, where `P` is complete-record accuracy. Operating cost is set to US$0 because no quantified hosting, monitoring, or support cost was supplied; this is an explicit limitation, not a claim that production operations are free. Monthly cost is cost per claim multiplied by 8,000.

Complete-record accuracy is used because it requires both the decision and the complete structured claim record to be correct. The fallback equation is the coursework proxy: `1 − P` is not a directly observed human-intervention rate.

The model prices used are US$0.20/US$1.20 per million input/output tokens for GPT-5.6 Luna, US$0.075/US$0.25 for GLM-5.3 Flash, US$0.0679/US$0.168 for DeepSeek V4 Flash, US$0.04/US$0.15 for Mercury 2.5, and US$0.10/US$0.40 for Qwen 2.5 7B Instruct. These are evaluation assumptions/point-in-time listed prices rather than provider invoices.

## 4.2 Live-model comparison

All five models report the same 40-case battery and 60 trials. The 10 non-approval cases were repeated three times, while the other 30 cases were run once.

| Rank | Model | Trials | Decision accuracy | Complete-record accuracy | Avg input tokens | Avg output tokens | AI cost/run | Expected cost/claim | Monthly cost |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | openai/gpt-5.6-luna | 60 | 83.3% | 80.0% | 7,664.20 | 522.83 | $0.002160 | $1.522160 | $12,177.28 |
| 2 | z-ai/glm-5.3-flash | 60 | 75.0% | 73.3% | 9,531.90 | 1,209.93 | $0.001017 | $2.027684 | $16,221.47 |
| 3 | deepseek/deepseek-v4-flash | 60 | 66.7% | 66.7% | 15,141.40 | 1,683.52 | $0.001311 | $2.534644 | $20,277.15 |
| 4 | inception/mercury-2.5 | 60 | 68.3% | 63.3% | 14,205.33 | 1,445.52 | $0.000785 | $2.787452 | $22,299.61 |
| 5 | qwen/qwen-2.5-7b-instruct | 60 | 61.7% | 55.0% | 15,243.55 | 399.20 | $0.001684 | $3.421684 | $27,373.47 |

GPT-5.6 Luna remains the economic recommendation. Its token charge is slightly higher than several alternatives, but token-price differences are only fractions of a cent per run. Its 80.0% complete-record accuracy reduces expected human fallback enough to produce the lowest total cost. Against the US$60,800 fully manual monthly baseline, it has US$48,622.72 of monthly headroom before additional fixed operating costs remove the saving.

Pavan's Qwen notebook reports 60 V2 trials and total estimated cost of US$0.101044. Applying the common D6 price formula to its average tokens gives US$0.001684 per run. Quincy's separate Qwen V1 pass is controlled-comparison evidence and is not counted as a sixth D5(b) model.

This recommendation is economic, not a claim that the model is production-ready. The team should also consider error types, safety, reproducibility, and whether the test distribution represents real claims.

## 4.3 Four measured cost levers

| Lever | Measurement | Result | Interpretation |
|---|---|---|---|
| Tool block size `B` | D2(a) token count | 225 tokens per turn | The block was held constant. Repeated exposure was 2,700 tokens in the 12-turn sequential illustration and 1,125 tokens in the five-turn batch illustration. |
| Turn count `T` | D2(c), same 60-trial scripted battery | 6.10 sequential to 3.85 parallel, a 36.9% reduction | Parallel independent calls reduce repeated prompt and tool-block exposure; accuracy remained 100% in both modes. |
| Observation size `D` | D7 tool-interface before/after | 58.03 to 28.09 tokens per call, a 51.6% reduction | The compact typed return removed stale fields; the associated pass rate rose from 88.3% to 100%. |
| Success rate `P` | D2(b) descriptor V1/V2 | 48.3% to 61.7%, an increase of 13.3 percentage points | Higher success reduces the dominant expected fallback term; V1 and V2 were each tested for 60 trials. |

`D` and `P` changed together in the descriptor/interface experiments, so this is an observed association rather than a clean causal estimate of one lever in isolation.

## 4.4 Sensitivity and break-even

Holding GPT-5.6 Luna's measured token cost constant, monthly cost is US$18,257.28 at 70% success, US$12,177.28 at 80%, and US$6,097.28 at 90%. A 10-percentage-point change in success changes monthly fallback cost by US$6,080, far more than the measured token-charge differences.

With a US$7.60 fully manual baseline and zero quantified operating cost, Luna's success-rate break-even is `0.002160236 / 7.60 = 0.0284%`. This is not a deployment threshold: unmeasured fixed costs, compliance requirements, harm from incorrect decisions, and the real escalation rate could materially change the result.

## 4.5 Evidence quality

The GLM notebook explicitly verifies 40 cases, 60 trial rows, 44 complete-record passes, and 644,510 tokens. Pavan's Qwen notebook displays both V1 and V2 60-trial summaries, with the V2 row used here. The DeepSeek, GPT-5.6 Luna, and Mercury submissions provide saved summary outputs and notebooks without a separate raw 60-row result file in the received package. These summaries are sufficient for the D6 comparison, while retaining raw per-trial exports would improve auditability.

## Sources

- PE6201 A2 FAQ, Problem A costing assumptions.
- Team D2/D3/D5(a)/D7 notebook and saved outputs.
- Five member D5(b) model outputs received by 15 September 2026.
- OpenRouter/listed model prices used as evaluation assumptions on 15 September 2026.
