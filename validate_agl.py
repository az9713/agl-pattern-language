"""AGL v0.4 reference static and trace auditor.

This is NOT an orchestration runtime or proof of real-world safety.  It validates
schema contracts and audits an explicitly provided event log.  Preventing
external duplicate side effects requires transactional storage / provider keys.
Requires jsonschema (`pip install jsonschema`).
"""
import argparse, json, sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parent

REQUIRED_GUARDS={'authorization','lease','budget','dedupe'}

def validate_static(doc):
    issues=[]
    schema=json.loads((ROOT/'schema.json').read_text(encoding='utf-8'))
    for err in sorted(Draft202012Validator(schema).iter_errors(doc),key=lambda e:list(map(str,e.path))):
        path='$'+''.join(f'[{repr(x)}]' for x in err.path)
        issues.append(f'SCHEMA {path}: {err.message}')
    if issues:return issues
    c=doc.get('contract'); g=doc.get('goal'); l=doc.get('loop'); v=doc['verifier']; gov=doc['governance']; a=doc.get('ambition')
    if c:
        if not c['approved'] or not c['frozen']:
            issues.append('CONTRACT: execution contract must be approved and frozen')
        if c['approved_by'] != gov['approved_by']:
            issues.append('GOVERNANCE: contract approver differs from policy approver')
        if not set(c['authorized_actions']).issubset(set(gov['permission_scope'])):
            issues.append('GOVERNANCE: contract authorized actions exceed policy')
    if a:
        if not a['R']['verbify']['output'].strip():
            issues.append('RANGE: verbify did not yield a functional objective')
        if a['R']['discipline_discovery']['input_ref']!='#/ambition/R/verbify/output':
            issues.append('RANGE: discipline discovery must consume verbify output')
        if not a['S']['quality_floor'] or not a['S']['same_outcome_constraint']:
            issues.append('SPEED: quality and outcome preservation must be explicit')
    if v['operator']!='V' or len(set(v['outcomes']))!=3:
        issues.append('VERIFIER: must include exactly PASS, FAIL, INCONCLUSIVE')
    total=0
    if g:
        if not c or g['contract_ref']!=c['id']:
            issues.append('GOAL: contract reference does not resolve')
        if g['evaluator_ref']!=v['id']:
            issues.append('GOAL: evaluator reference does not resolve')
        if g['executor_id']==v['runner_id']:
            issues.append('INDEPENDENCE: evaluator and executor identity must differ')
        if not set(g['execution_policy']['permitted_methods']).issubset(set(c['authorized_actions'])):
            issues.append('GOAL: permitted methods exceed contract actions')
        total+=g['budget']['max_money']
    if l:
        if not c or l['contract_ref']!=c['id'] or l['safety']['scope']['approved_contract_ref']!=c['id']:
            issues.append('LOOP: contract references do not resolve')
        if not set(l['response']['authorized_actions']).issubset(set(c['authorized_actions'])):
            issues.append('LOOP: response exceeds contract authorization')
        if l['timing']['mode']=='fixed' and l['timing'].get('interval_seconds',0)<60:
            issues.append('TIMING: fixed schedule must have interval_seconds >= 60')
        if l['timing']['mode']!='fixed' and 'interval_seconds' in l['timing']:
            issues.append('TIMING: fixed interval cannot be specified for non-fixed scheduling')
        if l['safety']['boundedness']['per_run_money_limit']>l['safety']['boundedness']['cumulative_money_limit']:
            issues.append('BOUNDEDNESS: per-run cap exceeds cumulative cap')
        if l['response']['no_change']!='NO_OP':
            issues.append('LOOP: no-change path must have no action')
        if not REQUIRED_GUARDS.issubset(set(l['enforcement']['runtime_guards'])):
            issues.append('ENFORCEMENT: missing runtime guard declaration(s)')
        total+=l['safety']['boundedness']['cumulative_money_limit']
    if total>gov['max_money_total']:
        issues.append(f'BUDGET: aggregate reserved maxima {total:g} exceed governance cap {gov["max_money_total"]:g}')
    return issues

def validate_trace(doc,trace):
    """Audit logged facts only.  An incomplete or dishonest trace proves nothing."""
    problems=[]
    l=doc.get('loop')
    if not l:
        return ['TRACE: only documents with loop operator support this reference audit']
    contract=doc['contract']; allowed=set(l['response']['authorized_actions'])
    effects=set(); seen_events=set(); checkpoint=-1; spent=0.0; per_run={}
    for i,record in enumerate(trace):
        tag=f'TRACE[{i}]'
        if not isinstance(record,dict):problems.append(f'{tag}: expected object');continue
        kind=record.get('kind')
        if kind=='checkpoint':
            v=record.get('version')
            if type(v)!=int or v<=checkpoint:
                problems.append(f'{tag}: nonmonotonic or invalid checkpoint')
            else:checkpoint=v
        elif kind=='observation':
            event_id=record.get('event_id')
            if not event_id:problems.append(f'{tag}: missing event_id')
            # duplicated observations are admissible; duplicate actions are not
            else:seen_events.add(event_id)
        elif kind=='action':
            if record.get('contract_id')!=contract['id']:
                problems.append(f'{tag}: incorrect contract')
            if record.get('name') not in allowed:
                problems.append(f'{tag}: unauthorized action name')
            if record.get('authorization_checked') is not True:
                problems.append(f'{tag}: no recorded authorization preflight')
            if not record.get('lease_id'):
                problems.append(f'{tag}: no concurrency lease reference')
            ev=record.get('event_id');eff=record.get('effect_id')
            if not ev or ev not in seen_events:
                problems.append(f'{tag}: action lacks prior observed event')
            if not eff:
                problems.append(f'{tag}: consequential action requires effect_id')
            elif eff in effects:
                problems.append(f'{tag}: repeated effect_id {eff}')
            else:effects.add(eff)
            cost=record.get('money_cost',0)
            if isinstance(cost,bool) or not isinstance(cost,(int,float)) or cost<0:
                problems.append(f'{tag}: invalid money_cost');continue
            spent+=cost
            run_id=record.get('run_id','')
            if not run_id:problems.append(f'{tag}: missing run_id')
            per_run[run_id]=per_run.get(run_id,0)+cost
        else:problems.append(f'{tag}: unsupported event kind')
    cap=l['safety']['boundedness']
    if spent>cap['cumulative_money_limit']:
        problems.append('TRACE: cumulative observed spend exceeds cap')
    for run,total in per_run.items():
        if total>cap['per_run_money_limit']:
            problems.append(f'TRACE: run {run} observed spend exceeds per-run cap')
    # No claim that log authentic, exhaustive or writes atomic.
    return problems

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('spec',type=Path)
    p.add_argument('--trace',type=Path)
    a=p.parse_args()
    doc=json.loads(a.spec.read_text(encoding='utf-8'))
    errors=validate_static(doc)
    if a.trace and not errors:
        errors+=validate_trace(doc,json.loads(a.trace.read_text(encoding='utf-8')))
    if errors:
        for e in errors:print('FAIL:',e)
        return 1
    print('PASS: reference schema and semantic checks'+(' plus supplied-trace audit' if a.trace else '')+'.')
    print('LIMIT: PASS does not prove execution safety, evaluator soundness, or evidence authenticity.')
    return 0
if __name__=='__main__':sys.exit(main())