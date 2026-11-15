
import re
import sqlite3
from datetime import date


def list_members():
    conn = sqlite3.connect("library.db")
    rows = conn.execute("SELECT * FROM members").fetchall()
    conn.close()

    return [
        {"id": r[0], "name": r[1], "email": r[2], "type": r[3]}
        for r in rows
    ]


def get_member(member_id):
    conn = sqlite3.connect("library.db")
    member = conn.execute(
        "SELECT * FROM members WHERE id = ?", (member_id,)
    ).fetchone()
    conn.close()

    if member is None:
        return None

    return {
        "id": member[0],
        "name": member[1],
        "email": member[2],
        "type": member[3],
    }


def create_member(data):
    if not data.get("name"):
        return {"error": "name is required"}, 400

    email = str(data.get("email", ""))
    if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is None:
        return {"error": "invalid email"}, 400

    member_type = data.get("type", "student")
    if member_type not in ("student", "staff"):
        return {"error": "type must be student or staff"}, 400

    conn = sqlite3.connect("library.db")

    existing = conn.execute(
        "SELECT * FROM members WHERE email = ?", (email,)
    ).fetchone()

    if existing is not None:
        conn.close()
        return {"error": "email already registered"}, 409

    cur = conn.execute(
        "INSERT INTO members (name, email, type) VALUES (?, ?, ?)",
        (data["name"], email, member_type),
    )
    conn.commit()

    member = conn.execute(
        "SELECT * FROM members WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    conn.close()

    return {
        "id": member[0],
        "name": member[1],
        "email": member[2],
        "type": member[3],
    }, 201


def get_member_loans(member_id):
    conn = sqlite3.connect("library.db")

    member = conn.execute(
        "SELECT * FROM members WHERE id = ?", (member_id,)
    ).fetchone()

    if member is None:
        conn.close()
        return {"error": "member not found"}, 404

    rows = conn.execute(
        "SELECT * FROM loans WHERE member_id = ?", (member_id,)
    ).fetchall()
    conn.close()

    owed = 0
    open_loans = 0
    loans = []

    for loan in rows:
        if loan[4] == 0:
            open_loans += 1
            days_late = (date.today() - date.fromisoformat(loan[3])).days

            if days_late > 0:
                owed += days_late * 0.5

        elif loan[6] == 0:
            owed += loan[5]

        loans.append({
            "id": loan[0],
            "book_id": loan[1],
            "due_date": loan[3],
            "returned": bool(loan[4]),
            "fine": round(float(loan[5]), 2),
            "fine_paid": bool(loan[6]),
        })

    if member[3] == "staff":
        remaining = 5 - open_loans
    else:
        remaining = 3 - open_loans

    return {
        "loans": loans,
        "total_owed": round(float(owed), 2),
        "loans_remaining": remaining,
    }, 200
