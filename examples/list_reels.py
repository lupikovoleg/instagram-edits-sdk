"""Live, static-only contract: fetch ONE page; no automatic cursor guessing."""
import argparse
from edits_api import EditsClient, EditsError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first", type=int, default=10)
    parser.add_argument("--after")
    parser.add_argument("--timeframe", default="LIFETIME")
    parser.add_argument("--order-by", default="BY_DATE")
    parser.add_argument("--output", required=True, help="New JSON file")
    args = parser.parse_args()
    try:
        response = EditsClient.from_env().account_reels(
            first=args.first, after=args.after, timeframe=args.timeframe, order_by=args.order_by)
        response.save_json(args.output)
    except EditsError as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(f"Raw page saved to {args.output}; inspect its actual cursor before continuing.")


if __name__ == "__main__":
    main()
