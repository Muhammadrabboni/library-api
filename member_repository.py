
import sqlite3


DB_NAME = "library.db"


def list_members():
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT * FROM members").fetchall()
    conn.close()
    return rows


def get_member(member_id):
    conn = sqlite3.connect(DB_NAME)

    member = conn.execute(
        "SELECT * FROM members WHERE id = ?",
        (member_id,)
    ).fetchone()

    conn.close()
    return member


def get_member_by_email(email):
    conn = sqlite3.connect(DB_NAME)

    member = conn.execute(
        "SELECT * FROM members WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()
    return member


def insert_member(name, email, member_type):
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.execute(
        "INSERT INTO members (name, email, type) VALUES (?, ?, ?)",
        (name, email, member_type),
    )

    conn.commit()

    member = conn.execute(
        "SELECT * FROM members WHERE id = ?",
        (cursor.lastrowid,)
    ).fetchone()

    conn.close()
    return member


def get_member_loans(member_id):
    conn = sqlite3.connect(DB_NAME)

    rows = conn.execute(
        "SELECT * FROM loans WHERE member_id = ?",
        (member_id,)
    ).fetchall()

    conn.close()
    return rows
