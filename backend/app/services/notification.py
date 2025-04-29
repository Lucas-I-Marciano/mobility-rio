import smtplib
import os
from email.message import EmailMessage
import dotenv
dotenv.load_dotenv()

def send_notification_email(recipient_email, email_subject, body_plain_text, body_html_content=None):
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    if not SENDER_EMAIL:
        print("Error: SENDER_EMAIL environment variable not set.")
        raise Exception("Error: SENDER_EMAIL environment variable not set.")
    GMAIL_APP_PASSWORD  = os.getenv("GMAIL_APP_PASSWORD")
    if not GMAIL_APP_PASSWORD :
        print("Error: GMAIL_APP_PASSWORD  environment variable not set.")
        raise Exception("Error: GMAIL_APP_PASSWORD  environment variable not set.")

    msg = EmailMessage()
    msg['Subject'] = email_subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg.set_content(body_plain_text)
    if body_html_content:
        msg.add_alternative(body_html_content, subtype='html')
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            print("Connected to Gmail SMTP server...")
            smtp_server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
            print("Login successful...")
            # Send the email
            smtp_server.send_message(msg)
            print(f"Email sent successfully from {SENDER_EMAIL} to {recipient_email}!")

    except smtplib.SMTPAuthenticationError:
        print("Authentication Error: Check your email and App Password.")
        print("Make sure you are using an App Password and not your main password.")
        print("Verify the App Password was entered correctly (16 characters without spaces).")
    except smtplib.SMTPConnectError:
        print("Connection Error: Could not connect to the Gmail SMTP server.")
        print("Check your internet connection or if a firewall is blocking port 465.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")