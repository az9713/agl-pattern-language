"""AGL v0.4, Lab 2: learning-oriented validator experiments.

Run in the extracted kit: python lab2_explained.py --guided
Or: python lab2_explained.py --case 4
No production tool calls. Every mutation is performed on an in-memory copy.
"""
import argparse
import copy
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from validate_agl import ROOT, validate_static, validate_trace

BASE = json.loads((ROOT / "abstract_valid_spec.json").read_text(encoding="utf-8"))

@dataclass(frozen=True)
class Case:
    number: int
    name: str
    section: str
    invariant: str
    mutation: str
    expected: str
    check: str
    lesson: str
    limitation: str

CASES = [
    Case(1, "Valid reference contract", "3, 7, 8", "The complete approved P4 contract is well-formed.",
         "No mutation: keep the reference configuration unchanged.", "PASS", "", "All implemented schema and cross-field checks accept the reference configuration.", "This does not prove a live agent will behave correctly."),
    Case(2, "Noun-to-verb transformation", "4.4, 8", "Range requires an explicit VERBIFY transformation.",
         "Delete ambition.R.verbify.", "FAIL", "verbify", "The grammar enforces the presence of a transformation from artifact to function.", "Presence of a field does not establish that the transformation is insightful."),
    Case(3, "Epistemic discovery mechanism", "4.3, 8, 10", "Depth requires a declared surprise detector.",
         "Delete ambition.D.discovery.surprise_detector.", "FAIL", "surprise_detector", "Knowledge discovery has an explicit structural prerequisite.", "The checker cannot determine whether the detector discovers anything."),
    Case(4, "Evaluator identity separation", "5.1, 8, 9", "Goal executor and verifier runner must not have the same ID.",
         "Set verifier.runner_id equal to goal.executor_id.", "FAIL", "INDEPENDENCE", "A simple structural independence condition is checked.", "Different IDs do not establish true evaluator independence."),
    Case(5, "No authority escalation", "3, 6.2, 8", "Loop actions must be a subset of approved contract actions.",
         "Add delete-production to loop.response.authorized_actions.", "FAIL", "authorization", "The checker rejects declared Loop scope escalation.", "A specification check does not enforce host/tool permissions at runtime."),
    Case(6, "Cumulative budget reservation", "3, 6.2, 8", "Declared Goal and Loop budgets must fit governance allocation.",
         "Reduce governance.max_money_total from 30 to 15.", "FAIL", "BUDGET", "The checker catches aggregate budget oversubscription.", "It cannot enforce real spending without an action-time budget controller."),
    Case(7, "Required guard declaration", "6.2, 8", "A Loop must declare authorization, lease, budget, and dedupe guards.",
         "Remove dedupe from loop.enforcement.runtime_guards.", "FAIL", "ENFORCEMENT", "The schema-plus-validator require the dedupe guard to be declared.", "Declaring dedupe does not implement replay protection."),
    Case(8, "Scheduling lower bound", "6.3, 8", "A fixed Loop interval in this reference checker must be >= 60 seconds.",
         "Set loop.timing.interval_seconds from 3600 to 12.", "FAIL", "TIMING", "A too-frequent fixed schedule is rejected by the reference policy.", "This is a local checker rule, not a universal scheduling law."),
    Case(9, "Well-formed recorded trace", "6.1, 8", "Observed action and checkpoint evidence must be internally consistent.",
         "Provide observation -> authorized-by-declaration action -> checkpoint version 1.", "PASS", "", "The trace has no violations detectable by this retrospective auditor.", "Recorded permission and lease flags may be untruthful; effects may be unlogged."),
    Case(10, "Duplicate recorded side-effect", "6.2, 8", "A consequential effect ID must not repeat in the supplied trace.",
         "Append the same action record twice with effect_id effect-1.", "FAIL", "repeated effect_id", "The auditor detects a repeated effect identifier.", "This does not prevent an API from performing the same effect twice."),
    Case(11, "Monotonic checkpoint state", "6.1, 6.2, 8", "Recorded checkpoint version numbers must strictly increase.",
         "Provide checkpoint version 3 followed by version 2.", "FAIL", "nonmonotonic", "The auditor detects a backward state-version transition in the trace.", "This does not demonstrate atomic commits or durable storage."),
]


def inputs(case):
    doc = copy.deepcopy(BASE)
    trace = None
    n = case.number
    if n == 2: del doc['ambition']['R']['verbify']
    elif n == 3: del doc['ambition']['D']['discovery']['surprise_detector']
    elif n == 4: doc['verifier']['runner_id'] = doc['goal']['executor_id']
    elif n == 5: doc['loop']['response']['authorized_actions'].append('delete-production')
    elif n == 6: doc['governance']['max_money_total'] = 15
    elif n == 7: doc['loop']['enforcement']['runtime_guards'].remove('dedupe')
    elif n == 8: doc['loop']['timing']['interval_seconds'] = 12
    elif n >= 9:
        action = {
            'kind':'action', 'event_id':'event-1','effect_id':'effect-1',
            'name':'propose','authorization_checked':True,'lease_id':'lease-1',
            'contract_id':'contract-alpha','run_id':'run-1','money_cost':0.2
        }
        if n == 9: trace=[{'kind':'observation','event_id':'event-1'}, action, {'kind':'checkpoint','version':1}]
        elif n == 10: trace=[{'kind':'observation','event_id':'event-1'},action,copy.deepcopy(action)]
        elif n == 11: trace=[{'kind':'checkpoint','version':3},{'kind':'checkpoint','version':2}]
    return doc, trace


def execute(case):
    doc, trace = inputs(case)
    problems = validate_static(doc)
    if trace is not None and not problems: problems += validate_trace(doc, trace)
    expected_ok = case.expected == 'PASS'
    correctly_classified = (not problems if expected_ok else any(case.check.lower() in p.lower() for p in problems))
    return problems, correctly_classified


def show(case, detailed=False, guided=False):
    print(f'\nCASE {case.number:02d} / 11 | {case.name} | SPEC sections {case.section}')
    print('RULE:   ' + case.invariant)
    print('CHANGE: ' + case.mutation)
    if guided:
        try:
            answer = input('PREDICT checker verdict [PASS/FAIL]: ').strip().upper()
        except EOFError:
            answer = ''
        if answer not in ('PASS','FAIL'):
            print('Prediction skipped.')
        else:
            print('Your prediction: ' + ('CORRECT' if answer == case.expected else 'NOT QUITE') + f'; expected {case.expected}.')
    problems, correct = execute(case)
    print('EXPECT: ' + case.expected + (f' (must mention {case.check})' if case.check else ''))
    print('ACTUAL: ' + ('FAIL' if problems else 'PASS'))
    if problems:
        print('DIAGNOSTIC: ' + problems[0])
        if detailed and len(problems)>1:
            for p in problems[1:]: print('            ' + p)
    print('TEST:   ' + ('PASS - expected behavior confirmed' if correct else 'FAIL - expected behavior NOT confirmed'))
    print('LEARN:  ' + case.lesson)
    if detailed or guided: print('LIMIT:  ' + case.limitation)
    return correct


def main():
    parser=argparse.ArgumentParser(description='AGL v0.4 Lab 2 explained - learning companion for unittest')
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--case', type=int, choices=range(1,12), metavar='1-11', help='explain one case with limitations')
    mode.add_argument('--guided', action='store_true', help='interactive predict-observe-explain exercise for all 11 cases')
    mode.add_argument('--list', action='store_true', help='list all 11 cases')
    args=parser.parse_args()
    if args.list:
        for c in CASES: print(f'{c.number:2}. {c.name} | spec ss. {c.section} | expect {c.expected}')
        return 0
    selected=[CASES[args.case-1]] if args.case else CASES
    print('AGL v0.4 / LAB 2 - EXPERIMENT, DIAGNOSTIC, INTERPRETATION')
    print('Each mutation occurs in memory; your files stay unchanged.')
    if args.guided: print('Predict each outcome before the validator runs. You may press Enter to skip.')
    correct=sum(show(c, detailed=bool(args.case), guided=args.guided) for c in selected)
    print(f'\nSUMMARY: {correct}/{len(selected)} experiments behaved as specified.')
    print('This validates selected checker behaviors, not live agent safety or scientific insight.')
    return 0 if correct==len(selected) else 1

if __name__=='__main__':
    sys.exit(main())