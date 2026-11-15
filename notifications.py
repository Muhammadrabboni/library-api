
def send_notification(email, subject, body):
    """
    Mock notification service.
    Records notifications in outbox.txt instead of sending real emails.
    """
    with open("outbox.txt", "a") as file:
        file.write(
            f"TO: {email} | SUBJECT: {subject} | BODY: {body}\n"
        )
