
from errors import error_response
from utils.validation import is_valid_isbn
import book_repository


def book_to_dict(row):
    return {
        "id": row[0],
        "title": row[1],
        "author": row[2],
        "isbn": row[3],
        "available": bool(row[4]),
    }


def list_books(available_only=False):
    rows = book_repository.list_books(available_only)
    return [book_to_dict(row) for row in rows]


def get_book(book_id):
    row = book_repository.get_book(book_id)

    if row is None:
        return None

    return book_to_dict(row)


def create_book(data):
    if not data.get("title") or not data.get("author"):
        return error_response("title and author are required", 400)

    isbn = data.get("isbn")

    if not is_valid_isbn(isbn):
        return error_response("invalid isbn", 400)

    row = book_repository.insert_book(data)

    return book_to_dict(row), 201


def delete_book(book_id):
    row = book_repository.get_book(book_id)

    if row is None:
        return error_response("book not found", 404)

    if row[4] == 0:
        return error_response("book is on loan", 409)

    book_repository.delete_book(book_id)

    return None, 204
