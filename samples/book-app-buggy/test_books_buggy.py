import importlib.util
import json
from pathlib import Path
import pytest


def _load_module():
    """Dynamically load the books_buggy module from the same directory as this test."""
    module_path = Path(__file__).parent / "books_buggy.py"
    spec = importlib.util.spec_from_file_location("books_buggy", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_add_valid_book_and_persists(tmp_path):
    mod = _load_module()
    # isolate data file
    datafile = tmp_path / "data.json"
    mod.DATA_FILE = str(datafile)

    bc = mod.BookCollection()
    book = bc.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

    assert book in bc.books
    assert book.title == "The Hobbit"
    assert book.author == "J.R.R. Tolkien"
    assert book.year == 1937

    # persisted to JSON
    raw = json.loads(datafile.read_text())
    assert isinstance(raw, list)
    assert raw[0]["title"] == "The Hobbit"


def test_add_negative_and_future_year_are_accepted(tmp_path):
    mod = _load_module()
    datafile = tmp_path / "data.json"
    mod.DATA_FILE = str(datafile)

    bc = mod.BookCollection()
    neg = bc.add_book("Ancient Tome", "Unknown", -400)
    future = bc.add_book("Future Release", "SciFi", 3000)

    assert neg in bc.books and neg.year == -400
    assert future in bc.books and future.year == 3000

    raw = json.loads(datafile.read_text())
    titles = [r["title"] for r in raw]
    assert "Ancient Tome" in titles
    assert "Future Release" in titles


def test_adding_duplicate_titles_creates_multiple_entries(tmp_path):
    mod = _load_module()
    datafile = tmp_path / "data.json"
    mod.DATA_FILE = str(datafile)

    bc = mod.BookCollection()
    b1 = bc.add_book("Dune", "Frank Herbert", 1965)
    b2 = bc.add_book("Dune", "Frank Herbert", 1965)

    # both entries exist
    matches = [b for b in bc.books if b.title == "Dune"]
    assert len(matches) == 2

    raw = json.loads(datafile.read_text())
    dune_count = sum(1 for r in raw if r["title"] == "Dune")
    assert dune_count == 2


def test_non_int_year_is_not_type_checked(tmp_path):
    """Checks that the current implementation does not enforce year type."""
    mod = _load_module()
    datafile = tmp_path / "data.json"
    mod.DATA_FILE = str(datafile)

    bc = mod.BookCollection()
    b = bc.add_book("Loose Typing", "Tester", "two thousand")

    # current behavior: year is stored as-provided (no validation)
    assert b.year == "two thousand"
    raw = json.loads(datafile.read_text())
    assert raw[0]["year"] == "two thousand"
