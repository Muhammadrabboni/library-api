import db


def list_loans():
    conn = db.connect()
    rows = conn.execute("SELECT * FROM loans").fetchall()
    conn.close()
    return rows


def get_loan(loan_id):
    conn = db.connect()

    loan = conn.execute(
        "SELECT * FROM loans WHERE id = ?",
        (loan_id,),
    ).fetchone()

    conn.close()
    return loan


def get_book(book_id):
    conn = db.connect()

    book = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,),
    ).fetchone()

    conn.close()
    return book


def get_member(member_id):
    conn = db.connect()

    member = conn.execute(
        "SELECT * FROM members WHERE id = ?",
        (member_id,),
    ).fetchone()

    conn.close()
    return member


def get_member_loans(member_id):
    conn = db.connect()

    rows = conn.execute(
        "SELECT * FROM loans WHERE member_id = ?",
        (member_id,),
    ).fetchall()

    conn.close()
    return rows


def create_loan(data, due_date, checked_out):
    conn = db.connect()

    cursor = conn.execute(
        """
        INSERT INTO loans (book_id, member_id, due_date, checked_out)
        VALUES (?, ?, ?, ?)
        """,
        (data["book_id"], data["member_id"], due_date, checked_out),
    )

    conn.execute(
        "UPDATE books SET available = 0 WHERE id = ?",
        (data["book_id"],),
    )

    conn.commit()

    loan = conn.execute(
        "SELECT * FROM loans WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()

    conn.close()
    return loan


def return_loan(loan_id, book_id, fine):
    conn = db.connect()

    conn.execute(
        "UPDATE loans SET returned = 1, fine = ? WHERE id = ?",
        (fine, loan_id),
    )

    conn.execute(
        "UPDATE books SET available = 1 WHERE id = ?",
        (book_id,),
    )

    conn.commit()
    conn.close()


def renew_loan(loan_id, new_due_date):
    conn = db.connect()

    conn.execute(
        """
        UPDATE loans
        SET due_date = ?, renewals = renewals + 1
        WHERE id = ?
        """,
        (new_due_date, loan_id),
    )

    conn.commit()
    conn.close()


def pay_fine(loan_id):
    conn = db.connect()

    conn.execute(
        "UPDATE loans SET fine_paid = 1 WHERE id = ?",
        (loan_id,),
    )

    conn.commit()
    conn.close()