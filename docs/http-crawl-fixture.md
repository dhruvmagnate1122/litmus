# Technical Discoverability HTTP fixture

Issue #3 is implemented as a test-only slice. No production crawler or SEO
pack/engine changes are required.

Run from the repository root with Python's standard library:

```sh
python3 scripts/test_check.py
python3 scripts/test_http_crawl.py
# Or run both through discovery:
python3 -m unittest discover -s scripts -p 'test_*.py'
```

## Structure and intent

- `scripts/fixtures/http-crawl.json`: explicit HTTP routes (status, headers,
  body) and named cases (path, check, expected evidence result).
- `scripts/test_http_crawl.py`: serves those routes on an ephemeral loopback
  port, makes direct HTTP connections, records observations, validates evidence,
  and checks the engine's adjudication.

Every tested page is declared intended public/indexable except that robots.txt
deliberately blocks /private to demonstrate a mismatch. /missing is an intentional
404; the defect is linking/canonicalizing to it. Canonical cases declare /ok the
preferred duplicate URL. The test is a bounded sampler of these declared routes,
not a general website crawler. Redirects are followed manually for at most five
requests; the one-hop loop must remain unresolved.

| Case / route | SEO check | Runtime assertion / engine result |
|---|---|---|
| redirect: /old → /moved → /ok | SEO-STATUS | PASS; preserves 301/302/200 chain |
| loop: /loop; error: /error | SEO-STATUS | FAIL for bounded loop / 500 |
| indexable: /ok | SEO-INDEX | Runtime PASS alone → UNKNOWN; with static candidate → REVIEW; source + runtime PASS → PASS |
| meta-noindex; header-noindex | SEO-INDEX | FAIL for unintended meta / X-Robots-Tag noindex |
| robots-allowed: /ok; robots-blocked: /private | SEO-ROBOTS | PASS / FAIL against declared crawl intent |
| canonical: /duplicate; bad-canonical: /bad-canonical | SEO-CANONICAL | PASS for declared /ok target (200); FAIL for /missing (404) |
| broken-link: /links → /ok and /missing | SEO-BROKEN | FAIL; records successful and broken destinations |

## Reproducible evidence

`observe(case)` returns a separate record for each case under its SEO check ID.
The tests pass those records through the current `validate_evidence` contract:
`type=runtime`, `result=PASS/FAIL`, serialized response details, `observed_at`,
`environment=synthetic-loopback-fixture`, `producer.kind=tool`,
`producer.name=scripts/test_http_crawl.py`, and `reference`.

References are repository-relative JSON Pointers, for example
`scripts/fixtures/http-crawl.json#/cases/0` identifies the redirect case.
Resolve the pointer within the same Git revision and rerun the commands above.
Response details use relative paths, so neither the temporary port nor machine
paths enter evidence. Two observations must produce identical records.
The fixed timestamp is synthetic fixture metadata, **not a real deployment
observation time**. These records are test inputs, not evidence for your app.

The source record used to resolve SEO-INDEX is explicitly manual-attested fixture
intent. Missing evidence stays UNKNOWN; incomplete resolution of a static
candidate stays REVIEW; explicit REVIEW persists; FAIL wins even against PASS.
No source PASS is inferred from the HTTP response.

## Manual and external scope

For a real app, confirm route/index intent and representative coverage manually.
A noindex on a private page or an intentional 404 is not automatically a defect.
Canonical tags are hints: checking one declared local target does not verify
search-engine canonical selection, duplicate-content equivalence, or facets.
robots.txt controls crawling rather than guaranteeing deindexing.

This fixture does not execute JavaScript, compare browser-rendered content
(SEO-RENDER), inventory orphan pages (SEO-INTERNAL), validate sitemaps/schema,
review titles/content/accessibility, or assess hreflang/migration completeness.
Those checks retain their normal missing-evidence state.
HTTPS/TLS, canonical host behavior, authentication/staging gates, deployed
headers/CDNs, and production route coverage need separate deployed evidence.
Search Console/indexing diagnostics and backlink analysis remain manual/external.

No live third-party request is made. The client connects directly to 127.0.0.1,
ignores proxy environment settings, and never automatically follows redirects.
All fixture targets are relative paths; tests reject external/authority targets
before a request. There are no third-party packages, browser downloads, DNS
lookups, external validators, or live search dependencies.
