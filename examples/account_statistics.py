"""Fetch account or audience statistics; LAST_30_DAYS was live-tested."""
import argparse
from edits_api import EditsClient, EditsError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--period", default="LAST_30_DAYS", help="Period enum, default LAST_30_DAYS")
    parser.add_argument("--audience", action="store_true", help="Use BaselAudienceInsightsQuery")
    parser.add_argument("--timezone", default="UTC")
    parser.add_argument("--output", required=True, help="New JSON file")
    args = parser.parse_args()
    try:
        client = EditsClient.from_env()
        response = (client.audience_insights(period=args.period, client_timezone=args.timezone)
                    if args.audience else client.account_insights(period=args.period, include_time_series=True))
        response.save_json(args.output)
    except EditsError as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(f"Raw statistics saved to {args.output}")


if __name__ == "__main__":
    main()
