import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()

def send_notification(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv('SMTP_FROM')
    msg['To'] = os.getenv('SMTP_TO')

    with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
        status = server.sendmail(os.getenv('SMTP_FROM'), [os.getenv('SMTP_TO')], msg.as_string())
    return status

if __name__ == "__main__":
    subject = "[IBWRBot] No new orders available",
    body = "There are no new orders available in the database."

    send_notification(
        subject=subject,
        body=body
    )
