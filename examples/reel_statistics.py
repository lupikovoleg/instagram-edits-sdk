"""Fetch statistics even if Instagram does not provide a retention curve."""
import argparse
from edits_api import EditsClient, EditsError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reel")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        result = EditsClient.from_env().reel_insights(args.reel)
        result.export(args.output)
        print(f"Statistics saved. Retention available: {result.retention_available}")
    except EditsError as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
