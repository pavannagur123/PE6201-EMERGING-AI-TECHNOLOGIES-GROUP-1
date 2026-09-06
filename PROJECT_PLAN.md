# PE6201 A2 delivery plan - Problem A

## Scope

Build one hand-rolled ReAct agent over local claim fixtures. The gated action is a simulated decision-record write; there is no UI, letter generation, live integration, or real customer data.

## Build sequence

1. D0 pre-build rationale and good-run criteria - complete in `D0_PREBUILD.md`.
2. Configure Problem A and verify a reproducible scripted baseline.
3. Design and document the tool contracts, poka-yoke choices, and parallel dependency rule.
4. Extend fixtures and answer key to 30-40 isolated cases, including 6-10 negative cases.
5. Implement a complete scripted backend, code checks, judgement queue, and ten guardrail cases.
6. Instrument sequential and parallel runs; reproduce and repair two failures.
7. Run the live battery only after scripted runs are stable; commit raw results and calculate costs from API usage.
8. Finish the report, five-minute demonstration, self-appraisal, declaration, README, and submission archive.

## Non-negotiable acceptance checks

- `BACKEND = "scripted"` remains the committed default and `python3 run_eval.py --all` runs offline.
- Every case has a fixture, answer-key label, and deterministic script.
- The action gate, step cap, token ceiling, and action de-duplication are code-enforced and tested.
- All reported live results retain model identifier, prompt version, trial count, API token usage, and cost.
