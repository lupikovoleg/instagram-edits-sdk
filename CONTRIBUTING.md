# Contributing

Keep evidence levels explicit. A registry entry or a passing mock test must not
be labelled as a live-verified server contract. Record APK version, operation ID,
request variables, response schema, date and limits for a new finding.

Do not submit cookies, Authorization headers, passwords, HAR captures, real
personal response dumps, APK binaries, decompiled Meta source, or copied media.
Fixtures must be clearly synthetic. Keep request examples read-only by default.

Before submitting:

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/offline_demo.py
python tools/generate_docs.py --check
python tools/check_release.py
```

CI must never call Instagram. Real verification needs an explicitly authorized
account, and should publish only a sanitized evidence record.
