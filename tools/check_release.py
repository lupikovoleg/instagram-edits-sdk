#!/usr/bin/env python3
"""Check publishable sources and docs, not private browser/session data."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".venv", "build", "dist", "__pycache__", "results"}


def main():
    errors = []
    operations = json.loads((ROOT / "src/edits_api/operations.json").read_text())
    if len(operations) != 1663 or sum(o["edits_related"] for o in operations) != 88:
        errors.append("Catalog cardinality changed without updating provenance")
    evidence = json.loads((ROOT / "docs/evidence/method-verification.json").read_text())
    verified = {r["operation"] for r in evidence["requests"] if r["http_status"] == 200}
    if {o["operation_name"] for o in operations if o["evidence_level"] == "live-verified"} != verified:
        errors.append("Live verification claims differ from recorded evidence")
    vendor = ROOT / "docs/swagger/vendor"
    provenance = json.loads((vendor / "provenance.json").read_text())
    for name in ("swagger-ui-bundle.js", "swagger-ui.css", "LICENSE", "swagger-ui-bundle.js.LICENSE.txt"):
        path = vendor / name
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != provenance.get("sha256", {}).get(name):
            errors.append(f"Missing or modified Swagger distribution file: {name}")
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if not path.is_file() or any(p in EXCLUDED or p.startswith(".venv") or p.endswith(".egg-info") for p in rel.parts):
            continue
        if path.suffix in {".apk", ".dex", ".so", ".har"}:
            errors.append(f"Unpublishable artifact: {rel}")
            continue
        try:
            text = path.read_text()
        except UnicodeError:
            errors.append(f"Unexpected binary: {rel}")
            continue
        # This public project URL is intentional; account identifiers in response data are not.
        public_repository = "https://github.com/" + "lupikov" + "oleg/instagram-edits-sdk"
        text = text.replace(public_repository, "https://github.com/OWNER/instagram-edits-sdk")
        if rel == Path("docs/releasing.md"):
            # The Trusted Publisher form requires the public GitHub owner explicitly.
            text = text.replace("`lupikov" + "oleg`", "`PUBLIC_GITHUB_OWNER`")
        forbidden = ["/Users/" + "oleglupikov", "lupikov" + "oleg", "399546659388" + "0963822", "2303" + "9664", "Ddyv7" + "LANvru"]
        if any(value in text for value in forbidden):
            errors.append(f"Private/local identifier in {rel}")
        if re.search(r"Bearer IGT:2:[A-Za-z0-9+/=]{32,}", text):
            errors.append(f"Possible authorization token in {rel}")
        if path.suffix == ".md":
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" not in target and not target.startswith("#"):
                    local = target.split("#", 1)[0]
                    if local and not (path.parent / local).exists():
                        errors.append(f"Broken link in {rel}: {target}")
    if errors:
        raise SystemExit("\n".join(errors))
    print("Release sources checked: no APKs, response dumps, local account identifiers or token-shaped values; links valid.")


if __name__ == "__main__":
    main()
