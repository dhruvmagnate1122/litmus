import json,tempfile,unittest
from pathlib import Path
from check import scan_source,load_packs,derive,validate_evidence,release_summary,MAX_BYTES

def ev(t,r,kind="tool"):
    return {"type":t,"result":r,"details":"synthetic","observed_at":"2026-09-30T12:00:00Z","environment":"test","producer":{"kind":kind,"name":"test"},"artifact":"fixture"}

class Tests(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
 def tearDown(self): self.tmp.cleanup()
 def put(self,n,t): p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t);return p
 def test_secret_candidate_redacted(self):
  s='sk_live_'+'SYNTHETIC'*4;self.put('.env','KEY='+s);f,_=scan_source(self.root);self.assertEqual(f[0]['rule_id'],'SEC-SECRETS');self.assertEqual(f[0]['status'],'REVIEW');self.assertNotIn(s,json.dumps(f))
 def test_static_candidate_never_fail(self):
  self.put('settings.py','DEBUG = True');f,_=scan_source(self.root);self.assertEqual(f[0]['status'],'REVIEW')
 def test_noindex_candidate(self):
  self.put('index.html','<meta name="robots" content="noindex">');f,_=scan_source(self.root);self.assertIn('SEO-INDEX',{x['rule_id'] for x in f})
 def test_vendor_skipped(self):
  self.put('node_modules/x.js','DEBUG = True');f,_=scan_source(self.root);self.assertEqual(f,[])
 def test_oversize_omitted(self):
  self.put('big.js','x'*(MAX_BYTES+1));_,s=scan_source(self.root);self.assertEqual(len(s['omissions']),1)
 def test_packs_have_severity_nextstep(self):
  packs=load_packs(Path(__file__).parents[1]);self.assertEqual(set(packs),{'security','seo','performance','conversion-copy'})
  for p in packs.values():
   for r in p['checks']:
    self.assertIn(r['severity'],{'critical','high','medium','low','info'});self.assertTrue(r.get('next_step'))
 def test_evidence_requires_provenance(self):
  with self.assertRaises(ValueError): validate_evidence({'X':[{'type':'runtime','result':'PASS'}]})
 def test_evidence_accepts_reference_alias(self):
  item=ev('runtime','PASS'); item['reference']=item.pop('artifact')
  self.assertEqual(validate_evidence({'X':[item]})['X'][0]['reference'],'fixture')
 def test_evidence_requires_artifact_or_reference(self):
  item=ev('runtime','PASS'); item.pop('artifact')
  with self.assertRaises(ValueError): validate_evidence({'X':[item]})
 def test_pass_needs_all_types(self):
  rule={'id':'X','evidence':['source','runtime']}
  self.assertEqual(derive(rule,[ev('source','PASS')])[0],'UNKNOWN')
  self.assertEqual(derive(rule,[ev('source','PASS'),ev('runtime','PASS')])[0],'PASS')
 def test_fail_wins(self):
  rule={'id':'X','evidence':['runtime']}
  self.assertEqual(derive(rule,[ev('runtime','PASS'),ev('runtime','FAIL')])[0],'FAIL')
 def test_conflicting_na_is_review(self):
  rule={'id':'X','evidence':['runtime']}
  self.assertEqual(derive(rule,[ev('runtime','NOT_APPLICABLE'),ev('runtime','PASS')])[0],'REVIEW')
 def test_static_resolved_only_complete(self):
  rule={'id':'X','evidence':['config','runtime']}
  self.assertEqual(derive(rule,[ev('config','PASS')],True)[0],'REVIEW')
  st,msg=derive(rule,[ev('config','PASS'),ev('runtime','PASS')],True);self.assertEqual(st,'PASS');self.assertIn('resolved',msg)
 def test_release_blocker_by_severity(self):
  checks=[{'rule_id':'A','status':'FAIL','severity':'critical'},{'rule_id':'B','status':'FAIL','severity':'low'}]
  r=release_summary(checks);self.assertEqual(r['decision'],'BLOCKED');self.assertEqual(r['release_blockers'],['A']);self.assertIn('B',r['lower_severity_open_items'])
 def test_unknown_requires_review_decision(self):
  r=release_summary([{'rule_id':'A','status':'UNKNOWN','severity':'medium'}]);self.assertEqual(r['decision'],'NEEDS_REVIEW')
 def test_perf_measurement_first(self):
  p=load_packs(Path(__file__).parents[1])['performance'];ids={x['id'] for x in p['checks']}
  self.assertIn('PERF-CWV',ids);self.assertIn('PERF-REGRESSION',ids);self.assertNotIn('PERF-LOAD-BALANCER',ids)
 def test_copy_style_suggestion_only(self):
  p=load_packs(Path(__file__).parents[1])['conversion-copy'];r=next(x for x in p['checks'] if x['id']=='COPY-EMDASH')
  self.assertEqual(r['automation'],'suggestion-only')
if __name__=='__main__': unittest.main()
