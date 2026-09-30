---
name: product-quality-gate
description: Review web applications across an application-security baseline, technical discoverability, measured web performance, and conversion-copy quality. Uses static candidate signals plus config, project facts, runtime/external evidence and guided human review. Does not certify security or guarantee ranking, performance, or conversion outcomes.
---

# Litmus / Product Quality Gate

Use the evidence pipeline: source → config/questionnaire → runtime/external/manual evidence → adjudication → release summary.

1. Scope the project with `assets/project-profile.json`. v0.1.0 targets web applications/sites; mark irrelevant rules `NOT_APPLICABLE` with rationale.
2. Run `scripts/check.py`. Treat static matches as `REVIEW` candidates only.
3. For each applicable rule, gather the evidence types declared in `packs/*.json`. Evidence must include provenance, timestamp, environment and artifact/reference.
4. Never convert incomplete or contradictory evidence into `PASS`. `FAIL` evidence wins; unresolved conflict remains `REVIEW`.
5. Use severity separately from status. `CRITICAL/HIGH` failures are release blockers by default; lower severities require explicit accept/defer decisions.
6. Security is an ASVS-oriented baseline with OWASP Top 10:2025 mapping, not a claim of complete Top 10 detection. Use authorized environments and external SCA/advisory tools for current dependency vulnerabilities.
7. SEO is technical discoverability. Search Console/backlinks are manual/external. Consume performance results instead of duplicating CWV/image checks.
8. Performance is measurement-first. Do not prescribe caching, indexes, N+1 fixes, code splitting, CDN/pooling/load balancing, or framework tactics without measured evidence.
9. Conversion copy is guided human review. Only claim integrity should hard-fail; heuristics/styles are review/suggestion territory.
10. Produce a release summary: blockers, required review, unknowns, accepted/deferred items, and suggestions. Never output a blanket compliance or quality badge.
11. Run `python3 <skill-dir>/scripts/test_check.py` after changing engine or pack definitions.
