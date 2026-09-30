# Security policy

Litmus is a review tool and may itself have security defects.

If you find a vulnerability in Litmus that could expose secrets, execute unintended code, corrupt evidence, or otherwise create security risk, please avoid publishing exploit details in a public issue until the maintainer has had a reasonable opportunity to assess it.

For ordinary false positives, false negatives, missing checks, or rule-design concerns, use a normal GitHub issue.

Litmus does not execute target project code during its dependency-free static triage. Contributions should preserve that boundary unless a future adapter explicitly documents and isolates runtime execution.
