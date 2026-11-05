import argparse
import json
import sys
from datapulse.database import ingest_csv, list_tables
from datapulse.profiling import profile_csv
from datapulse.validation import validate_csv
from datapulse.sql_guard import execute_readonly
from datapulse.nl2sql import ask

def main():
    parser = argparse.ArgumentParser(prog="datapulse", description="DataPulse data analytics and safe AI SQL")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("profile"); p.add_argument("file")
    p = sub.add_parser("validate"); p.add_argument("file")
    p = sub.add_parser("ingest"); p.add_argument("file"); p.add_argument("--table")
    sub.add_parser("tables")
    p = sub.add_parser("query"); p.add_argument("sql")
    p = sub.add_parser("ask"); p.add_argument("question")
    args = parser.parse_args()
    try:
        if args.command == "profile": print(json.dumps(profile_csv(args.file), indent=2, default=str))
        elif args.command == "validate":
            r = validate_csv(args.file)
            print(f"Rows: {r['total_rows']} | valid: {r['valid_rows']} | rejected: {r['rejected_rows']}")
            if not r["rejected"].empty: print(r["rejected"].to_string(index=False))
        elif args.command == "ingest": print(json.dumps(ingest_csv(args.file, args.table), indent=2))
        elif args.command == "tables": print(json.dumps(list_tables(), indent=2))
        elif args.command == "query": print(json.dumps(execute_readonly(args.sql), indent=2, default=str))
        elif args.command == "ask": print(json.dumps(ask(args.question), indent=2, default=str))
    except Exception as exc:
        print(f"DataPulse error: {exc}", file=sys.stderr)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
