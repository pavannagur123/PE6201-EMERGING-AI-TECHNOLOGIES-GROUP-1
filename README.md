# PE6201 A2 — Applied AI System (Problem A)

This repository contains a single-agent health-insurance claim first-response system, its fixture data, guardrails, evaluation harness, live-model results, cost model and reproduced failures.

## Reproduce the scripted run

No API key or network call is required after cloning.

1. Clone the repository and open `A2_CODE.ipynb` from the repository root.
2. Install Python 3.10+ with `pandas` and Jupyter, or open the notebook in Google Colab.
3. Choose **Run all**. The setup locates `data_A/` and `expected_outcomes_A_team.json` relative to the repository. If required, set environment variable `PE6201_REPO_ROOT` to the clone directory.
4. Confirm the expected headline results:
   - D2(c): 60 sequential and 60 parallel trials; 100% scripted correctness in both modes; average turns 6.10 versus 3.85.
   - D3: 10 guardrail tests passed, zero API calls.
   - D4: 40 cases, 10 negative cases, 60 scheduled trials.
   - D5(a): 60/60 complete records passed on the scripted backend, zero API calls.
   - D7: loop failure 8 turns before versus 2.

Generated tables are written to `D2c_results/`, `D3_result/`, `D4_results/`, `D5a_results/` and `D7_results/`.

## Live experiments

`A2_CODE.ipynb` contains the OpenRouter D2(b)/D5(b) experiments. Live cells require `OPENROUTER_API_KEY` and are not part of the default scripted reproduction. Saved controlled V1/V2 results are under `D2b_result/`; final model summaries are under `d5b/` and `D6_results/`. 

## Submission artefacts

- Agent and harness: `A2_CODE.ipynb`
- Fixtures and labels: `data_A/`, `expected_outcomes_A_team.json`
- Guardrails and evaluation: `D3_result/`, `D4_results/`, `D5a_results/`
- Cost model: `D6_results/`
- Contribution log: `CONTRIBUTIONS.md`
- Team declaration: `TEAM_DECLARATION.pdf`
- Demonstration video: add the URL from `VIDEO_LINK.txt` here before submission

## Safety boundary

All records are synthetic. Read tools access local fixture files. The gated decision action writes only a simulated local record and never contacts a member or live insurer system.
