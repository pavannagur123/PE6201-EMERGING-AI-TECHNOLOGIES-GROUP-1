# 2. The tool layer

We used eight tools because the task is a narrow first-response decision, not an open-ended investigation. Six cover the required checks: claim, policy, procedure coverage, pre-authorisation, hospital status and the simulated decision letter. We added `check_duplicate_claim` and `check_required_documents` because the routing rule requires an escalation for an already decided claim and a named request when an attachment is missing.

We did not add a generic search tool or a narrative-interpretation tool. The facts needed for a decision are already in named fixture fields, while the member narrative is untrusted. A broad search tool would overlap with the ID-based tools, add to the prompt every turn and be harder to test. This was a design choice, rather than a tool removed after an experiment.

| Tool | Why it is needed |
| --- | --- |
| `get_claim` | Starts the case and returns the identifiers for later checks. |
| `lookup_policy` | Checks status, dates and remaining annual cover. |
| `check_coverage` | Resolves one procedure and whether it requires pre-authorisation. |
| `get_preauthorisation` | Confirms that the authorisation is valid on the service date. |
| `lookup_hospital` | Records the required panel-status check. |
| `check_duplicate_claim` | Supports the duplicate-claim escalation. |
| `check_required_documents` | Identifies the exact missing attachment. |
| `issue_decision_letter` | The only write; it records a gated local log entry. |

Each tool has a six-field descriptor: signature, purpose, inputs, bounded return, failure conditions and irreversibility. The boundaries reduce confusion: `lookup_policy` is a claim-level check, while `check_coverage` is a line-level check. We used three poka-yoke controls. ID patterns reject malformed values, `additionalProperties=false` rejects invented arguments, and the write tool gives the model no way to confirm an action by itself. An unconfirmed decision cannot be recorded.

For the descriptor experiment, we changed only `check_coverage`. V1 returned `code`, `description`, `requires_preauth`, `excluded` and `exclusion_rule`. V2 returned `code`, `coverage_status`, `preauthorisation_required` and `exclusion_rule`, and stated that an excluded line does not automatically escalate the whole claim. The model, temperature and 40-case set stayed the same. There were 30 ordinary trials and three trials for each of 10 negative cases, giving 60 trials per version.

| Measure | V1 | V2 |
| --- | ---: | ---: |
| Decision accuracy | 48.3% | 61.7% |
| Full-record accuracy | 43.3% | 55.0% |
| Tool-return token proxy per call | 58.23 | 58.45 |
| Interface guardrails passed | 5/5 | 5/5 |

V2 improved decision accuracy by 13.4 percentage points and full-record accuracy by 11.7 points. It did not reduce the tool-return token proxy, so we treat the rewrite as an accuracy improvement rather than a cost saving.

Our dependency rule is that calls may share a turn only when no call in the block needs another call's output. `get_claim` runs first. Duplicate, policy and hospital checks can then run together; independent coverage checks can share the next turn. Pre-authorisation waits until coverage identifies the relevant procedures. We defer document checking even though it only needs the claim ID, because an earlier escalation may make it unnecessary.

In the 60-trial scripted comparison, sequential and parallel runs both achieved a 100.0% full-record pass rate and used 6.10 tool calls per trial. Parallel calling reduced mean turns from 6.10 to 3.85 and estimated input tokens from 8,177.67 to 5,135.25. Estimated input cost for all trials fell from US$0.049071 to US$0.030812, a 37.2% reduction. These are scripted estimates based on a 1,200-token prefix and a characters/4 proxy, not live-model billing.
