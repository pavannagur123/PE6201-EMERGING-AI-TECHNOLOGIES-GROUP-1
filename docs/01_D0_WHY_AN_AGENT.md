# Step 1 - D0: Why an agent at all

This document explains the design decision made before the agent implementation. The original pre-build version is preserved in Git commit `ac1c48b`, before the first agent-code commit.

## D0(a) - Ladder position

The system is a rung-7, single-agent ReAct loop. A claim does not follow one fixed sequence. A lapsed policy should stop after a policy lookup. A claim with several lines needs one coverage check per distinct procedure, and a pre-authorisation lookup is needed only after a coverage result says it is required. The model therefore selects the next tool call from facts returned during the run.

Rungs 1-6 do not provide the same behaviour:

| Rung | Why it is insufficient for this task |
|---|---|
| Single call | Cannot obtain traceable ground truth from several systems of record during the call. |
| Prompt chain | Uses a fixed sequence even when a claim should stop early. |
| Routing | Selects a lane but does not perform the variable lookup sequence within the lane. |
| Parallelisation | Helps after dependencies are known, but does not decide which conditional checks are required. |
| Orchestrator-workers | Adds agents and cost while the assignment requires one agent. |
| Evaluator-optimiser | Reviews an answer but does not choose the evidence-retrieval path. |

All tools before `issue_decision_letter` are read-only. That simulated local write is the first irreversible action and the governance boundary.

## D0(b) - The two tests

The ground-truth test passes because the claim, member, policy, hospital, procedure, required-document, pre-authorisation, and decided-claim records can contradict the model immediately. Missing or malformed records produce a loud technical escalation.

The reliability diagnostic will be completed from measured results:

`s = P^(1/T)`

Here, `P` is the measured whole-run pass rate and `T` is the measured median turn count. The value is diagnostic only: steps are not independent and free-text interpretation is less reliable than an ID lookup.

## D0(c) - Five testable properties of a good run

1. It identifies a cause traceable to an authoritative record and treats the member narrative as untrusted text.
2. It returns exactly one routing-table outcome: approve in principle, request a named document, or escalate.
3. It resolves every original claim line before approval and cites the rule for every excluded line.
4. It names missing evidence precisely and never invents a policy, coverage fact, document, or pre-authorisation.
5. It calls `issue_decision_letter` at most once, after the evidence is complete and the configured autonomy gate has passed.

## Evidence to add after implementation

- Two cases with different legitimate turn counts.
- Measured `P`, median `T`, and implied `s`.
- The observed effect of parallel calls on turns, tokens, cost, and correctness.
