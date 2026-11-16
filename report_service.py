import book_repository
import loan_repository
import report_repository

from utils.fines import money, calculate_days_late, calculate_fine


def overdue_report():
    rows = report_repository.list_open_loans_with_details()

    items = []
    total = 0

    for row in rows:
        days_late = calculate_days_late(row["due_date"])

        if days_late > 0:
            fine = calculate_fine(row["due_date"])
            total += fine

            items.append({
                "loan_id": row["id"],
                "title": row["title"],
                "member": row["member_name"],
                "days_late": days_late,
                "fine": money(fine),
            })

    return {
        "items": items,
        "total_fines": money(total),
    }


def summary_report():
    total_books = book_repository.count_books()
    rows = loan_repository.list_loans()

    on_loan = 0
    outstanding = 0

    for loan in rows:
        if loan[4] == 0:
            on_loan += 1
            outstanding += calculate_fine(loan[3])

        elif loan[6] == 0:
            outstanding += loan[5]

    return {
        "total_books": total_books,
        "on_loan": on_loan,
        "fines_outstanding": money(outstanding),
    }