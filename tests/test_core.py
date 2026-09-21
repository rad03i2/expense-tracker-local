from pathlib import Path
import json
import pytest
from expense_tracker.core import ExpenseError, ExpenseStore, parse_amount


def test_amount_validation():
    assert parse_amount("12.345") == 1235
    with pytest.raises(ExpenseError): parse_amount("0")
    with pytest.raises(ExpenseError): parse_amount("oops")


def test_crud_filters_and_summary(tmp_path):
    store = ExpenseStore(tmp_path / "db.sqlite")
    a = store.add(amount="10.50", currency="usd", category="Food", spent_on="2026-09-01", merchant="Cafe")
    store.add(amount="20", currency="USD", category="Food", spent_on="2026-09-02", merchant="Market")
    store.add(amount="1000", currency="IQD", category="Transport", spent_on="2026-09-03")
    assert store.get(a.id).merchant == "Cafe"
    assert len(store.list(currency="USD")) == 2
    assert len(store.list(query="cafe")) == 1
    summary = store.summary(currency="USD")
    assert summary == [{"currency":"USD", "category":"Food", "amount":"30.50", "count":2}]
    store.delete(a.id)
    with pytest.raises(ExpenseError): store.get(a.id)
    store.close()


def test_export_and_overwrite_guard(tmp_path):
    store = ExpenseStore(tmp_path / "db.sqlite")
    store.add(amount="5", currency="EUR", category="Books", spent_on="2026-09-01")
    out = tmp_path / "expenses.json"
    assert store.export(out, "json") == 1
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema"] == 1 and payload["expenses"][0]["amount"] == "5.00"
    with pytest.raises(ExpenseError): store.export(out, "json")
    store.close()


def test_date_range_validation(tmp_path):
    store = ExpenseStore(tmp_path / "db.sqlite")
    with pytest.raises(ExpenseError): store.list(start="2026-10-01", end="2026-09-01")
    store.close()
