# Litmus launch kit

Use the problem and the evidence model as the hook. Do not ask for stars before giving people a reason to care.

## Show HN draft

**Title:** Show HN: Litmus – an evidence-driven pre-launch quality gate for web apps

AI coding tools can get an app from prompt to deploy very quickly, but the last-mile review is still fragmented: AppSec checks in one place, technical SEO somewhere else, performance in Lighthouse, and conversion copy in a doc.

I built Litmus as an open-source quality-gate framework for that last mile.

The design constraint is that regex is not proof. Static source matches are only REVIEW candidates. Rules declare severity and required evidence, and runtime/config/external/manual evidence resolves them. The report separates release blockers, high-risk review, unknowns, lower-severity work, and suggestions instead of returning one fake green score.

Current packs:
- Application Security Baseline
- Technical Discoverability
- Web Performance (experimental, measurement-first)
- Conversion Copy Review (guided human review)

The core is dependency-free Python and intentionally lightweight. Browser automation, Lighthouse/RUM, SCA feeds and other richer checks are future adapters rather than being faked by regex.

Repo: https://github.com/dhruvmagnate1122/litmus

I’d especially value criticism of the evidence model, false-positive handling, and what should *not* be in a launch gate.

## LinkedIn draft

AI can build a web app in a weekend.

It can also ship a leaked secret, broken authorization boundary, accidental `noindex`, slow Core Web Vitals, and unsupported marketing claims in the same weekend.

I’ve open-sourced **Litmus**, a pre-launch Product Quality Gate covering:
- application-security baseline;
- technical discoverability;
- measured web performance;
- conversion-copy review.

The main design choice: **static detection is not proof**.

A regex match becomes a review candidate, not an automatic vulnerability. Litmus tracks status, severity and verification strength separately and asks for reproducible evidence before meaningful PASS results.

It’s early (v0.1.0), intentionally scoped to web apps, and I’m looking for engineers who want to challenge the rule/evidence model or contribute adapters.

https://github.com/dhruvmagnate1122/litmus

## Short X / Threads draft

Built an open-source pre-launch gate for web apps:

Litmus checks AppSec + technical SEO + performance + conversion copy.

Key rule: regex ≠ proof.

Static hits are REVIEW candidates; runtime/config/tool evidence decides what’s actually verified.

https://github.com/dhruvmagnate1122/litmus

## Reddit/dev-community angle

Do not copy-paste the same promotion everywhere. Lead with a technical question or lesson relevant to that community.

Useful angles:
- r/webdev / dev communities: “What belongs in a real pre-launch gate, and what is cargo-cult checklist bloat?”
- AppSec communities: “I’m mapping an evidence-driven baseline to OWASP Top 10/ASVS without pretending static analysis proves runtime security.”
- SEO communities: “Separating technical discoverability from Search Console/backlinks and from performance metrics.”
- performance communities: “Why I removed N+1/index/code-splitting from hard gates and made the pack measurement-first.”
- SaaS/founder communities: “The last-mile QA problem for AI-built products.”

Always disclose that you are the author.

## Content ideas that naturally generate repo discovery

1. Run Litmus against intentionally flawed demo apps and publish the findings.
2. Publish “what the checker refused to call a failure” examples to show conservative design.
3. Compare a regex-only finding with the runtime evidence needed to resolve it.
4. Write a post on why Performance was rebuilt around budgets instead of techniques.
5. Invite maintainers to contribute framework adapters rather than asking for stars.
