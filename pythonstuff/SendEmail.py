import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

EMAIL_SENDER_ADDRESS = os.environ.get("EMAIL_SENDER_ADDRESS")
EMAIL_SENDER_PASSWORD = os.environ.get("EMAIL_SENDER_PASSWORD")
EMAIL_RECEIVER_ADDRESS = os.environ.get("EMAIL_RECEIVER_ADDRESS")

def send_email(subject:str, content:str, to_address:str=EMAIL_RECEIVER_ADDRESS):

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER_ADDRESS
    msg["To"] = to_address
    msg.set_content(content, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_SENDER_ADDRESS, EMAIL_SENDER_PASSWORD)
        smtp.send_message(msg)
