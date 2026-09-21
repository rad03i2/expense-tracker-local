from __future__ import annotations

import csv
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable

MONEY = Decimal("0.01")


class ExpenseError(ValueError):
    pass


def parse_amount(value: str | Decimal) -> int:
    try:
        amount = Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP)
    except InvalidOperation as exc:
        raise ExpenseError("amount must be a valid number") from exc
    if amount <= 0:
        raise ExpenseError("amount must be greater than zero")
    return int(amount * 100)


def parse_date(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ExpenseError("date must use YYYY-MM-DD") from exc


def normalize_currency(value: str) -> str:
    currency = value.strip().upper()
    if len(currency) != 3 or not currency.isalpha():
        raise ExpenseError("currency must be a three-letter code such as USD or IQD")
    return currency


def cents_text(cents: int) -> str:
    return f"{Decimal(cents) / 100:.2f}"


@dataclass(frozen=True)
class Expense:
    id: int
    spent_on: str
    amount_cents: int
    currency: str
    category: str
    merchant: str
    note: str
    created_at: str

    def public(self) -> dict:
        data = asdict(self)
        data["amount"] = cents_text(data.pop("amount_cents"))
        return data


class ExpenseStore:
    def __init__(self, path: Path | str):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS expenses (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          spent_on TEXT NOT NULL,
          amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
          currency TEXT NOT NULL,
          category TEXT NOT NULL,
          merchant TEXT NOT NULL DEFAULT '',
          note TEXT NOT NULL DEFAULT '',
          created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(spent_on);
        CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
        CREATE INDEX IF NOT EXISTS idx_expenses_currency ON expenses(currency);
        """)

    def close(self):
        self.db.close()

    def add(self, *, amount: str, currency: str, category: str, spent_on: str | None = None,
            merchant: str = "", note: str = "") -> Expense:
        category = category.strip()
        if not category or len(category) > 80:
            raise ExpenseError("category is required and must be at most 80 characters")
        merchant, note = merchant.strip(), note.strip()
        if len(merchant) > 160 or len(note) > 1000:
            raise ExpenseError("merchant or note is too long")
        values = (parse_date(spent_on or date.today().isoformat()), parse_amount(amount),
                  normalize_currency(currency), category, merchant, note,
                  datetime.now().astimezone().isoformat(timespec="seconds"))
        cur = self.db.execute("INSERT INTO expenses(spent_on,amount_cents,currency,category,merchant,note,created_at) VALUES(?,?,?,?,?,?,?)", values)
        self.db.commit()
        return self.get(cur.lastrowid)

    def get(self, expense_id: int) -> Expense:
        row = self.db.execute("SELECT * FROM expenses WHERE id=?", (expense_id,)).fetchone()
        if not row:
            raise ExpenseError(f"expense {expense_id} was not found")
        return Expense(**dict(row))

    def list(self, *, currency: str | None = None, category: str | None = None,
             start: str | None = None, end: str | None = None, query: str | None = None) -> list[Expense]:
        where, args = [], []
        if currency:
            where.append("currency=?"); args.append(normalize_currency(currency))
        if category:
            where.append("LOWER(category)=LOWER(?)"); args.append(category.strip())
        if start:
            where.append("spent_on>=?"); args.append(parse_date(start))
        if end:
            where.append("spent_on<=?"); args.append(parse_date(end))
        if start and end and start > end:
            raise ExpenseError("start date cannot be after end date")
        if query:
            where.append("(LOWER(merchant) LIKE ? OR LOWER(note) LIKE ? OR LOWER(category) LIKE ?)")
            token = f"%{query.lower()}%"; args.extend([token, token, token])
        sql = "SELECT * FROM expenses" + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY spent_on DESC,id DESC"
        return [Expense(**dict(row)) for row in self.db.execute(sql, args)]

    def delete(self, expense_id: int) -> None:
        cur = self.db.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        self.db.commit()
        if cur.rowcount != 1:
            raise ExpenseError(f"expense {expense_id} was not found")

    def summary(self, **filters) -> list[dict]:
        expenses = self.list(**filters)
        totals: dict[tuple[str, str], list[int]] = {}
        for item in expenses:
            key = (item.currency, item.category)
            current = totals.setdefault(key, [0, 0]); current[0] += item.amount_cents; current[1] += 1
        return [{"currency": c, "category": cat, "amount": cents_text(v[0]), "count": v[1]}
                for (c, cat), v in sorted(totals.items())]

    def export(self, destination: Path, fmt: str, *, overwrite: bool = False, **filters) -> int:
        destination = destination.expanduser()
        if destination.exists() and not overwrite:
            raise ExpenseError(f"refusing to overwrite {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        rows = [x.public() for x in self.list(**filters)]
        tmp = destination.with_name(destination.name + ".tmp")
        if fmt == "json":
            tmp.write_text(json.dumps({"schema": 1, "expenses": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        elif fmt == "csv":
            fields = ["id", "spent_on", "amount", "currency", "category", "merchant", "note", "created_at"]
            with tmp.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
        else:
            raise ExpenseError("format must be json or csv")
        tmp.replace(destination)
        return len(rows)
