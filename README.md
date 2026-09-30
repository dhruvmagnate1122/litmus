# Product Quality Gate

A reusable coding-agent skill and dependency-free Python checker for reviewing four launch-quality areas: security, SEO/discoverability, performance, and conversion copy.

**Version 0.1.0 — evidence-driven review.** It combines conservative source-pattern detection with configuration inspection, project facts, runtime evidence, and manual/heuristic review. It does not certify security, guarantee rankings, guarantee performance, or guarantee conversion lift.

## Statuses

Engineering packs: `PASS / FAIL / REVIEW / UNKNOWN / NOT_APPLICABLE`.

Conversion-copy may additionally use: `SUGGESTION / CLAIM_NEEDS_EVIDENCE`.

## Quick start

```sh
python3 scripts/check.py /absolute/path/to/project
python3 scripts/check.py /absolute/path/to/project --profile /path/to/project-profile.json
python3 scripts/check.py /absolute/path/to/project --profile /path/to/project-profile.json --evidence /path/to/evidence.json
python3 scripts/test_check.py
```

## Packs

- **Security:** authorization/admin routes, row-level or equivalent data isolation where applicable, secrets, Git/env hygiene, sensitive logging, parameterized queries, server-side input validation, XSS defenses, file uploads, webhook verification, rate limiting, CORS, production debug settings, dependency review, password/auth handling, email verification where relevant, and independent security review.
- **SEO:** indexability, robots, sitemap, canonicals, titles, descriptions, headings, alt text, structured data, internal/broken links, images, Core Web Vitals, mobile, HTTPS, URLs, social previews, Search Console, backlinks, and optional `llms.txt`.
- **Performance:** caching where safe, DB indexes, N+1 review, images, loading states, debouncing, code splitting, CDN/platform delivery, server caching, pagination, payloads, re-renders, minification, lazy loading, deferred scripts, unused dependencies, connection pooling, and load balancing when architecture requires it.
- **Conversion copy:** scannability, section focus, specific headlines, headline/body alignment, benefits, CTAs, objections, proof, unsupported claims, audience specificity, above-the-fold clarity, and optional style suggestions.

`llms.txt` is optional/experimental and is not treated as a Google ranking requirement. Pure copy-style preferences such as em-dash usage are never hard failures.

## Layout

- `SKILL.md` — agent workflow
- `scripts/check.py` — conservative local scanner + evidence status engine
- `scripts/test_check.py` — regression tests
- `packs/*.json` — pack definitions
- `assets/project-profile.json` — project facts
- `assets/evidence-example.json` — evidence format
- `references/review-guide.md` — runtime/config recipes
- `LICENSE` — MIT

A clean scan does not mean a product is secure, fast, rankable, or persuasive. Many checks require a running app, provider configuration, measurements, or human judgment.
