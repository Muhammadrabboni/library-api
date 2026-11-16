import db


def list_books(available_only=False):
    conn = db.connect()

    if available_only:
        rows = conn.execute(
            "SELECT * FROM books WHERE available = 1"
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM books").fetchall()

    conn.close()
    return rows


def get_book(book_id):
    conn = db.connect()

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,),
    ).fetchone()

    conn.close()
    return row


def insert_book(data):
    conn = db.connect()

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
        (cursor.lastrowid,),
    ).fetchone()

    conn.close()
    return row


def delete_book(book_id):
    conn = db.connect()

    conn.execute(
        "DELETE FROM books WHERE id = ?",
        (book_id,),
    )

    conn.commit()
    conn.close()


def count_books():
    conn = db.connect()

    total = conn.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    conn.close()
    return total