from datetime import date, timedelta
from utils.validation import is_valid_date
import loan_repository
from utils.fines import money, calculate_days_late, calculate_fine
from utils.checks import (
    is_book_available,
    is_loan_returned,
    has_unpaid_fine,
    get_loan_limit,
)

DAILY_FINE = 0.50
LOAN_PERIOD = 14


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
            current_fine = calculate_fine(loan[3])

        result["current_fine"] = money(current_fine)

    return result


def write_notification(email, subject, body):
    with open("outbox.txt", "a") as file:
        file.write(
            f"TO: {email} | SUBJECT: {subject} | BODY: {body}\n"
        )


def list_loans(overdue_only=False):
    rows = loan_repository.list_loans()
    result = []

    for loan in rows:
        days_late = calculate_days_late(loan[3])

        if overdue_only and (loan[4] == 1 or days_late <= 0):
            continue

        result.append(
            loan_to_dict(loan, include_current_fine=True)
        )

    return result


def get_loan(loan_id):
    loan = loan_repository.get_loan(loan_id)

    if loan is None:
        return {"error": "loan not found"}, 404

    return loan_to_dict(loan, include_current_fine=True), 200


def create_loan(data):
    if not data.get("book_id") or not data.get("member_id"):
        return {"error": "book_id and member_id are required"}, 400

    if data.get("due_date") and not is_valid_date(data["due_date"]):
        return {"error": "invalid due_date"}, 400

    book = loan_repository.get_book(data["book_id"])

    if book is None:
        return {"error": "book not found"}, 404

    member = loan_repository.get_member(data["member_id"])

    if member is None:
        return {"error": "member not found"}, 404

    if not is_book_available(book):
        return {"error": "book is not available"}, 409

    rows = loan_repository.get_member_loans(data["member_id"])

    owed = 0
    open_loans = 0

    for loan in rows:
        if loan[4] == 0:
            open_loans += 1
            days_late = calculate_days_late(loan[3])

            if days_late > 0:
                owed += days_late * DAILY_FINE

        elif loan[6] == 0:
            owed += loan[5]

    if owed > 0:
        return {"error": "member has unpaid fines"}, 409

    limit = get_loan_limit(member)

    if open_loans >= limit:
        return {"error": "loan limit reached"}, 409

    today = date.today()
    due_date = data.get("due_date") or (
        today + timedelta(days=LOAN_PERIOD)
    ).isoformat()

    loan = loan_repository.create_loan(
        data,
        due_date,
        today.isoformat()
    )

    write_notification(
        member[2],
        "Book checked out",
        "You checked out " + book[1],
    )

    return loan_to_dict(loan), 201


def return_book(loan_id):
    loan = loan_repository.get_loan(loan_id)

    if loan is None:
        return {"error": "loan not found"}, 404

    if is_loan_returned(loan):
        return {"error": "loan already returned"}, 409

    fine = calculate_fine(loan[3])

    loan_repository.return_loan(loan_id, loan[1], fine)

    member = loan_repository.get_member(loan[2])
    book = loan_repository.get_book(loan[1])
    updated = loan_repository.get_loan(loan_id)

    write_notification(
        member[2],
        "Book returned",
        "You returned " + book[1] + ". Fine: $" + str(money(fine)),
    )

    return loan_to_dict(updated), 200


def renew_loan(loan_id):
    loan = loan_repository.get_loan(loan_id)

    if loan is None:
        return {"error": "loan not found"}, 404

    if is_loan_returned(loan):
        return {"error": "loan already returned"}, 409

    if date.fromisoformat(loan[3]) < date.today():
        return {"error": "overdue loans cannot be renewed"}, 409

    if loan[7] >= 1:
        return {"error": "loan was already renewed"}, 409

    new_due_date = (
        date.fromisoformat(loan[3]) + timedelta(days=LOAN_PERIOD)
    ).isoformat()

    loan_repository.renew_loan(loan_id, new_due_date)

    member = loan_repository.get_member(loan[2])
    book = loan_repository.get_book(loan[1])
    updated = loan_repository.get_loan(loan_id)

    write_notification(
        member[2],
        "Loan renewed",
        "You renewed " + book[1],
    )

    return loan_to_dict(updated), 200


def pay_fine(loan_id):
    loan = loan_repository.get_loan(loan_id)

    if loan is None:
        return {"error": "loan not found"}, 404

    if loan[4] == 0:
        return {"error": "return the book before paying"}, 409

    if not has_unpaid_fine(loan):
        return {"error": "no fine to pay"}, 409

    loan_repository.pay_fine(loan_id)

    member = loan_repository.get_member(loan[2])
    updated = loan_repository.get_loan(loan_id)

    write_notification(
        member[2],
        "Fine paid",
        "We received $" + str(money(loan[5])),
    )

    return loan_to_dict(updated), 200
