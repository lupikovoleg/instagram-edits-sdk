"""Synthetic demonstration. Does not send any network requests or use real credentials."""
import argparse
from pathlib import Path
import tempfile
from edits_api import EditsClient, Session


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional new export directory")
    args = parser.parse_args()
    fixture = Path(__file__).resolve().parents[1] / "tests/fixtures/reel_details.synthetic.json"
    data = fixture.read_bytes()
    client = EditsClient(Session.from_sessionid("999:SYNTHETIC-ONLY"),
                         transport=lambda request, timeout: (200, data, "application/json"))
    result = client.reel_insights("12345")
    if args.output:
        result.export(args.output)
    else:
        with tempfile.TemporaryDirectory() as parent:
            result.export(Path(parent) / "synthetic-demo")
    print(f"SYNTHETIC: {len(result.retention)} points; live_request={result.response.live_request}")


if __name__ == "__main__":
    main()
