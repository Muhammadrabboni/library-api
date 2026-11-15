from datetime import date
from errors import error_response
from utils.validation import is_valid_email, is_valid_member_type
from utils.checks import get_loan_limit

import member_repository


def member_to_dict(member):
    return {
        "id": member[0],
        "name": member[1],
        "email": member[2],
        "type": member[3],
    }


def list_members():
    rows = member_repository.list_members()
    return [member_to_dict(row) for row in rows]


def get_member(member_id):
    member = member_repository.get_member(member_id)

    if member is None:
        return None

    return member_to_dict(member)


def create_member(data):
    if not data.get("name"):
        return error_response("name is required", 400)

    email = str(data.get("email", ""))

    if not is_valid_email(email):
        return error_response("invalid email", 400)

    member_type = data.get("type", "student")

    if not is_valid_member_type(member_type):
        return error_response("type must be student or staff", 400)

    existing = member_repository.get_member_by_email(email)

    if existing is not None:
        return error_response("email already registered", 409)

    member = member_repository.insert_member(
        data["name"],
        email,
        member_type
    )

    return member_to_dict(member), 201


def get_member_loans(member_id):
    member = member_repository.get_member(member_id)

    if member is None:
        return error_response("member not found", 404)

    rows = member_repository.get_member_loans(member_id)

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

    remaining = get_loan_limit(member) - open_loans

    return {
        "loans": loans,
        "total_owed": round(float(owed), 2),
        "loans_remaining": remaining,
    }, 200
