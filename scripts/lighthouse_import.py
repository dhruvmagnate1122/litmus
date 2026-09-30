#!/usr/bin/env python3
"""Convert a Lighthouse JSON report into Litmus evidence for the Performance pack.

Lighthouse measures one synthetic page load (lab data). Lab results are recorded
as REVIEW: a human decides what they mean for real users. Field data (CrUX p75)
is only recorded when the input is a PageSpeed Insights response that includes it.
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check import validate_evidence

PACK = Path(__file__).parents[1] / "packs" / "performance.json"
LAB_NOTE = "Lab data from a single synthetic run; not proof of production or field performance."


def cwv_budget():
    pack = json.loads(PACK.read_text())
    rule = next(r for r in pack["checks"] if r["id"] == "PERF-CWV")
    return rule["budget"]


def numeric(audits, audit_id):
    value = audits.get(audit_id, {}).get("numericValue")
    return value if isinstance(value, (int, float)) else None


def lab_record(details, context):
    return {
        "type": "runtime",
        "result": "REVIEW",
        "details": details + " " + LAB_NOTE,
        "observed_at": context["observed_at"],
        "environment": context["environment"],
        "producer": context["producer"],
        "reference": context["reference"],
    }


def lab_cwv(audits, budget, url):
    lcp = numeric(audits, "largest-contentful-paint")
    cls = numeric(audits, "cumulative-layout-shift")
    tbt = numeric(audits, "total-blocking-time")
    if lcp is None and cls is None:
        return None
    parts = ["Lab metrics for " + url + ":"]
    if lcp is not None:
        parts.append("LCP %d ms (good <= %d ms);" % (round(lcp), budget["lcp_ms_good_max"]))
    if cls is not None:
        parts.append("CLS %.3f (good <= %s);" % (cls, budget["cls_good_max"]))
    parts.append("INP cannot be measured in a lab run")
    if tbt is not None:
        parts.append("(TBT %d ms is only a lab proxy for responsiveness)." % round(tbt))
    else:
        parts[-1] += "."
    return " ".join(parts)


def lab_related(audits):
    out = {}
    tbt = numeric(audits, "total-blocking-time")
    if tbt is not None:
        long_tasks = audits.get("long-tasks", {}).get("details", {}).get("items")
        text = "Lab total blocking time %d ms" % round(tbt)
        if isinstance(long_tasks, list):
            text += "; %d long task(s) recorded" % len(long_tasks)
        out["PERF-LONGTASKS"] = text + "."
    bootup = numeric(audits, "bootup-time")
    if bootup is not None:
        out["PERF-JS-BUDGET"] = "Lab JavaScript execution time %d ms." % round(bootup)
    requests = audits.get("network-requests", {}).get("details", {}).get("items")
    if isinstance(requests, list):
        out["PERF-REQUESTS"] = "Lab page load made %d network request(s)." % len(requests)
    third = audits.get("third-party-summary", {}).get("details", {}).get("items")
    if isinstance(third, list):
        out["PERF-THIRD-PARTY"] = "Lab third-party entity count: %d." % len(third)
    return out


def field_cwv(field, budget, context):
    metrics = (field or {}).get("metrics") or {}
    lcp = metrics.get("LARGEST_CONTENTFUL_PAINT_MS", {}).get("percentile")
    inp = metrics.get("INTERACTION_TO_NEXT_PAINT", {}).get("percentile")
    cls_raw = metrics.get("CUMULATIVE_LAYOUT_SHIFT_SCORE", {}).get("percentile")
    if lcp is None and inp is None and cls_raw is None:
        return None
    cls = cls_raw / 100 if cls_raw is not None else None
    parts = ["Field p75 (CrUX):"]
    parts.append("LCP %s ms;" % lcp if lcp is not None else "LCP missing;")
    parts.append("INP %s ms;" % inp if inp is not None else "INP missing;")
    parts.append("CLS %.2f." % cls if cls is not None else "CLS missing.")
    within = (
        lcp is not None and inp is not None and cls is not None
        and lcp <= budget["lcp_ms_good_max"]
        and inp <= budget["inp_ms_good_max"]
        and cls <= budget["cls_good_max"]
    )
    return {
        "type": "runtime",
        "result": "PASS" if within else "REVIEW",
        "details": " ".join(parts) + " Collection period and page/origin scope come from CrUX.",
        "observed_at": context["observed_at"],
        "environment": "field: Chrome UX Report p75, %s" % context["form_factor"],
        "producer": {"kind": "external", "name": "Chrome UX Report via PageSpeed Insights"},
        "reference": context["reference"],
    }


def import_report(report, reference):
    if not isinstance(report, dict):
        raise ValueError("Lighthouse report must be a JSON object")
    field = None
    if "lighthouseResult" in report:
        field = report.get("loadingExperience")
        report = report["lighthouseResult"]
    audits = report.get("audits")
    if not isinstance(audits, dict) or "fetchTime" not in report:
        raise ValueError("Not a Lighthouse report: missing audits or fetchTime")
    settings = report.get("configSettings", {})
    form_factor = settings.get("formFactor", "unknown device")
    throttling = settings.get("throttlingMethod", "unknown")
    url = report.get("finalDisplayedUrl") or report.get("finalUrl") or report.get("requestedUrl", "unknown URL")
    context = {
        "observed_at": report["fetchTime"],
        "environment": "lab: %s, %s throttling" % (form_factor, throttling),
        "producer": {"kind": "external", "name": "Lighthouse " + report.get("lighthouseVersion", "unknown version")},
        "reference": reference,
        "form_factor": form_factor,
    }
    budget = cwv_budget()
    evidence = {}
    cwv = lab_cwv(audits, budget, url)
    if cwv:
        evidence["PERF-CWV"] = [lab_record(cwv, context)]
    for rule_id, text in lab_related(audits).items():
        evidence[rule_id] = [lab_record(text, context)]
    field_record = field_cwv(field, budget, context)
    if field_record:
        evidence.setdefault("PERF-CWV", []).append(field_record)
    return validate_evidence(evidence)


def main():
    ap = argparse.ArgumentParser(description="Convert a Lighthouse JSON report into Litmus evidence.")
    ap.add_argument("report")
    ap.add_argument("--reference", help="Reproducible pointer to the report (defaults to the file name)")
    ap.add_argument("--output", help="Write evidence JSON here instead of stdout")
    a = ap.parse_args()
    try:
        report = json.loads(Path(a.report).read_text(encoding="utf-8"))
        evidence = import_report(report, a.reference or Path(a.report).name)
    except Exception as exc:
        print(json.dumps({"error": "Invalid Lighthouse report", "detail": str(exc)}), file=sys.stderr)
        return 2
    text = json.dumps(evidence, indent=2)
    if a.output:
        Path(a.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
