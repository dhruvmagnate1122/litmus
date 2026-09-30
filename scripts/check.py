#!/usr/bin/env python3
import argparse, datetime as dt, json, os, re, sys
from pathlib import Path

VERSION="0.1.0"
SEVERITIES={"critical":5,"high":4,"medium":3,"low":2,"info":1}
SKIP={".git","node_modules",".next","dist","build",".venv","venv","vendor","coverage","__pycache__"}
TEXT_EXT={".js",".jsx",".ts",".tsx",".mjs",".cjs",".py",".sql",".html",".htm",".css",".json",".yml",".yaml",".toml",".md"}
MAX_BYTES=1024*1024
PATTERNS=[
 {"id":"SEC-SECRETS","severity":"critical","title":"Possible embedded private credential","confidence":"medium","pattern":r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk_live_[A-Za-z0-9]{16,}|\bAKIA[A-Z0-9]{16}\b"},
 {"id":"SEC-CORS","severity":"medium","title":"Permissive CORS candidate","confidence":"low","pattern":r"Access-Control-Allow-Origin\s*[:=]\s*['\"]?\*|allow_origins\s*=\s*\[\s*['\"]\*['\"]\s*\]"},
 {"id":"SEC-DEBUG","severity":"high","title":"Production debug candidate","confidence":"low","pattern":r"\bDEBUG\s*=\s*(?:True|true|1)\b|debug\s*:\s*true"},
 {"id":"SEC-INJECTION","severity":"critical","title":"Possible interpolated SQL candidate","confidence":"low","pattern":r"(?:SELECT|INSERT|UPDATE|DELETE).{0,120}(?:\$\{|\+\s*[A-Za-z_]|f['\"]|format\()"},
 {"id":"SEO-INDEX","severity":"high","title":"noindex directive candidate","confidence":"low","pattern":r"<meta[^>]+name=['\"]robots['\"][^>]+content=['\"][^'\"]*noindex|X-Robots-Tag.{0,30}noindex"}
]

def read_obj(path,label):
    obj=json.loads(Path(path).read_text())
    if not isinstance(obj,dict): raise ValueError(label+" must be a JSON object")
    return obj

def load_packs(base):
    out={}
    for p in sorted((base/"packs").glob("*.json")):
        obj=json.loads(p.read_text())
        out[obj["pack"]]=obj
    return out

def scan_source(root):
    findings=[]; omissions=[]; count=0
    for base,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=[d for d in dirs if d not in SKIP and not (Path(base)/d).is_symlink()]
        for name in files:
            p=Path(base)/name
            rel=p.relative_to(root).as_posix()
            if p.is_symlink(): omissions.append({"path":rel,"reason":"symlink"}); continue
            if p.suffix.lower() not in TEXT_EXT and not name.startswith(".env"): continue
            try:
                if p.stat().st_size>MAX_BYTES: omissions.append({"path":rel,"reason":"over-size-limit"}); continue
                raw=p.read_bytes()
                if b"\0" in raw: continue
                txt=raw.decode("utf-8")
            except Exception:
                omissions.append({"path":rel,"reason":"unreadable"}); continue
            count+=1
            for rule in PATTERNS:
                ms=list(re.finditer(rule["pattern"],txt,re.I|re.S))
                if ms:
                    findings.append({
                        "rule_id":rule["id"],"status":"REVIEW","severity":rule["severity"],
                        "confidence":rule["confidence"],"verification_level":"static-candidate",
                        "title":rule["title"],"path":rel,
                        "lines":sorted({txt.count("\n",0,m.start())+1 for m in ms})[:20]
                    })
    return findings,{"files_scanned":count,"omissions":omissions}

def validate_evidence(evidence):
    if not isinstance(evidence,dict): raise ValueError("Evidence must be an object")
    allowed_results={"PASS","FAIL","REVIEW","NOT_APPLICABLE","SUGGESTION","CLAIM_NEEDS_EVIDENCE"}
    allowed_kinds={"tool","external","manual"}
    for rid,items in evidence.items():
        if not isinstance(items,list): raise ValueError("Evidence records must be arrays")
        for item in items:
            if not isinstance(item,dict): raise ValueError("Evidence record must be an object")
            for k in ("type","result","details","observed_at","environment","producer"):
                if k not in item: raise ValueError("Evidence record missing "+k)
            artifact=item.get("artifact")
            reference=item.get("reference")
            if not ((isinstance(artifact,str) and artifact.strip()) or (isinstance(reference,str) and reference.strip())):
                raise ValueError("Evidence record requires artifact or reference")
            if str(item["result"]).upper() not in allowed_results: raise ValueError("Invalid evidence result")
            prod=item["producer"]
            if not isinstance(prod,dict) or prod.get("kind") not in allowed_kinds or not prod.get("name"):
                raise ValueError("Invalid producer")
            dt.datetime.fromisoformat(str(item["observed_at"]).replace("Z","+00:00"))
    return evidence

def verification_level(items):
    kinds={x.get("producer",{}).get("kind") for x in items if isinstance(x,dict)}
    if not items: return "none"
    if kinds=={"manual"}: return "manual-attested"
    if kinds and kinds <= {"tool","external"}: return "tool-external-attested"
    return "mixed-attested"

def derive(rule,items,has_static=False):
    results=[str(x.get("result","")).upper() for x in items]
    if "FAIL" in results:
        return "FAIL","failure evidence present"
    if "CLAIM_NEEDS_EVIDENCE" in results:
        return "CLAIM_NEEDS_EVIDENCE","material claim lacks supporting evidence"
    if "REVIEW" in results:
        return "REVIEW","review evidence unresolved"
    if "NOT_APPLICABLE" in results:
        if any(r in {"PASS","SUGGESTION"} for r in results):
            return "REVIEW","conflicting applicability evidence"
        return "NOT_APPLICABLE","evidence marks rule inapplicable"
    if "SUGGESTION" in results:
        return "SUGGESTION","suggestion-only evidence"
    required=set(rule.get("evidence",[]))
    passed={x.get("type") for x in items if str(x.get("result","")).upper()=="PASS"}
    if required and required.issubset(passed):
        return "PASS","required evidence types passed"+(" and static candidate resolved" if has_static else "")
    if rule.get("automation") in {"experimental-optional","suggestion-only"} and not required:
        return ("SUGGESTION" if rule.get("automation")=="suggestion-only" else "NOT_APPLICABLE"),"optional/non-gating rule"
    if has_static:
        return "REVIEW","static candidate lacks complete resolving evidence"
    return "UNKNOWN","required evidence incomplete"

def confidence_for(status,items,has_static):
    if status=="FAIL":
        return "high" if any(x.get("producer",{}).get("kind") in {"tool","external"} for x in items) else "medium"
    if status=="PASS":
        return "high" if items and all(x.get("producer",{}).get("kind") in {"tool","external"} for x in items) else "medium"
    if has_static: return "low"
    return "unknown"

def release_summary(checks):
    blockers=[]; required_review=[]; unknowns=[]; deferred=[]; suggestions=[]
    for c in checks:
        sev=c.get("severity","info")
        st=c["status"]
        if st=="FAIL" and SEVERITIES.get(sev,1)>=SEVERITIES["high"]: blockers.append(c["rule_id"])
        elif st=="REVIEW" and SEVERITIES.get(sev,1)>=SEVERITIES["high"]: required_review.append(c["rule_id"])
        elif st=="UNKNOWN": unknowns.append(c["rule_id"])
        elif st in {"FAIL","REVIEW"}: deferred.append(c["rule_id"])
        elif st in {"SUGGESTION","CLAIM_NEEDS_EVIDENCE"}: suggestions.append(c["rule_id"])
    decision="BLOCKED" if blockers else ("NEEDS_REVIEW" if required_review or unknowns else "NO_BLOCKERS_FOUND")
    return {"decision":decision,"release_blockers":blockers,"required_review":required_review,"unknowns":unknowns,"lower_severity_open_items":deferred,"suggestions":suggestions}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root"); ap.add_argument("--profile"); ap.add_argument("--evidence"); ap.add_argument("--fail-on-review",action="store_true")
    a=ap.parse_args()
    root=Path(a.root).resolve()
    if not root.is_dir():
        print(json.dumps({"error":"Invalid root"}),file=sys.stderr); return 2
    try:
        profile=read_obj(a.profile,"Profile") if a.profile else None
        evidence=validate_evidence(read_obj(a.evidence,"Evidence")) if a.evidence else {}
    except Exception as exc:
        print(json.dumps({"error":"Invalid profile/evidence","detail":str(exc)}),file=sys.stderr); return 2
    source,scope=scan_source(root)
    source_by={}
    for f in source: source_by.setdefault(f["rule_id"],[]).append(f)
    packs=load_packs(Path(__file__).parents[1]); guided=[]
    for pack_name,pack in packs.items():
        for rule in pack["checks"]:
            items=evidence.get(rule["id"],[])
            st,resolution=derive(rule,items,rule["id"] in source_by)
            guided.append({
                "pack":pack_name,"pack_maturity":pack.get("maturity"),"rule_id":rule["id"],"title":rule["title"],
                "status":st,"severity":rule.get("severity","info"),"confidence":confidence_for(st,items,rule["id"] in source_by),
                "verification_level":verification_level(items),
                "automation":rule.get("automation"),"evidence_required":rule.get("evidence",[]),"evidence_count":len(items),
                "static_candidates":source_by.get(rule["id"],[]),"resolution":resolution,"next_step":rule.get("next_step")
            })
    result={
        "version":VERSION,"scope":scope,"profile_provided":profile is not None,"evidence_provided":bool(evidence),
        "source_findings":source,"checks":guided,"release":release_summary(guided),
        "limitations":[
            "Static matches are candidate signals only and never automatic FAIL.",
            "Evidence JSON is structurally validated but is not cryptographically authenticated; provenance is surfaced for review.",
            "The dependency-free core does not replace browser automation, SCA/CVE feeds, database profiling, Search Console/RUM or human review.",
            "NO_BLOCKERS_FOUND is not a security, SEO, performance or conversion guarantee."
        ]
    }
    print(json.dumps(result,indent=2))
    if a.fail_on_review and result["release"]["decision"] in {"BLOCKED","NEEDS_REVIEW"}: return 1
    return 0
if __name__=="__main__": sys.exit(main())
