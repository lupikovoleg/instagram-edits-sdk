"""CLI wrapper around the same importable client used by backends."""
import argparse
import json
from pathlib import Path
import sys

from . import EditsClient, EditsError, Session, list_operations
from ._wire import private_write


def main(argv=None):
    parser = argparse.ArgumentParser(prog="edits-api")
    sub = parser.add_subparsers(dest="command", required=True)
    catalog = sub.add_parser("catalog", help="List catalog entries without authentication or network")
    catalog.add_argument("--all", action="store_true", help="Include shared Instagram operations")
    retention = sub.add_parser("retention", help="Fetch and export one owned Reel")
    retention.add_argument("media")
    retention.add_argument("--output", type=Path, required=True)
    insights = sub.add_parser("insights", help="Fetch Reel statistics even when retention is unavailable")
    insights.add_argument("media")
    insights.add_argument("--output", type=Path, required=True)
    query = sub.add_parser("request", help="Execute a named, versioned operation")
    query.add_argument("operation")
    query.add_argument("--variables", type=Path, required=True, help="Path to a JSON object")
    query.add_argument("--output", type=Path, required=True, help="New private JSON output file")
    query.add_argument("--allow-mutation", action="store_true")
    for command in (retention, insights, query):
        command.add_argument("--session", type=Path, help="Settings JSON; '-' reads stdin; default uses environment")
        command.add_argument("--host", choices=("i.instagram.com", "b.i.instagram.com"), default="i.instagram.com")
        command.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args(argv)
    try:
        if args.command == "catalog":
            print(json.dumps(list_operations(edits_only=not args.all), ensure_ascii=False, indent=2))
            return 0
        session = Session.from_settings(args.session) if args.session else Session.from_env()
        client = EditsClient(session, host=args.host, timeout=args.timeout)
        if args.command in ("retention", "insights"):
            result = client.reel_insights(args.media)
            if args.command == "retention" and not result.retention_available:
                raise EditsError("Retention is unavailable; use the insights command for the other metrics.")
            result.export(args.output)
            print(f"Saved {len(result.retention)} retention points to {args.output}" if result.retention_available
                  else f"Saved statistics to {args.output}; retention is unavailable.")
        else:
            variables = json.loads(args.variables.read_text(encoding="utf-8"))
            result = client.execute(args.operation, variables, allow_mutation=args.allow_mutation)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            private_write(args.output, json.dumps(result.payload, ensure_ascii=False, indent=2, allow_nan=False))
            print(f"Saved response from {result.operation} to {args.output}")
        return 0
    except (EditsError, OSError, ValueError) as exc:
        # Do not print OS filenames, raw JSON bodies or secret-containing parse errors.
        message = str(exc) if isinstance(exc, EditsError) else "Invalid input or file operation failed."
        print(f"Error: {message}", file=sys.stderr)
        return 1
