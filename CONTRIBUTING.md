# Contributing to Litmus

Litmus should become more useful without becoming more confident than its evidence allows.

## Good contributions

- reduce a known false positive;
- add a framework/runtime adapter that produces reproducible evidence;
- add or improve a pack rule with severity, applicability, evidence requirements and a concrete next step;
- add tests for an evidence conflict or edge case;
- improve documentation with a reproducible example;
- add a new pack only when its scope and evidence model are clear.

## Rule requirements

Every gating rule should define:

- stable `id`;
- `title`;
- `severity`: `critical/high/medium/low/info`;
- `automation` level;
- required `evidence` types;
- `next_step`;
- applicability notes where the check is conditional;
- authoritative or primary references when the rule depends on an external standard.

Do not turn a coding preference into a security/performance/SEO failure.

## Evidence rules

Static patterns are candidates, not proof. A new detector should normally emit `REVIEW`, not `FAIL`.

Evidence must include provenance, timestamp, environment and an `artifact` or `reference`. Manual evidence must remain visibly manual.

## Pull requests

1. Keep changes narrowly scoped.
2. Add or update regression tests.
3. Run:
   ```sh
   python3 scripts/test_check.py
   ```
4. Explain false-positive/false-negative tradeoffs.
5. For a new rule, include at least one passing and one failing/review fixture when practical.

## Beginner-friendly contribution paths

- add a documented example;
- improve a `next_step`;
- add a framework-specific detector that only emits `REVIEW`;
- add a test for `artifact` / `reference` evidence;
- improve an issue template;
- add a runtime evidence adapter design note.

## What we will reject

- claims that Litmus certifies security, SEO, performance or conversion outcomes;
- rules that hard-fail subjective style preferences;
- regexes presented as proof of runtime behavior;
- CVE claims without an external advisory source;
- broad rewrites without tests.
