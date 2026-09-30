import json,tempfile,unittest
from pathlib import Path
from check import scan_source,load_packs,derive,MAX_BYTES
class Tests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def put(self,n,t):p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t);return p
 def test_secret_redacted(self):
  s='sk_live_'+'SYNTHETIC'*4;self.put('.env','KEY='+s);f,_=scan_source(self.root);self.assertEqual(f[0]['rule_id'],'SEC-SECRETS');self.assertNotIn(s,json.dumps(f))
 def test_cors_candidate(self):self.put('app.py',"allow_origins=['*']");f,_=scan_source(self.root);self.assertIn('SEC-CORS',{x['rule_id'] for x in f})
 def test_debug_candidate(self):self.put('settings.py','DEBUG = True');f,_=scan_source(self.root);self.assertIn('SEC-DEBUG',{x['rule_id'] for x in f})
 def test_noindex_candidate(self):self.put('index.html','<meta name="robots" content="noindex">');f,_=scan_source(self.root);self.assertIn('SEO-INDEX',{x['rule_id'] for x in f})
 def test_vendor_skipped(self):self.put('node_modules/x.js','DEBUG = True');f,_=scan_source(self.root);self.assertEqual(f,[])
 def test_oversize_omitted(self):self.put('big.js','x'*(MAX_BYTES+1));_,s=scan_source(self.root);self.assertEqual(len(s['omissions']),1)
 def test_packs_load(self):self.assertEqual(set(load_packs(Path(__file__).parents[1])),{'security','seo','performance','conversion-copy'})
 def test_pass_needs_all(self):
  r={'id':'X','evidence':['source','runtime']};self.assertEqual(derive(r,{'X':[{'type':'source','result':'PASS'}]}),'UNKNOWN');self.assertEqual(derive(r,{'X':[{'type':'source','result':'PASS'},{'type':'runtime','result':'PASS'}]}),'PASS')
 def test_fail_wins(self):self.assertEqual(derive({'id':'X','evidence':['runtime']},{'X':[{'type':'runtime','result':'FAIL'}]}),'FAIL')
 def test_copy_claim(self):self.assertEqual(derive({'id':'X','mode':'evidence'},{'X':[{'type':'evidence','result':'CLAIM_NEEDS_EVIDENCE'}]},True),'CLAIM_NEEDS_EVIDENCE')
 def test_style_not_failure(self):self.assertEqual(derive({'id':'X','mode':'style-preference'},{},True),'NOT_APPLICABLE')
if __name__=='__main__':unittest.main()
