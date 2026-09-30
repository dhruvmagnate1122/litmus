# Review guide

## Evidence

Use `source`, `config`, `questionnaire`, `runtime`, and `evidence`. Engineering `PASS` requires declared evidence types where applicable. `FAIL` means an observed technical/behavioral expectation failed. `REVIEW` is ambiguous/candidate evidence. `UNKNOWN` means evidence is missing. `NOT_APPLICABLE` needs a rationale.

For copy, use `CLAIM_NEEDS_EVIDENCE` for unsupported factual marketing claims and `SUGGESTION` for subjective style changes.

## Security

Use authorized test environments and synthetic data. Test privileged routes by direct API/resource access, data isolation with cross-tenant synthetic users, allowed/disallowed CORS origins, upload type/size/content/storage behavior, valid/invalid webhook signatures, bounded rate-limit tests, production error handling, and representative logs for secrets/tokens/sensitive data.

## SEO

Fetch robots, sitemap and metadata from the deployed environment; crawl representative routes for indexability and broken links; validate structured data only when relevant; measure Core Web Vitals with documented device/network context; verify HTTPS behavior. Search Console and backlinks are external/manual evidence. `llms.txt` is optional and its absence is not a Google SEO failure.

## Performance

Measure before prescribing. Use query logs/profiling for indexes/N+1, validate cache correctness and invalidation, inspect bundles/long tasks/re-renders, review image dimensions/formats/compression/loading, and determine whether pooling/load balancing/CDN are already provider-managed or unnecessary.

## Conversion copy

Separate claims from style. Material claims need defensible evidence. CTA/headline/benefit/objection checks are heuristics. Em dashes, aphorisms and antithesis are stylistic choices, never automatic failures.
