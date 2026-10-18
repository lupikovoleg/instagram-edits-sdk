"""Fetch ONE cursor page; pagination was verified with two pages."""
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
        page = EditsClient.from_env().reels_page(
            first=args.first, after=args.after, timeframe=args.timeframe, order_by=args.order_by)
        page.response.save_json(args.output)
    except EditsError as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(f"Saved {len(page.items)} Reels to {args.output}; has_next_page={page.has_next_page}")
    # page.next_cursor can be passed to the next call; treat it as account data.


if __name__ == "__main__":
    main()
