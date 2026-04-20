from typing import List, Tuple, Any, Optional


def print_menu() -> None:
    """Print the main menu. Falls back to a simpler display on failure."""
    try:
        print("\n📚 Book Collection App")
        print("1. Add a book")
        print("2. List books")
        print("3. Mark book as read")
        print("4. Remove a book")
        print("5. Exit")
    except Exception:
        # Fallback in case of terminal/encoding issues
        print("\nBook Collection App")
        print("1. Add a book")
        print("2. List books")
        print("3. Mark book as read")
        print("4. Remove a book")
        print("5. Exit")


def get_user_choice(valid_choices: Optional[List[str]] = None) -> str:
    """Prompt the user for a menu choice and validate it.

    Returns a valid choice string from valid_choices. On Ctrl-C/EOF returns '5' (Exit).
    """
    if valid_choices is None:
        valid_choices = ["1", "2", "3", "4", "5"]

    while True:
        try:
            choice = input("Choose an option (1-5): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled. Exiting.")
            return "5"

        # Basic validation: ensure input is provided and numeric
        if not choice:
            print("No input provided. Please enter a number.")
            continue

        if not choice.isdigit():
            print("Invalid input. Please enter a number (e.g., 1, 2, 3).")
            continue

        if choice in valid_choices:
            return choice

        # If numeric but not an allowed option, give clearer feedback
        print(f"Invalid choice. Please enter one of: {', '.join(valid_choices)}")


def get_book_details() -> Tuple[str, str, Optional[int]]:
    """Prompt the user interactively for book details with validation and retry limits.

    Behavior and prompts:
    - title (required): prompts for a non-empty title. The user has up to ``max_attempts`` attempts
      (default 3) to provide a non-empty value. If the user cancels input (Ctrl-C/EOF) or exceeds the
      attempt limit, the function prints a cancellation message and returns the cancelled sentinel
      values described below.
    - author (required): same behavior as title (up to ``max_attempts`` retries, cancellation handled).
    - year (optional): prompts for a publication year. If provided, the input is parsed to an int and
      validated against a sane range (0..2100). If parsing fails or the year is out of range, the
      year is treated as omitted (None) and a warning is printed.

    Return value:
    A tuple (title, author, year_or_None) with types (str, str, Optional[int]).
    - title: non-empty string when successfully provided; empty string "" if input was cancelled or
      the function aborted due to repeated empty attempts.
    - author: non-empty string when successfully provided; empty string "" if input was cancelled or
      the function aborted due to repeated empty attempts.
    - year_or_None: integer year when provided and valid; ``None`` when omitted, invalid, out-of-range,
      or when input was cancelled.

    Notes:
    - The function handles EOFError and KeyboardInterrupt internally and does not raise them to callers.
    - ``max_attempts`` is defined locally (3) and limits how many times the user can submit an empty
      title/author before the routine gives up and returns cancelled values.
    """
    max_attempts = 3

    # Title (required) with limited retries
    try:
        title = input("Enter book title: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
        return "", "", None

    attempts = 0
    while not title:
        attempts += 1
        if attempts >= max_attempts:
            print("Too many empty attempts. Cancelling book entry.")
            return "", "", None
        try:
            title = input("Title is required. Enter book title: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            return "", "", None

    # Author (required) with limited retries
    try:
        author = input("Enter author: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
        return title, "", None

    attempts = 0
    while not author:
        attempts += 1
        if attempts >= max_attempts:
            print("Too many empty attempts for author. Cancelling book entry.")
            return "", "", None
        try:
            author = input("Author is required. Enter author: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            return "", "", None

    # Year (optional) with validation
    try:
        year_input = input("Enter publication year (optional): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
        return title, author, None

    year: Optional[int] = None
    if year_input:
        try:
            year = int(year_input)
            # Basic sanity checks for year
            if year < 0 or year > 2100:
                print("Unrealistic year entered; leaving year blank.")
                year = None
        except ValueError:
            print("Invalid year entered; leaving year blank.")
            year = None

    return title, author, year


def print_books(books: List[Any]) -> None:
    """Print a list of books defensively. Accepts dicts or objects.

    Malformed entries are skipped with a placeholder message.
    """
    if not books:
        print("No books in your collection.")
        return

    print("\nYour Books:")
    for index, book in enumerate(books, start=1):
        try:
            if isinstance(book, dict):
                title = book.get("title", "Untitled")
                author = book.get("author", "Unknown")
                year = book.get("year", "?")
                read = bool(book.get("read", False))
            else:
                title = getattr(book, "title", "Untitled")
                author = getattr(book, "author", "Unknown")
                year = getattr(book, "year", "?")
                read = bool(getattr(book, "read", False))

            status = "Read" if read else "Unread"
            print(f"{index}. {title} by {author} ({year}) - {status}")
        except Exception:
            # Skip malformed book but continue listing the rest
            print(f"{index}. <Invalid book entry>")
            continue


def get_search_criteria() -> dict:
    """Prompt the user for search criteria and return a dict of filters."""
    try:
        title = input("Title substring (optional): ").strip() or None
        author = input("Author name (optional): ").strip() or None
        min_year_s = input("Min year (optional): ").strip()
        max_year_s = input("Max year (optional): ").strip()
        read_s = input("Filter by read status? (read/unread/any): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
        return {}

    min_year = None
    max_year = None
    try:
        min_year = int(min_year_s) if min_year_s else None
    except ValueError:
        print("Invalid min year; ignored")
    try:
        max_year = int(max_year_s) if max_year_s else None
    except ValueError:
        print("Invalid max year; ignored")

    if read_s == "read":
        read = True
    elif read_s == "unread":
        read = False
    else:
        read = None

    return {"title": title, "author": author, "min_year": min_year, "max_year": max_year, "read": read}
