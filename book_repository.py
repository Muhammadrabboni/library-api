
import sqlite3


DB_NAME = "library.db"


def list_books(available_only=False):
    conn = sqlite3.connect(DB_NAME)

    if available_only:
        rows = conn.execute(
            "SELECT * FROM books WHERE available = 1"
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM books").fetchall()

    conn.close()
    return rows


def get_book(book_id):
    conn = sqlite3.connect(DB_NAME)

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    conn.close()
    return row


def insert_book(data):
    conn = sqlite3.connect(DB_NAME)

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
    return row


def delete_book(book_id):
    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        "DELETE FROM books WHERE id = ?",
        (book_id,)
    )

    conn.commit()
    conn.close()
