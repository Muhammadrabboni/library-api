
from datetime import date


DAILY_FINE = 0.50


def money(value):
    return round(float(value), 2)


def calculate_days_late(due_date, current_date=None):
    if current_date is None:
        current_date = date.today()

    return max(0, (current_date - date.fromisoformat(due_date)).days)


def calculate_fine(due_date, current_date=None):
    return money(calculate_days_late(due_date, current_date) * DAILY_FINE)
