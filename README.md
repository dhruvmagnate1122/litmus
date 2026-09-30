# Litmus — Product Quality Gate

**One command to review a web app before launch across security, technical SEO, performance, and conversion quality — without pretending regex equals proof.**

Litmus is an open-source coding-agent skill plus lightweight Python triage engine. It finds conservative source candidates, then uses configuration, runtime, external-tool, and human evidence to decide what is actually verified.

> **A clean scan is not an all-clear.** Static findings are candidates, most meaningful passes require evidence, and Litmus never claims security certification, ranking guarantees, performance guarantees, or conversion lift.

## See the shape of a Litmus report

```text
LITMUS RELEASE DECISION: NEEDS_REVIEW

RELEASE BLOCKERS
  none

REQUIRED REVIEW
  [HIGH] SEC-DEBUG
    Static candidate: production debug setting detected
    Verification: static-candidate
    Next: verify deployed configuration and error behavior

UNKNOWNS
  [HIGH] PERF-CWV
    Runtime measurement not supplied
    Next: measure representative routes and record lab/field context

VERIFIED
  [HIGH] SEO-INDEX
    Status: PASS
    Verification: tool/external-attested
```

Litmus is deliberately not a green-checkmark generator. It separates **status**, **severity**, and **verification strength**, preserves conflicting evidence, and surfaces a release decision with blockers, required review, unknowns, deferred work, and suggestions.

## Try it

```sh
git clone https://github.com/dhruvmagnate1122/litmus.git
cd litmus
python3 scripts/check.py /absolute/path/to/your-web-app
```

Add project facts and evidence when you have them:

```sh
python3 scripts/check.py /absolute/path/to/your-web-app \
  --profile /path/to/project-profile.json \
  --evidence /path/to/evidence.json
```

No third-party Python packages are required for the core triage/status engine.

## Why Litmus instead of another checklist?

| Plain checklist | Regex-only scanner | Litmus |
|---|---|---|
| Easy to forget or cargo-cult | Fast but noisy | Static candidates + evidence |
| No provenance | Often treats presence as proof | Provenance and verification level |
| All failures look alike | Usually tool-specific severity | Status + severity kept separate |
| Little path from finding to decision | Findings stop at detection | Next-step evidence + release summary |
| Hard to extend consistently | Rules live in code | Versioned packs + contribution surface |

## Contribute a pack, adapter, or rule

Litmus is intentionally extensible. Useful contributions include framework adapters, runtime-evidence collectors, better static candidates, false-positive reductions, and domain packs.

Start with [CONTRIBUTING.md](CONTRIBUTING.md), the [roadmap](ROADMAP.md), or one of the repository's `good first issue` tasks.

A minimal example project and evidence fixture live under [examples/minimal-web-app](examples/minimal-web-app).

## What the gate actually decides

Litmus separates three dimensions:

- **status:** `PASS / FAIL / REVIEW / UNKNOWN / NOT_APPLICABLE`; copy may also use `SUGGESTION / CLAIM_NEEDS_EVIDENCE`
- **severity:** `CRITICAL / HIGH / MEDIUM / LOW / INFO`
- **verification:** static candidate, partial evidence, manual-attested, tool/external-attested, or mixed evidence

A `FAIL + CRITICAL` can block release; a `FAIL + LOW` does not automatically do so. Static regex findings are `REVIEW`, never automatic `FAIL`.

### Release decision

The report groups results into:

1. **release blockers** — `FAIL` at `CRITICAL` or `HIGH`
2. **required review** — unresolved `REVIEW` at `CRITICAL` or `HIGH`
3. **unknowns** — missing evidence that must be accepted, resolved, or marked `NOT_APPLICABLE`
4. **accepted/deferred work** — lower-severity items with an explicit decision
5. **suggestions** — non-gating copy/style guidance

Litmus does not manufacture a single green “all clear.”

## Evidence trust model

`evidence.json` is an input contract, not proof of truth. Each evidence record must include:

- `type` — e.g. `source`, `config`, `questionnaire`, `runtime`, `external`, `manual`
- `result`
- `details`
- `observed_at`
- `environment`
- `producer.kind` (`tool`, `external`, or `manual`) and `producer.name`
- either `artifact` or `reference` — a reproducible pointer to the supporting evidence

The core validates structure and adjudicates conflicts; it **cannot cryptographically prove that user-supplied evidence is honest**. Reports therefore expose evidence provenance and verification level.

Conflict rules are conservative: `FAIL` evidence wins; conflicting/partial evidence becomes `REVIEW`; a static candidate may be resolved to `PASS` only when all evidence types required by the rule pass, and the original candidate remains recorded.

## Quick start

```sh
python3 scripts/check.py /absolute/path/to/project
python3 scripts/check.py /absolute/path/to/project --profile /path/to/project-profile.json
python3 scripts/check.py /absolute/path/to/project --profile /path/to/project-profile.json --evidence /path/to/evidence.json
python3 scripts/test_check.py
```

The dependency-free core is intentionally a **triage/status engine**. It does not pretend to replace HTML/JS parsers, browser automation, Lighthouse/RUM, SCA/CVE feeds, database profilers, Search Console, or human review. Rich adapters are future extension points.

## Pack maturity

| Pack | Maturity | What gates |
|---|---|---|
| Application Security Baseline | baseline | High-confidence control failures; OWASP ASVS-oriented, Top 10:2025 mapped |
| Technical Discoverability | baseline | Crawl/index/render failures; search operations are manual/external |
| Web Performance | experimental | Numeric/runtime budgets; implementation techniques are diagnostics |
| Conversion Copy Review | guided | Claim integrity can fail; persuasion/style is guided human review |

## Packs

### Application Security Baseline

Covers authorization, tenant isolation, SSRF/egress, security misconfiguration/headers, storage exposure, supply-chain integrity, cryptography/key management, secrets, injection, server validation, XSS, CSRF, threat modeling, abuse controls, authentication, session/cookie lifecycle, MFA where warranted, recovery, webhook/integrity controls, safe logging, security logging/alerting, exceptional conditions and uploads.

OWASP Top 10:2025 is used as a **coverage map**, not a claim of complete detection. The verification approach is ASVS-oriented because OWASP recommends ASVS for verifiable application-security requirements.

Dependency/CVE status is **external evidence**: the offline core can inventory files/configuration but cannot know current advisories without an advisory feed or SCA tool.

### Technical Discoverability

Covers indexability, robots, optional sitemaps, canonicalization where duplicates exist, status/redirect behavior, rendered-content availability, titles/descriptions/headings, structured data, internal/broken links, duplicate/faceted URLs, hreflang where relevant, migrations and HTTPS/host behavior.

Search Console and backlinks are **manual/external search-operations evidence**, not local automated checks. `llms.txt` remains optional/experimental and is never a Google ranking requirement.

Core Web Vitals and image-weight budgets live in **Performance**. SEO consumes those results rather than duplicating them.

### Web Performance

This pack is **measurement first**. The gate starts with Core Web Vitals and project budgets, then API/database latency, JS/image/payload/request budgets, long tasks, third-party cost, cold starts where applicable, and regressions against an accepted baseline.

Caching, indexes, N+1, code splitting, lazy loading, client re-renders, CDN/pooling/load-balancing, and similar techniques are **diagnostics**, not universal requirements. A source grep cannot prove an N+1 problem or a missing index.

Default Core Web Vitals “good” reference thresholds in the pack are LCP ≤ 2.5s, INP ≤ 200ms and CLS ≤ 0.1 at the 75th percentile; projects can define stricter budgets.

### Conversion Copy Review

This pack is explicitly **guided human review with machine assistance**:

- **claim integrity:** evidence for material factual claims; may produce `FAIL` / `CLAIM_NEEDS_EVIDENCE`
- **conversion heuristics:** offer clarity, audience match, headline/body continuity, benefits, CTA, friction, objections, above-the-fold clarity, scannability and state copy; generally `REVIEW` / `SUGGESTION`
- **style suggestions:** optional only; em dashes, aphorisms or antithesis are never failures

## From REVIEW/UNKNOWN to a ship decision

Every rule carries `next_step` guidance and required evidence types. Teams should resolve, explicitly accept/defer, or mark inapplicable before treating the gate as complete. The final report surfaces blockers separately from unresolved lower-risk work so a project does not drown in an undifferentiated list.

## Layout

- `SKILL.md` — agent workflow
- `scripts/check.py` — lightweight static triage + evidence adjudication + release summary
- `scripts/test_check.py` — regression tests
- `packs/*.json` — severity, automatability, evidence requirements, maturity and next steps
- `assets/project-profile.json` — applicability/project facts
- `assets/evidence-example.json` — evidence contract example
- `references/review-guide.md` — runtime/config/manual recipes
- `LICENSE` — MIT

## Limits

v0.1.0 is scoped to web applications/sites. Native mobile needs a separate pack. LLM-feature products need additional AI-specific security controls beyond this baseline. No claim of security certification, ranking prediction, performance guarantee, or conversion lift is made.
