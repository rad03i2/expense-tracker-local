from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from . import __version__
from .core import ExpenseError, ExpenseStore


def default_db() -> Path:
    override = os.environ.get("EXPENSE_TRACKER_DB")
    if override:
        return Path(override)
    return Path.home() / ".expense-tracker-local" / "expenses.sqlite3"


def filters(parser):
    parser.add_argument("--currency")
    parser.add_argument("--category")
    parser.add_argument("--start", help="YYYY-MM-DD")
    parser.add_argument("--end", help="YYYY-MM-DD")
    parser.add_argument("--query", help="search merchant, category, and note")


def build_parser():
    p = argparse.ArgumentParser(prog="expense-tracker", description="Private local expense tracking")
    p.add_argument("--db", type=Path, default=default_db())
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__} — Radwan Abdulhadi Ahmed / @rad03i2")
    sub = p.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="record an expense")
    add.add_argument("amount"); add.add_argument("--currency", default="USD"); add.add_argument("--category", required=True)
    add.add_argument("--date", dest="spent_on"); add.add_argument("--merchant", default=""); add.add_argument("--note", default="")
    ls = sub.add_parser("list", help="list/search expenses"); filters(ls); ls.add_argument("--json", action="store_true")
    show = sub.add_parser("show"); show.add_argument("id", type=int)
    delete = sub.add_parser("delete"); delete.add_argument("id", type=int); delete.add_argument("--yes", action="store_true")
    summary = sub.add_parser("summary", help="totals by currency and category"); filters(summary); summary.add_argument("--json", action="store_true")
    export = sub.add_parser("export"); export.add_argument("destination", type=Path); export.add_argument("--format", choices=("json", "csv"), default="csv"); export.add_argument("--overwrite", action="store_true"); filters(export)
    return p


def kwargs(args):
    return {k: getattr(args, k) for k in ("currency", "category", "start", "end", "query") if hasattr(args, k)}


def main(argv=None):
    args = build_parser().parse_args(argv)
    store = ExpenseStore(args.db)
    try:
        if args.command == "add":
            item = store.add(amount=args.amount, currency=args.currency, category=args.category, spent_on=args.spent_on, merchant=args.merchant, note=args.note)
            print(json.dumps(item.public(), ensure_ascii=False))
        elif args.command == "show":
            print(json.dumps(store.get(args.id).public(), ensure_ascii=False, indent=2))
        elif args.command == "list":
            rows = [x.public() for x in store.list(**kwargs(args))]
            if args.json: print(json.dumps(rows, ensure_ascii=False, indent=2))
            elif not rows: print("No expenses found.")
            else:
                for x in rows: print(f"{x['id']:>4}  {x['spent_on']}  {x['amount']:>12} {x['currency']}  {x['category']}  {x['merchant']}")
        elif args.command == "summary":
            rows = store.summary(**kwargs(args))
            if args.json: print(json.dumps(rows, ensure_ascii=False, indent=2))
            elif not rows: print("No expenses found.")
            else:
                for x in rows: print(f"{x['currency']}  {x['category']}: {x['amount']} ({x['count']})")
        elif args.command == "delete":
            if not args.yes: raise ExpenseError("deletion requires --yes")
            store.delete(args.id); print(f"Deleted expense {args.id}.")
        elif args.command == "export":
            count = store.export(args.destination, args.format, overwrite=args.overwrite, **kwargs(args)); print(f"Exported {count} expense(s) to {args.destination}.")
        return 0
    except ExpenseError as exc:
        print(f"error: {exc}", file=__import__("sys").stderr); return 2
    finally:
        store.close()

if __name__ == "__main__":
    raise SystemExit(main())
