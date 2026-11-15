
def is_book_available(book):
    return book is not None and book[4] == 1


def is_loan_returned(loan):
    return loan[4] == 1


def has_unpaid_fine(loan):
    if loan[4] == 0:
        return False

    return loan[5] > 0 and loan[6] == 0


def get_loan_limit(member):
    return 5 if member[3] == "staff" else 3
