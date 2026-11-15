
import sqlite3
from datetime import date, timedelta


DB_NAME = "library.db"
DAILY_FINE = 0.50
LOAN_PERIOD = 14


def money(value):
    return round(float(value), 2)


def is_valid_date(value):
    try:
        date.fromisoformat(str(value))
        return True
    except ValueError:
        return False


def loan_to_dict(loan, include_current_fine=False):
    result = {
        "id": loan[0],
        "book_id": loan[1],
        "member_id": loan[2],
        "due_date": loan[3],
        "returned": bool(loan[4]),
        "fine": money(loan[5]),
        "fine_paid": bool(loan[6]),
        "renewals": loan[7],
        "checked_out": loan[8],
    }

    if include_current_fine:
        current_fine = loan[5]

        if loan[4] == 0:
            days_late = (date.today() - date.fromisoformat(loan[3])).days
            current_fine = max(0, days_late) * DAILY_FINE

        result["current_fine"] = money(current_fine)

    return result


def write_notification(email, subject, body):
    with open("outbox.txt", "a") as file:
        file.write(
            f"TO: {email} | SUBJECT: {subject} | BODY: {body}\n"
        )


def list_loans(overdue_only=False):
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT * FROM loans").fetchall()
    conn.close()

    result = []

    for loan in rows:
        current_fine = loan[5]
        days_late = (date.today() - date.fromisoformat(loan[3])).days

        if loan[4] == 0:
            current_fine = max(0, days_late) * DAILY_FINE

        if overdue_only and (loan[4] == 1 or days_late <= 0):
            continue

        item = loan_to_dict(loan, include_current_fine=True)
        result.append(item)

    return result


def get_loan(loan_id):
    conn = sqlite3.connect(DB_NAME)
    loan = conn.execute(
        "SELECT * FROM loans WHERE id = ?", (loan_id,)
    ).fetchone()
    conn.close()

    if loan is None:
        return {"error": "loan not found"}, 404

    return loan_to_dict(loan, include_current_fine=True), 200


def create_loan(data):
    if not data.get("book_id") or not data.get("member_id"):
        return {"error": "book_id and member_id are required"}, 400

    if data.get("due_date") and not is_valid_date(data["due_date"]):
        return {"error": "invalid due_date"}, 400

    conn = sqlite3.connect(DB_NAME)

    book = conn.execute(
        "SELECT * FROM books WHERE id = ?", (data["book_id"],)
    ).fetchone()

    if book is None:
        conn.close()
        return {"error": "book not found"}, 404

    member = conn.execute(
        "SELECT * FROM members WHERE id = ?", (data["member_id"],)
    ).fetchone()

    if member is None:
        conn.close()
        return {"error": "member not found"}, 404

    if book[4] == 0:
        conn.close()
        return {"error": "book is not available"}, 409

    rows = conn.execute(
        "SELECT * FROM loans WHERE member_id = ?", (data["member_id"],)
    ).fetchall()

    owed = 0
    open_loans = 0

    for loan in rows:
        if loan[4] == 0:
            open_loans += 1
            days_late = (date.today() - date.fromisoformat(loan[3])).days

            if days_late > 0:
                owed += days_late * DAILY_FINE
        elif loan[6] == 0:
            owed += loan[5]

    if owed > 0:
        conn.close()
        return {"error": "member has unpaid fines"}, 409

    limit = 5 if member[3] == "staff" else 3

    if open_loans >= limit:
        conn.close()
        return {"error": "loan limit reached"}, 409

    today = date.today()
    due_date = data.get("due_date") or (
        today + timedelta(days=LOAN_PERIOD)
    ).isoformat()

    cursor = conn.execute(
        """
        INSERT INTO loans (book_id, member_id, due_date, checked_out)
        VALUES (?, ?, ?, ?)
        """,
        (data["book_id"], data["member_id"], due_date, today.isoformat()),
    )

    conn.execute(
        "UPDATE books SET available = 0 WHERE id = ?",
        (data["book_id"],),
    )

    conn.commit()

    loan = conn.execute(
        "SELECT * FROM loans WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()

    conn.close()

    write_notification(
        member[2],
        "Book checked out",
        "You checked out " + book[1],
    )

    return loan_to_dict(loan), 201


def return_book(loan_id):
    conn = sqlite3.connect(DB_NAME)

    loan = conn.execute(
        "SELECT * FROM loans WHERE id = ?", (loan_id,)
    ).fetchone()

    if loan is None:
        conn.close()
        return {"error": "loan not found"}, 404

    if loan[4] == 1:
        conn.close()
        return {"error": "loan already returned"}, 409

    days_late = (date.today() - date.fromisoformat(loan[3])).days
    fine = max(0, days_late) * DAILY_FINE

    conn.execute(
        "UPDATE loans SET returned = 1, fine = ? WHERE id = ?",
        (fine, loan_id),
    )

    conn.execute(
        "UPDATE books SET available = 1 WHERE id = ?",
        (loan[1],),
    )

    conn.commit()

    member = conn.execute(
        "SELECT * FROM members WHERE id = ?", (loan[2],)
    ).fetchone()

    book = conn.execute(
        "SELECT * FROM books WHERE id = ?", (loan[1],)
    ).fetchone()

    updated = conn.execute(
        "SELECT * FROM loans WHERE id = ?", (loan_id,)
    ).fetchone()

    conn.close()

    write_notification(
        member[2],
        "Book returned",
        "You returned " + book[1] + ". Fine: $" + str(money(fine)),
    )

    return loan_to_dict(updated), 200


def renew_loan(loan_id):
    conn = sqlite3.connect(DB_NAME)

    loan = conn.execute(
        "SELECT * FROM loans WHERE id = ?", (loan_id,)
    ).fetchone()

    if loan is None:
        conn.close()
        return {"error": "loan not found"}, 404

    if loan[4] == 1:
        conn.close()
        return {"error": "loan already returned"}, 409

    if date.fromisoformat(loan[3]) < date.today():
        conn.close()
        return {"error": "overdue loans cannot be renewed"}, 409

    if loan[7] >= 1:
        conn.close()
        return {"error": "loan was already renewed"}, 409

    new_due_date = (
        date.fromisoformat(loan[3]) + timedelta(days=LOAN_PERIOD)
    ).isoformat()

    conn.execute(
        """
        UPDATE loans
        SET due_date = ?, renewals = renewals + 1
        WHERE id = ?
        """,
        (new_due_date, loan_id),
    )

    conn.commit()

    member = conn.execute(
        "SELECT * FROM members WHERE id = ?", (loan[2],)
    ).fetchone()

    book = conn.execute(
        "SELECT * FROM books WHERE id = ?", (loan[1],)
    ).fetchone()

    updated = conn.execute(
        "SELECT * FROM loans WHERE id = ?", (loan_id,)
    ).fetchone()

    conn.close()

    write_notification(
        member[2],
        "Loan renewed",
        "You renewed " + book[1],
    )

    return loan_to_dict(updated), 200


def pay_fine(loan_id):
    conn = sqlite3.connect(DB_NAME)

    loan = conn.execute(
        "SELECT * FROM loans WHERE id = ?", (loan_id,)
    ).fetchone()

    if loan is None:
        conn.close()
        return {"error": "loan not found"}, 404

    if loan[4] == 0:
        conn.close()
        return {"error": "return the book before paying"}, 409

    if loan[5] <= 0 or loan[6] == 1:
        conn.close()
        return {"error": "no fine to pay"}, 409

    conn.execute(
        "UPDATE loans SET fine_paid = 1 WHERE id = ?", (loan_id,)
    )
    conn.commit()

    member = conn.execute(
        "SELECT * FROM members WHERE id = ?", (loan[2],)
    ).fetchone()

    updated = conn.execute(
        "SELECT * FROM loans WHERE id = ?", (loan_id,)
    ).fetchone()

    conn.close()

    write_notification(
        member[2],
        "Fine paid",
        "We received $" + str(money(loan[5])),
    )

    return loan_to_dict(updated), 200
