# Review guide

## Evidence contract

Evidence JSON is user/tool supplied and therefore not self-authenticating. The core validates shape, dates and required fields, then exposes provenance.

Required fields per record: `type`, `result`, `details`, `observed_at`, `environment`, `producer.kind`, and `producer.name`, plus at least one reproducible pointer using either `artifact` or `reference`.

Accepted producer kinds: `tool`, `external`, `manual`.

Conflict handling:
- any `FAIL` evidence => `FAIL`;
- `REVIEW` or contradictory PASS/FAIL signals => `REVIEW` unless FAIL is present;
- source candidates remain recorded;
- a source candidate can be resolved to `PASS` only when all evidence types required by that rule pass;
- missing required evidence => `UNKNOWN`, or `REVIEW` if a static candidate exists.

Evidence freshness is surfaced; the core does not decide universal expiration because acceptable age depends on deployment/change cadence. Agents/reviewers should reject stale evidence after material changes.

## Release decision

Default blockers: `FAIL` with severity `critical` or `high`.
Required review: unresolved `REVIEW` with severity `critical` or `high`.
Unknowns must be resolved, explicitly accepted/deferred, or marked `NOT_APPLICABLE` with rationale.

## Security

Use authorized test environments and synthetic data. Map coverage to OWASP Top 10:2025 but use ASVS-style verifiable requirements. Review direct object/action authorization, session/cookie lifecycle, SSRF/egress, CSRF where applicable, security headers, cloud/storage exposure, cryptography/key lifecycle, injection contexts, auth/recovery, supply-chain integrity, webhook/data integrity, security logging/alerting and exceptional-condition behavior. Current CVE conclusions require external/SCA evidence.

## Technical discoverability

Separate crawlability, indexability and renderability. Test deployed status codes/redirects, robots/meta directives, canonical behavior where duplicates exist, rendered content/links, internal links/orphans, broken links, structured data, duplicates/facets, hreflang/migrations where applicable. Search Console/backlinks are external/manual.

## Performance

Start with numeric/runtime evidence. Record lab vs field data, page/journey, device/network profile, percentile/sample size where applicable. Default CWV good references: LCP <= 2500ms, INP <= 200ms, CLS <= 0.1 at the 75th percentile. Projects may define stricter budgets.

Only diagnose caching, indexes/N+1, code splitting, lazy loading, re-renders or infrastructure after measurements identify a need. Source patterns are hints only.

## Conversion copy

Guided human review with machine assistance. Claim integrity requires evidence. Conversion heuristics need context from buyer/use case and page/journey. Style items are suggestions only.
