#!/usr/bin/env python3
import argparse,json,os,re,sys
from pathlib import Path
VERSION='0.1.0'
SKIP={'.git','node_modules','.next','dist','build','.venv','venv','vendor','coverage','__pycache__'}
TEXT_EXT={'.js','.jsx','.ts','.tsx','.mjs','.cjs','.py','.sql','.html','.htm','.css','.json','.yml','.yaml','.toml','.md'}
MAX_BYTES=1024*1024
PATTERNS=[
('SEC-SECRETS','high','Possible embedded private credential',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk_live_[A-Za-z0-9]{16,}|\bAKIA[A-Z0-9]{16}\b'),
('SEC-CORS','medium','Permissive CORS candidate',r"Access-Control-Allow-Origin\s*[:=]\s*['\"]?\*|allow_origins\s*=\s*\[\s*['\"]\*['\"]\s*\]"),
('SEC-DEBUG','medium','Production debug candidate',r'\bDEBUG\s*=\s*(?:True|true|1)\b|debug\s*:\s*true'),
('SEC-SQL','high','Possible interpolated/raw SQL candidate',r'(?:SELECT|INSERT|UPDATE|DELETE).{0,120}(?:\$\{|\+\s*[A-Za-z_]|f[\'\"]|format\()'),
('SEO-INDEX','high','noindex directive candidate',r'<meta[^>]+name=[\'\"]robots[\'\"][^>]+content=[\'\"][^\'\"]*noindex|X-Robots-Tag.{0,30}noindex')]
def read_obj(path,label):
 obj=json.loads(Path(path).read_text());
 if not isinstance(obj,dict): raise ValueError(label+' must be a JSON object')
 return obj
def scan_source(root):
 findings=[];omissions=[];count=0
 for base,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=[d for d in dirs if d not in SKIP and not (Path(base)/d).is_symlink()]
  for name in files:
   p=Path(base)/name
   if p.is_symlink(): omissions.append({'path':p.relative_to(root).as_posix(),'reason':'symlink'});continue
   if p.suffix.lower() not in TEXT_EXT and not name.startswith('.env'): continue
   try:
    if p.stat().st_size>MAX_BYTES: omissions.append({'path':p.relative_to(root).as_posix(),'reason':'over-size-limit'});continue
    raw=p.read_bytes()
    if b'\0' in raw: continue
    txt=raw.decode('utf-8')
   except Exception:
    omissions.append({'path':p.relative_to(root).as_posix(),'reason':'unreadable'});continue
   count+=1;rel=p.relative_to(root).as_posix()
   for rid,sev,title,pat in PATTERNS:
    ms=list(re.finditer(pat,txt,re.I|re.S))
    if ms: findings.append({'rule_id':rid,'status':'REVIEW','severity':sev,'title':title,'path':rel,'lines':sorted({txt.count('\n',0,m.start())+1 for m in ms})[:20],'confidence':'source-pattern-only'})
 return findings,{'files_scanned':count,'omissions':omissions}
def load_packs(base):
 out={}
 for p in sorted((base/'packs').glob('*.json')):
  obj=json.loads(p.read_text());out[obj['pack']]=obj
 return out
def derive(rule,evidence,copy_pack=False):
 items=evidence.get(rule['id'],[]) if isinstance(evidence,dict) else []
 results=[str(x.get('result','')).upper() for x in items if isinstance(x,dict)]
 if 'FAIL' in results:return 'FAIL'
 if 'CLAIM_NEEDS_EVIDENCE' in results:return 'CLAIM_NEEDS_EVIDENCE'
 if 'REVIEW' in results:return 'REVIEW'
 if 'NOT_APPLICABLE' in results:return 'NOT_APPLICABLE'
 if 'SUGGESTION' in results and copy_pack:return 'SUGGESTION'
 required=set(rule.get('evidence',[]));passed={x.get('type') for x in items if isinstance(x,dict) and str(x.get('result','')).upper()=='PASS'}
 if required and required.issubset(passed):return 'PASS'
 if rule.get('automation')=='optional' or rule.get('mode')=='style-preference':return 'NOT_APPLICABLE'
 return 'UNKNOWN'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('root');ap.add_argument('--profile');ap.add_argument('--evidence');ap.add_argument('--fail-on-review',action='store_true');a=ap.parse_args()
 root=Path(a.root).resolve()
 if not root.is_dir(): print(json.dumps({'error':'Invalid root'}),file=sys.stderr);return 2
 try:
  profile=read_obj(a.profile,'Profile') if a.profile else None;evidence=read_obj(a.evidence,'Evidence') if a.evidence else {}
 except Exception:
  print(json.dumps({'error':'Invalid profile/evidence'}),file=sys.stderr);return 2
 findings,scope=scan_source(root);packs=load_packs(Path(__file__).parents[1]);guided=[]
 for pack_name,pack in packs.items():
  for rule in pack['checks']:
   guided.append({'pack':pack_name,'rule_id':rule['id'],'title':rule['title'],'status':derive(rule,evidence,pack_name=='conversion-copy'),'evidence_required':rule.get('evidence',[]),'notes':rule.get('notes')})
 result={'version':VERSION,'overall':'INCOMPLETE_REVIEW_REQUIRED','profile_provided':profile is not None,'scope':scope,'source_findings':findings,'guided_checks':guided,'limitations':['Source matches are REVIEW candidates only.','PASS requires supplied evidence for declared types.','The CLI does not autonomously browse, profile production systems, or prove security/rankings/conversion outcomes.']}
 print(json.dumps(result,indent=2));return 1 if a.fail_on_review and (findings or any(x['status']=='FAIL' for x in guided)) else 0
if __name__=='__main__':sys.exit(main())
