"""Fetch the alternative Instagram insights branch using the tested APK version."""
import argparse
from edits_api import EditsClient, EditsError

# Explicit version from APK 448.0.0.53.84; future server versions may require a change.
BLOKS_VERSION = "8dc50e9193c9b70a3f9dbcc25fc5f444bbac27bb56a8c1359ede836b8069c4b8"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reel")
    parser.add_argument("--bloks-version", default=BLOKS_VERSION)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        result = EditsClient.from_env().extended_reel_insights(
            args.reel, bloks_versioning_id=args.bloks_version)
        insights = result.get_data("ig_reel_insights")
        curve = insights.get("retention", {}).get("retention_curve") if insights else None
        result.save_json(args.output)
        print(f"Saved response; retention points: {len(curve) if curve else 0}")
    except EditsError as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
