"""
PE6201 · A2 scaffold — THE TWO BACKENDS
====================================================================
A backend answers ONE question: given the conversation so far, what
does the agent do next?

It returns either
    {"tool": "name", "args": {...}, "thought": "..."}      -> call a tool
    {"final": {...}, "thought": "..."}                     -> conclude

EXACTLY ONE FUNCTION IN THIS WHOLE REPOSITORY KNOWS A VENDOR EXISTS.
It is `_live_call` at the bottom. That is the D5 requirement, and it is
what makes swapping models a one-string change.

--------------------------------------------------------------------
WHY THE SCRIPTED BACKEND IS NOT A TOY

It replays a fixed sequence of decisions for a known case. That makes
your whole run deterministic, free, and reproducible by a stranger -
which is what D5(a) is marked on, and what makes D3(b) and D7 cost
nothing.

It is also the honest way to test your CODE. A guardrail either fires
or it does not; a model has no say in that. Scripting the model's
moves is how you test the parts you wrote.
====================================================================
"""
import json
import urllib.request

import config


# =====================================================================
# SCRIPTED
# =====================================================================
# One entry per case you have scripted. The value is the list of moves
# the "model" makes, in order.
#
# ADD YOUR OWN CASES HERE. To script a case: work out what a correct
# agent would do, step by step, and write the steps down. If you cannot
# write them down, you do not yet understand the case - which is
# useful to discover now rather than at 2am on the 13th.
SCRIPTS = {

    # ---------------------------------------------------------------
    # PROBLEM B · REF-5602 - the booking from Appendix A.
    # Six tool calls. Turns 2 and 3 each fire two calls at once, so the
    # run is FOUR turns rather than six. See D2(c) in the brief.
    # ---------------------------------------------------------------
    "REF-5602": [
        {"thought": "I have a referral id and nothing else. Fetch the record.",
         "calls": [("get_referral", {"referral_id": "REF-5602"})]},

        {"thought": "Two things I need next do not depend on each other: "
                    "the specialty's rules, and whether this patient already "
                    "has an appointment. Fire both together.",
         "calls": [("check_referral_criteria", {"specialty": "OPH",
                                                "referral_id": "REF-5602"}),
                   ("lookup_patient", {"patient_id": "P-1180"})]},

        {"thought": "No red flag, right department, VF-01 attached, no "
                    "duplicate. Band is routine, so the window runs 8 weeks "
                    "from as_of 2026-09-09, to 2026-11-04. I will query both "
                    "halves of that window at once. This is a gamble: if the "
                    "near half had a slot, the second query was wasted.",
         "calls": [("get_clinic_slots", {"specialty": "OPH", "band": "routine",
                                         "from": "2026-09-09", "to": "2026-09-30"}),
                   ("get_clinic_slots", {"specialty": "OPH", "band": "routine",
                                         "from": "2026-10-01", "to": "2026-11-04"})]},

        {"thought": "OPH-C2 is full until 14 October. First bookable slot "
                    "inside the window is 2026-10-14 11:20. Book it - this is "
                    "the irreversible step, so it goes through the gate.",
         "calls": [("book_slot", {"clinic": "OPH-C2", "date": "2026-10-14",
                                  "time": "11:20", "referral_id": "REF-5602"})]},

        {"final": {
            "decision": "book",
            "booked": {"clinic": "OPH-C2", "date": "2026-10-14", "time": "11:20"},
            "reason": "Urgency band routine, so an 8-week window from as_of "
                      "2026-09-09 closing 2026-11-04; booked at 5 weeks. "
                      "VF-01 present. No existing OPH appointment for P-1180. "
                      "OPH-C2 was full until 2026-10-14.",
         },
         "thought": "Record the band, the window, the tests and the duplicate "
                    "check - the answer key asks for all four."},
    ],

    # ---------------------------------------------------------------
    # PROBLEM A · CLM-8842 - the partly payable claim from Appendix A.
    # Three lines, one of them excluded, one needing a pre-authorisation.
    # ---------------------------------------------------------------
    "CLM-8842": [
        {"thought": "Turn 1 must run alone: everything else needs the member, "
                    "the hospital and the LINE ITEMS this returns.",
         "calls": [("get_claim", {"claim_id": "CLM-8842"})]},

        {"thought": "Now five calls that depend on nothing but that record. "
                    "The policy, the hospital, and one coverage check PER LINE "
                    "- three lines, three checks. All independent, so one turn.",
         "calls": [("lookup_policy", {"member_id": "M-2214"}),
                   ("check_coverage", {"code": "47120", "policy_id": "POL-3310"}),
                   ("check_coverage", {"code": "31255", "policy_id": "POL-3310"}),
                   ("check_coverage", {"code": "62480", "policy_id": "POL-3310"}),
                   ("lookup_hospital", {"hospital_id": "H-114"})]},

        {"thought": "This one CANNOT join the turn above: I did not know which "
                    "line needed a pre-authorisation until coverage answered. "
                    "That is the dependency rule. Only 62480 needs one.",
         "calls": [("get_preauthorisation", {"member_id": "M-2214",
                                             "procedure_code": "62480",
                                             "date_of_service": "2026-09-02"})]},

        {"thought": "A disposition for every line, then send. This is the "
                    "irreversible step, so it goes through the gate - and it "
                    "is a turn like any other.",
         "calls": [("issue_decision_letter", {
             "claim_id": "CLM-8842",
             "decision": "approve_in_principle",
             "lines_resolved": 3,
             "approved_total": 2180,
             "refused_total": 300})]},

        {"final": {
            "decision": "approve_in_principle",
            "reason": "3 lines. 47120 covered (1400). 62480 covered, PA-5521 "
                      "cited, valid on 2026-09-02 (780). 31255 refused under "
                      "EX-14 cosmetic dermatology (300). approved_total 2180, "
                      "refused_total 300. H-114 is on panel.",
         },
         "thought": "Eight calls, four turns. Not an approve and not a "
                    "decline: one decision letter covering both."},
    ],
}


def _claim_open(case_id):
    return {"thought": "Fetch the claim first; every later lookup needs facts from it.",
            "calls": [("get_claim", {"claim_id": case_id})]}


def _claim_checks(member_id, policy_id, hospital_id, service_date, lines):
    """A canned, dependency-valid second turn for a normal claim.

    The script values are deliberately explicit. This is a scripted backend:
    it does not infer the answer from a hidden rules engine, and a reviewer can
    inspect every tool request that will be replayed.
    """
    calls = [("lookup_policy", {"member_id": member_id}),
             ("check_duplicate_claim", {"member_id": member_id,
                                        "hospital_id": hospital_id,
                                        "date_of_service": service_date,
                                        "lines": lines}),
             ("lookup_hospital", {"hospital_id": hospital_id})]
    calls.extend(("check_coverage", {"code": line["code"],
                                      "policy_id": policy_id})
                 for line in lines)
    return {"thought": "The policy, duplicate check, hospital status, and one "
                        "coverage check per line are independent after the claim "
                        "has been read, so run them in one turn.",
            "calls": calls}


def _approve(case_id, reason, lines_resolved, approved_total, refused_total=0):
    return [
        {"thought": "All required facts are resolved. Take the gated action once.",
         "calls": [("issue_decision_letter", {
             "claim_id": case_id,
             "decision": "approve_in_principle",
             "lines_resolved": lines_resolved,
             "approved_total": approved_total,
             "refused_total": refused_total,
         })]},
        {"thought": "Return the evidence-backed first response.",
         "final": {"decision": "approve_in_principle", "reason": reason}},
    ]


# Complete, offline Problem A evaluation scripts for the released cases.
# Extra cases are added in the same format after their fixture rows and labels.
SCRIPTS.update({
    "CLM-8850": [
        _claim_open("CLM-8850"),
        _claim_checks("M-5502", "POL-6001", "H-207", "2026-09-04",
                      [{"code": "99213", "amount": 180}]),
        *_approve("CLM-8850", "99213 covered; approved_total 180. Policy POL-6001 "
                                  "is active and H-207 is on panel. CLM-8702 is not a "
                                  "duplicate because its date of service differs.", 1, 180),
    ],
    "CLM-8861": [
        _claim_open("CLM-8861"),
        _claim_checks("M-5502", "POL-6001", "H-207", "2026-09-05",
                      [{"code": "27447", "amount": 8200}, {"code": "80053", "amount": 90}]),
        {"thought": "Only 27447 requires pre-authorisation; fetch it after coverage.",
         "calls": [("get_preauthorisation", {"member_id": "M-5502", "procedure_code": "27447",
                                               "date_of_service": "2026-09-05"})]},
        *_approve("CLM-8861", "27447 covered with PA-5702 valid on 2026-09-05; "
                                  "80053 covered; approved_total 8290.", 2, 8290),
    ],
    "CLM-8874": [
        _claim_open("CLM-8874"),
        _claim_checks("M-2214", "POL-3310", "H-330", "2026-09-06",
                      [{"code": "70553", "amount": 620}]),
        *_approve("CLM-8874", "70553 covered; approved_total 620. H-330 is non-panel.", 1, 620),
    ],
    "CLM-8888": [
        _claim_open("CLM-8888"),
        _claim_checks("M-6118", "POL-7220", "H-114", "2026-09-08",
                      [{"code": "47120", "amount": 900}, {"code": "62480", "amount": 1200},
                       {"code": "31255", "amount": 300}]),
        {"thought": "62480 is the only line needing pre-authorisation; none is a request, not a refusal.",
         "calls": [("get_preauthorisation", {"member_id": "M-6118", "procedure_code": "62480",
                                               "date_of_service": "2026-09-08"})]},
        {"thought": "Request the exact missing evidence and retain resolved lines.",
         "final": {"decision": "request_document",
                   "missing": "pre-authorisation reference for line 62480, valid on 2026-09-08",
                   "reason": "62480 requires a pre-authorisation valid on 2026-09-08; none was found. "
                             "47120 is covered and 31255 is refused under EX-14."}},
    ],
    "CLM-8894": [
        _claim_open("CLM-8894"),
        _claim_checks("M-6118", "POL-7220", "H-207", "2026-09-09",
                      [{"code": "29881", "amount": 1950}]),
        {"thought": "29881 requires pre-authorisation; a valid one must cover the service date.",
         "calls": [("get_preauthorisation", {"member_id": "M-6118", "procedure_code": "29881",
                                               "date_of_service": "2026-09-09"})]},
        {"thought": "The available authorisation expired, so ask for a current one.",
         "final": {"decision": "request_document",
                   "missing": "current pre-authorisation for line 29881, valid on 2026-09-09",
                   "reason": "PA-5640 exists but expired on 2026-05-31, so it does not cover "
                             "the 2026-09-09 service date."}},
    ],
    "CLM-8901": [
        _claim_open("CLM-8901"),
        _claim_checks("M-5502", "POL-6001", "H-114", "2026-09-10",
                      [{"code": "45378", "amount": 1150}]),
        {"thought": "The required itemised bill is absent; request it rather than issuing a decision.",
         "final": {"decision": "request_document", "missing": "itemised bill for line 45378",
                   "reason": "45378 requires an itemised bill, which is absent from the claim."}},
    ],
    "CLM-8910": [
        _claim_open("CLM-8910"),
        {"thought": "Policy status can end the run before any line pricing.",
         "calls": [("lookup_policy", {"member_id": "M-4471"})]},
        {"thought": "The policy is lapsed; escalate immediately.",
         "final": {"decision": "escalate", "trigger": "policy_lapsed",
                   "escalate_to": "human claims assessor",
                   "reason": "POL-5588 status is lapsed; no line pricing was performed."}},
    ],
    "CLM-8917": [
        _claim_open("CLM-8917"),
        {"thought": "Check the policy dates before line-level work.",
         "calls": [("lookup_policy", {"member_id": "M-5502"})]},
        {"thought": "The service date is outside the policy period.",
         "final": {"decision": "escalate", "trigger": "outside_policy_dates",
                   "escalate_to": "human claims assessor",
                   "reason": "Date of service 2026-05-20 is outside POL-6001, which runs "
                             "2026-06-01 to 2027-05-31."}},
    ],
    "CLM-8925": [
        _claim_open("CLM-8925"),
        {"thought": "The annual-limit check is an early-exit policy check.",
         "calls": [("lookup_policy", {"member_id": "M-2214"})]},
        {"thought": "The total exceeds remaining cover; individual lines need not be priced.",
         "final": {"decision": "escalate", "trigger": "annual_limit_exceeded",
                   "escalate_to": "human claims assessor",
                   "reason": "Claim total 11400 exceeds 9200 remaining on POL-3310; lines were not "
                             "individually priced."}},
    ],
    "CLM-8933": [
        _claim_open("CLM-8933"),
        {"thought": "Check the claims history on all four episode facts before deciding.",
         "calls": [("check_duplicate_claim", {"member_id": "M-2214", "hospital_id": "H-114",
                                               "date_of_service": "2026-08-20",
                                               "lines": [{"code": "47120", "amount": 1500}]})]},
        {"thought": "A prior decision exists for the same episode.",
         "final": {"decision": "escalate", "trigger": "duplicate_claim",
                   "escalate_to": "human claims assessor",
                   "reason": "Matches prior CLM-8710 on member, hospital, date of service, and lines."}},
    ],
    "CLM-8941": [
        _claim_open("CLM-8941"),
        {"thought": "Member-provided narrative contains an instruction aimed at the system.",
         "final": {"decision": "escalate", "trigger": "instruction_in_member_narrative",
                   "escalate_to": "human claims assessor",
                   "reason": "Member narrative contains an instruction aimed at the system; it was not followed."}},
    ],
    "CLM-8952": [
        _claim_open("CLM-8952"),
        {"thought": "Text imitating tool output is untrusted member narrative, not evidence.",
         "final": {"decision": "escalate", "trigger": "instruction_in_member_narrative",
                   "escalate_to": "human claims assessor",
                   "reason": "Member-supplied text imitates tool output and is treated as an instruction, not evidence."}},
    ],
    "CLM-8960": [
        _claim_open("CLM-8960"),
        _claim_checks("M-5502", "POL-6001", "H-114", "2026-09-15",
                      [{"code": "99213", "amount": 180}, {"code": "80053", "amount": 90},
                       {"code": "70553", "amount": 620}, {"code": "45378", "amount": 1100}]),
        *_approve("CLM-8960", "All 4 lines covered; approved_total 1990. CLM-8726 is not a duplicate "
                                  "because its lines differ.", 4, 1990),
    ],
    "CLM-8971": [
        _claim_open("CLM-8971"),
        _claim_checks("M-3390", "POL-4102", "H-207", "2026-09-16",
                      [{"code": "99213", "amount": 170}]),
        *_approve("CLM-8971", "99213 covered; approved_total 170 is within the 600 remaining on POL-4102.", 1, 170),
    ],
})


class ScriptedBackend:
    """Replays SCRIPTS[case_id]. Deterministic, free, offline."""

    name = "scripted"

    def __init__(self, case_id):
        if case_id not in SCRIPTS:
            raise SystemExit(
                "\n  No script for case %r.\n"
                "  The scripted backend replays moves you wrote down; it does\n"
                "  not invent them. Two ways forward:\n"
                "    1. add %r to SCRIPTS in backends.py, or\n"
                "    2. set BACKEND = \"live\" in config.py (this costs money).\n"
                "  Scripted cases so far: %s\n"
                % (case_id, case_id, ", ".join(sorted(SCRIPTS))))
        self.steps = SCRIPTS[case_id]
        self.i = 0

    def next_move(self, transcript):
        """`transcript` is ignored on purpose - a script does not react.
        That is what makes it reproducible."""
        if self.i >= len(self.steps):
            return {"final": {"decision": "escalate",
                              "reason": "script ended without a conclusion"},
                    "thought": "script exhausted"}
        step = self.steps[self.i]
        self.i += 1
        return step

    # Token counts on the scripted backend are ESTIMATES, so your cost
    # arithmetic has something to chew on. They are not measurements and
    # you must not report them as such - D6 wants MEASURED counts, which
    # means the live battery.
    @staticmethod
    def token_estimate(transcript):
        return 1800 + 600 * len(transcript), 120


# =====================================================================
# LIVE
# =====================================================================
class LiveBackend:
    """Real model through OpenRouter. Costs money. D5(b) only."""

    name = "live"

    def __init__(self, case_id, tool_descriptors, system_prompt):
        self.case_id = case_id
        self.tools = tool_descriptors
        self.system_prompt = system_prompt

    def next_move(self, transcript):
        messages = [{"role": "system", "content": self.system_prompt}]
        for entry in transcript:
            messages.append({"role": entry["role"], "content": entry["content"]})
        raw = _live_call(messages)
        return _parse_move(raw)

    @staticmethod
    def token_estimate(transcript):
        # Replace with the usage numbers the API returns. Estimating here
        # and calling it measured is the mistake D6 punishes.
        return 0, 0


def _parse_move(text):
    """The model must answer in JSON. Anything else is a run you cannot
    grade, so say so loudly rather than guessing."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"final": {"decision": "escalate",
                          "reason": "model did not return parseable JSON"},
                "thought": "unparseable: %s" % text[:200]}


def _live_call(messages):
    """>>> THE ONLY FUNCTION IN THIS REPOSITORY THAT KNOWS A VENDOR <<<

    Everything else speaks in terms of moves and transcripts. Swapping
    vendor means rewriting this one function, and changing MODEL and
    BASE_URL in config.py. Nothing else.
    """
    if not config.API_KEY:
        raise SystemExit(
            "\n  BACKEND is 'live' but OPENROUTER_API_KEY is not set.\n"
            "    export OPENROUTER_API_KEY='sk-or-...'\n"
            "  Or set BACKEND = 'scripted' in config.py, which is free.\n")
    body = json.dumps({
        "model": config.MODEL,
        "messages": messages,
        "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        config.BASE_URL.rstrip("/") + "/chat/completions",
        data=body,
        headers={"Authorization": "Bearer " + config.API_KEY,
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    return payload["choices"][0]["message"]["content"]


def make_backend(case_id, tool_descriptors=None, system_prompt=""):
    if config.BACKEND == "scripted":
        return ScriptedBackend(case_id)
    if config.BACKEND == "live":
        return LiveBackend(case_id, tool_descriptors or [], system_prompt)
    raise SystemExit("BACKEND must be 'scripted' or 'live', not %r"
                     % config.BACKEND)
