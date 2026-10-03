# Lighthouse importer example

`lighthouse-report.json` is a small, sanitized Lighthouse report (example.com, only the audits the importer reads).

Convert it into Litmus evidence and run the gate with it:

```sh
python3 scripts/lighthouse_import.py examples/lighthouse/lighthouse-report.json --output /tmp/lh-evidence.json
python3 scripts/check.py examples/minimal-web-app --evidence /tmp/lh-evidence.json
```

## What the importer records

| Rule | Lighthouse audit(s) |
|---|---|
| `PERF-CWV` | `largest-contentful-paint`, `cumulative-layout-shift` (TBT noted as a proxy only) |
| `PERF-LONGTASKS` | `total-blocking-time`, `long-tasks` |
| `PERF-JS-BUDGET` | `bootup-time` |
| `PERF-REQUESTS` | `network-requests` |
| `PERF-THIRD-PARTY` | `third-party-summary` |

Every record carries the Lighthouse version (`producer`), `fetchTime` (`observed_at`), device and throttling (`environment`) and a `reference` to the report (the file name by default, or `--reference`).

## Lab vs field

- A Lighthouse report is **lab data**: one synthetic page load. Lab records are always `REVIEW`, even when within budget, because a single lab run does not prove production performance. INP cannot be measured in a lab run.
- If the input is a PageSpeed Insights API response with `loadingExperience`, the importer adds a separate **field** record for `PERF-CWV` from the Chrome UX Report p75 values. It is `PASS` only when LCP, INP and CLS are all present and within the pack budget; otherwise `REVIEW`.
- Because the lab record stays `REVIEW`, `PERF-CWV` remains `REVIEW` until a human resolves it.


Invalid metric values (booleans, negative or non-finite numbers, and strings) are rejected. Field scope uses loadingExperience.id when supplied; the lab device and run timestamp do not establish the field collection device or period. Consult the referenced report/CrUX data for those details.
