
import sqlite3


def list_books(available_only=False):
    conn = sqlite3.connect("library.db")

    if available_only:
        rows = conn.execute(
            "SELECT * FROM books WHERE available = 1"
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM books").fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "author": row[2],
            "isbn": row[3],
            "available": bool(row[4]),
        }
        for row in rows
    ]


def get_book(book_id):
    conn = sqlite3.connect("library.db")
    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "author": row[2],
        "isbn": row[3],
        "available": bool(row[4]),
    }


def create_book(data):
    if not data.get("title") or not data.get("author"):
        return {"error": "title and author are required"}, 400

    isbn = data.get("isbn")
    digits = str(isbn).replace("-", "")

    if not digits.isdigit() or len(digits) not in (10, 13):
        return {"error": "invalid isbn"}, 400

    conn = sqlite3.connect("library.db")

    cursor = conn.execute(
        """
        INSERT INTO books (title, author, isbn, available)
        VALUES (?, ?, ?, 1)
        """,
        (data["title"], data["author"], data["isbn"]),
    )

    conn.commit()

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (cursor.lastrowid,)
    ).fetchone()

    conn.close()

    book = {
        "id": row[0],
        "title": row[1],
        "author": row[2],
        "isbn": row[3],
        "available": bool(row[4]),
    }

    return book, 201


def delete_book(book_id):
    conn = sqlite3.connect("library.db")

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if row is None:
        conn.close()
        return {"error": "book not found"}, 404

    if row[4] == 0:
        conn.close()
        return {"error": "book is on loan"}, 409

    conn.execute(
        "DELETE FROM books WHERE id = ?",
        (book_id,)
    )

    conn.commit()
    conn.close()

    return None, 204
