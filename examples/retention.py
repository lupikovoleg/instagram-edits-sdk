"""Live: IG_SESSIONID supplied by your secret manager; fetch one owned Reel."""
import argparse
from edits_api import EditsClient, EditsError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reel", help="Owned Reel URL or numeric media ID")
    parser.add_argument("--output", required=True, help="New export directory")
    args = parser.parse_args()
    try:
        result = EditsClient.from_env().reel_insights(args.reel)
        result.export(args.output)
    except EditsError as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(f"{len(result.retention)} points saved to {args.output}")


if __name__ == "__main__":
    main()
