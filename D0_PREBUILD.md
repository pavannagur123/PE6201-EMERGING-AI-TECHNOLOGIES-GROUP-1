# D0 - Why an agent at all

## D0(a) - Ladder position

This system belongs on rung 7: a single-agent ReAct loop. A single call cannot inspect the authoritative claim, policy, hospital, procedure, pre-authorisation, and claims-history records in a traceable sequence. A prompt chain, routing workflow, parallel workflow, or orchestrator-worker design could execute a fixed path, but the right path is not fixed: one claim may end after the policy lookup, while another requires a coverage check for each line and then a pre-authorisation lookup only for the lines that require it. An evaluator-optimiser adds a second model pass but does not determine which records must be fetched next. The system therefore needs a model to choose its next tool call from observations returned by the tools.

The first irreversible action is `issue_decision_letter`. It commits the insurer to a first response, so it is the governance cliff: all earlier tools are read-only; this action is explicitly gated and simulated as a local structured record.

## D0(b) - When an agent is justified

### Ground-truth test

The loop can be contradicted at machine speed by the systems of record: the claim row, active policy and date range, remaining annual limit, procedure exclusion and pre-authorisation rows, required-document rows, hospital status, and decided-claims history. Each tool returns a local fixture result immediately. If a required record is missing or a guardrail fires, the system escalates rather than inventing an answer.

### Reliability arithmetic

This section will be completed from measured D4/D7 results, not guessed values. The reported diagnostic is `s = P^(1/T)`, where `P` is measured whole-run pass rate and `T` is measured median turns. We will compare the observed result with the predicted effect of reducing turns through valid parallel calls, while noting that steps are neither independent nor equally error-prone.

## D0(c) - What a good run looks like

1. It identifies one traceable cause from an authoritative record, rather than accepting member-supplied narrative as an instruction.
2. It returns exactly one routing-table outcome: approve in principle, request a named document, or escalate to a human claims assessor.
3. It resolves every claim line before approving, including an explicit exclusion and rule for any non-payable line.
4. It requests the exact missing document or escalates when the records cannot support a safe decision; it never invents a pre-authorisation, coverage fact, or policy status.
5. It invokes `issue_decision_letter` no more than once and only after the evidence trail is complete and the confirm gate has passed.
