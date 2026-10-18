"""Read public metrics, delta, comments or Kits; saves the complete response."""
import argparse
from edits_api import EditsClient, EditsError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("public", "delta", "comments", "kits"))
    parser.add_argument("--reel", help="Owned Reel URL or numeric ID; required except for Kits")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.operation != "kits" and not args.reel:
        parser.error("--reel is required for this operation")
    try:
        client = EditsClient.from_env()
        if args.operation == "public":
            result = client.public_insights(args.reel)
        elif args.operation == "delta":
            result = client.reels_delta([args.reel])
        elif args.operation == "comments":
            result = client.comment_insights(args.reel)
            analysis = result.get_data("xig_fetch_media", "ai_comment_insights")
            print(f"Comment analysis available: {analysis is not None}")
        else:
            result = client.kits()
            connection = result.get_data("xig_basel_kits", "kits")
            print(f"Kits returned: {len(connection['edges'])}")
        result.save_json(args.output)
        print(f"Saved {result.operation} response to {args.output}")
    except EditsError as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
