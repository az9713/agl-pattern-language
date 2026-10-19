import copy,json,unittest
from pathlib import Path
from validate_agl import validate_static,validate_trace,ROOT

class Tests(unittest.TestCase):
  def setUp(self):
    self.good=json.loads((ROOT/'abstract_valid_spec.json').read_text(encoding='utf-8'))
  def test_valid(self):self.assertEqual(validate_static(self.good),[])
  def test_missing_verbify(self):
    d=copy.deepcopy(self.good);del d['ambition']['R']['verbify']
    self.assertTrue(any('verbify' in m for m in validate_static(d)))
  def test_missing_discovery_mechanism(self):
    d=copy.deepcopy(self.good);del d['ambition']['D']['discovery']['surprise_detector']
    self.assertTrue(any('surprise_detector' in m for m in validate_static(d)))
  def test_evaluator_independence(self):
    d=copy.deepcopy(self.good);d['verifier']['runner_id']=d['goal']['executor_id']
    self.assertTrue(any('INDEPENDENCE' in s for s in validate_static(d)))
  def test_scope_escalation(self):
    d=copy.deepcopy(self.good);d['loop']['response']['authorized_actions'].append('delete-production')
    self.assertTrue(any('authorization' in s for s in validate_static(d)))
  def test_budget_overrun(self):
    d=copy.deepcopy(self.good);d['governance']['max_money_total']=15
    self.assertTrue(any('BUDGET' in s for s in validate_static(d)))
  def test_missing_runtime_guard(self):
    d=copy.deepcopy(self.good);d['loop']['enforcement']['runtime_guards'].remove('dedupe')
    self.assertTrue(any('ENFORCEMENT' in s for s in validate_static(d)))
  def test_fixed_schedule(self):
    d=copy.deepcopy(self.good);d['loop']['timing']['interval_seconds']=12
    self.assertTrue(any('TIMING' in s for s in validate_static(d)))
  def test_good_trace(self):
    events=[{'kind':'observation','event_id':'event-1'},
      {'kind':'action','event_id':'event-1','effect_id':'effect-1','name':'propose','authorization_checked':True,'lease_id':'lease-1','contract_id':'contract-alpha','run_id':'run-1','money_cost':0.2},
      {'kind':'checkpoint','version':1}]
    self.assertEqual(validate_trace(self.good,events),[])
  def test_replay_trace(self):
    actions=[{'kind':'observation','event_id':'event-1'}]
    record={'kind':'action','event_id':'event-1','effect_id':'effect-1','name':'propose','authorization_checked':True,'lease_id':'lease-1','contract_id':'contract-alpha','run_id':'run-1','money_cost':0.2}
    self.assertTrue(any('repeated effect_id' in s for s in validate_trace(self.good,actions+[record,record])))
  def test_nonmonotonic_checkpoint(self):
    self.assertTrue(any('nonmonotonic' in s for s in validate_trace(self.good,[{'kind':'checkpoint','version':3},{'kind':'checkpoint','version':2}])))
if __name__=='__main__':unittest.main(verbosity=2)