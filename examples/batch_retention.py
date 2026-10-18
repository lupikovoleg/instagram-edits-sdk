"""Live: a bounded list of owned Reel URLs, one request per line, stop on failure."""
import argparse
from pathlib import Path
import time
from edits_api import EditsClient, EditsError, media_id


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("list", type=Path, help="UTF-8 file with one owned Reel URL/ID per line")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--delay", type=float, default=3)
    args = parser.parse_args()
    if args.delay < 2:
        parser.error("Use a delay of at least two seconds; this is not a server rate-limit guarantee.")
    try:
        reels = [line.strip() for line in args.list.read_text().splitlines() if line.strip()]
        # Validate all identifiers and duplicate output names before the first request.
        pks = [media_id(reel) for reel in reels]
        if len(pks) != len(set(pks)):
            parser.error("Duplicate media IDs in input list")
        if any((args.output / pk).exists() for pk in pks):
            parser.error("One or more output directories already exist")
        client = EditsClient.from_env()
        for i, (reel, pk) in enumerate(zip(reels, pks)):
            if i:
                time.sleep(args.delay)
            result = client.reel_insights(reel)
            result.export(args.output / pk)
            print(f"{pk}: {len(result.retention)} points")
    except EditsError as exc:
        parser.exit(1, f"Stopped without retrying: {exc}\n")


if __name__ == "__main__":
    main()
