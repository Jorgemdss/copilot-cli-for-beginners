import sys
from books import BookCollection
from utils import print_books


# Global collection instance
collection = BookCollection()


def show_books(books):
    """Delegate book display to utils.print_books for consistent, defensive output."""
    print_books(books)


def handle_list():
    books = collection.list_books()
    show_books(books)


def handle_add():
    print("\nAdd a New Book\n")

    title = input("Title: ").strip()
    author = input("Author: ").strip()
    year_str = input("Year: ").strip()

    try:
        year = int(year_str) if year_str else 0
        collection.add_book(title, author, year)
        print("\nBook added successfully.\n")
    except ValueError as e:
        print(f"\nError: {e}\n")


def handle_remove():
    print("\nRemove a Book\n")

    title = input("Enter the title of the book to remove: ").strip()
    collection.remove_book(title)

    print("\nBook removed if it existed.\n")


def handle_find():
    print("\nFind Books by Author\n")

    author = input("Author name: ").strip()
    books = collection.find_by_author(author)

    show_books(books)


def handle_mark(title=None):
    """Mark a book as read by title. If title is None, prompt the user."""
    print("\nMark a Book as Read\n")

    if not title:
        try:
            title = input("Enter the title of the book to mark as read: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            return

    if not title:
        print("\nTitle is required.\n")
        return

    try:
        success = collection.mark_as_read(title)
        if success:
            print("\nBook marked as read.\n")
        else:
            print("\nBook not found.\n")
    except Exception as e:
        # Avoid exposing internal errors to users
        print("\nAn error occurred while marking the book as read.\n")


def handle_search(argv_title: str = None):
    """Search books using optional CLI args or interactive prompts.

    argv_title: simple positional title substring if provided by argv.
    """
    # If argv provided a title substring, use it as initial criteria
    title = argv_title
    author = None
    min_year = None
    max_year = None
    read = None

    # If no argv criteria provided, prompt interactively
    if not any([title]):
        try:
            title = input("Title substring (optional): ").strip() or None
            author = input("Author (optional): ").strip() or None
            min_year_s = input("Min year (optional): ").strip()
            max_year_s = input("Max year (optional): ").strip()
            read_s = input("Filter by read status? (read/unread/any): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            return

        try:
            min_year = int(min_year_s) if min_year_s else None
        except ValueError:
            print("Invalid min year; ignoring")
            min_year = None

        try:
            max_year = int(max_year_s) if max_year_s else None
        except ValueError:
            print("Invalid max year; ignoring")
            max_year = None

        if read_s == "read":
            read = True
        elif read_s == "unread":
            read = False
        else:
            read = None

    # Perform search
    try:
        books = collection.search(title, author, min_year, max_year, read)
        show_books(books)
    except Exception:
        print("An error occurred while searching the collection.")


def show_help():
    print("""
Book Collection Helper

Commands:
  list     - Show all books
  add      - Add a new book
  remove   - Remove a book by title
  find     - Find books by author
  mark     - Mark a book as read
  search   - Search books with filters (flags: --title, --author, --min-year, --max-year, --read/--unread)
  help     - Show this help message
""")


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "list":
        handle_list()
    elif command == "add":
        handle_add()
    elif command == "remove":
        handle_remove()
    elif command == "find":
        handle_find()
    elif command == "mark":
        # Accept title via argv (join remaining args) or prompt interactively
        title = " ".join(sys.argv[2:]).strip() if len(sys.argv) > 2 else None
        handle_mark(title)
    elif command == "search":
        # Parse simple flags from argv for search
        args = sys.argv[2:]
        title = None
        author = None
        min_year = None
        max_year = None
        read = None
        i = 0
        while i < len(args):
            a = args[i]
            if a in ("--title", "-t") and i + 1 < len(args):
                title = args[i + 1]
                i += 2
            elif a in ("--author", "-a") and i + 1 < len(args):
                author = args[i + 1]
                i += 2
            elif a in ("--min-year",) and i + 1 < len(args):
                try:
                    min_year = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif a in ("--max-year",) and i + 1 < len(args):
                try:
                    max_year = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
            elif a == "--read":
                read = True
                i += 1
            elif a == "--unread":
                read = False
                i += 1
            else:
                # treat as positional title substring
                if title is None:
                    title = a
                else:
                    title = title + " " + a
                i += 1
        # If no flags/positional provided, fall back to interactive prompts
        if not any([title, author, min_year, max_year, read]):
            handle_search()
        else:
            handle_search(title)
    elif command == "help":
        show_help()
    else:
        print("Unknown command.\n")
        show_help()


if __name__ == "__main__":
    main()
