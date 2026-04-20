import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import BookCollection


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_add_book():
    collection = BookCollection()
    initial_count = len(collection.books)
    collection.add_book("1984", "George Orwell", 1949)
    assert len(collection.books) == initial_count + 1
    book = collection.find_book_by_title("1984")
    assert book is not None
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.read is False

def test_mark_book_as_read():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    result = collection.mark_as_read("Dune")
    assert result is True
    book = collection.find_book_by_title("Dune")
    assert book.read is True

def test_mark_book_as_read_invalid():
    collection = BookCollection()
    result = collection.mark_as_read("Nonexistent Book")
    assert result is False

def test_remove_book():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    result = collection.remove_book("The Hobbit")
    assert result is True
    book = collection.find_book_by_title("The Hobbit")
    assert book is None

def test_remove_book_invalid():
    collection = BookCollection()
    result = collection.remove_book("Nonexistent Book")
    assert result is False


def test_search_title_substr():
    collection = BookCollection()
    collection.add_book('The Great Adventure', 'X', 1999)
    collection.add_book('Small Tale', 'Y', 2001)
    results = collection.search(title_substr='great')
    assert len(results) == 1
    assert results[0].title == 'The Great Adventure'


def test_search_author():
    collection = BookCollection()
    collection.add_book('Book1', 'Alice', 2010)
    collection.add_book('Book2', 'Bob', 2011)
    results = collection.search(author='alice')
    assert len(results) == 1
    assert results[0].author == 'Alice'


def test_search_year_range():
    collection = BookCollection()
    collection.add_book('Old', 'A', 1980)
    collection.add_book('Mid', 'B', 2000)
    collection.add_book('New', 'C', 2020)
    results = collection.search(min_year=1990, max_year=2010)
    titles = {b.title for b in results}
    assert titles == {'Mid'}


def test_search_read_filter():
    collection = BookCollection()
    collection.add_book('R1', 'A', 2000)
    collection.add_book('R2', 'B', 2001)
    collection.mark_as_read('R1')
    read_results = collection.search(read=True)
    unread_results = collection.search(read=False)
    assert len(read_results) == 1 and read_results[0].title == 'R1'
    assert len(unread_results) == 1 and unread_results[0].title == 'R2'


def test_search_combined_filters():
    collection = BookCollection()
    collection.add_book('Special 2005', 'AuthorX', 2005)
    collection.add_book('Special 2015', 'AuthorX', 2015)
    results = collection.search(title_substr='special', author='authorx', min_year=2010)
    assert len(results) == 1
    assert results[0].year == 2015
