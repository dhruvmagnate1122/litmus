# Minimal Litmus fixture

This tiny fixture exists to demonstrate candidate detection and evidence resolution. It is **not** a production starter app.

Run:

```sh
python3 ../../scripts/check.py . --profile profile.json --evidence evidence.json
```

The fixture intentionally includes a `noindex` candidate in `index.html`. The evidence file shows how runtime evidence can leave that candidate under review rather than pretending source presence alone proves an SEO defect.
