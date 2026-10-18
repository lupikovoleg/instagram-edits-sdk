#!/usr/bin/env python3
"""Check publishable sources and docs, not private browser/session data."""
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
    if [o["operation_name"] for o in operations if o["evidence_level"] == "live-verified"] != ["BaselReelDetailsQuery"]:
        errors.append("Unexpected live verification claims")
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
        forbidden = ["/Users/" + "oleglupikov", "lupikov" + "oleg", "399546659388" + "0963822"]
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
