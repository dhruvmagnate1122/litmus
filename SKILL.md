---
name: product-quality-gate
description: Review a digital product across security, SEO, performance, and conversion-copy quality using source checks plus config, project facts, runtime evidence, and manual review. Use before launch, after major changes, or when assessing AI-built or traditionally coded web products. Does not guarantee security, rankings, speed, or conversions.
---

# Product Quality Gate

Use this evidence pipeline: source → config → questionnaire → runtime → evidence → status. Do not flatten all checks into regexes.

## Workflow

1. Read project instructions and `assets/project-profile.json`; keep unknown facts unknown.
2. Run `python3 <skill-dir>/scripts/check.py <project-root> [--profile <profile.json>] [--evidence <evidence.json>]`.
3. Treat source matches as `REVIEW`, not proof of a vulnerability or defect.
4. Apply only relevant packs from `packs/`. Use `NOT_APPLICABLE` when architecture/product facts make a check irrelevant.
5. For security, prefer OWASP-aligned evidence and isolated runtime tests. Never probe systems without authorization.
6. For SEO, distinguish technical indexability from rankings. A technically healthy site is not guaranteed to rank.
7. For performance, measure actual bottlenecks before prescribing infrastructure. Do not add load balancers, caches, CDNs, or connection pools just to satisfy a checklist.
8. For copy, distinguish factual claims from style preferences. Unsupported factual claims can be `CLAIM_NEEDS_EVIDENCE`; style items should normally be `SUGGESTION`.
9. Report evidence date/environment and remaining unknowns. Never manufacture a `PASS`.
10. Run `python3 <skill-dir>/scripts/test_check.py` after rule or engine changes.

Engineering statuses: `PASS`, `FAIL`, `REVIEW`, `UNKNOWN`, `NOT_APPLICABLE`. Copy may additionally use `SUGGESTION` and `CLAIM_NEEDS_EVIDENCE`.
