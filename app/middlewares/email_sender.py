from flask_mail import Message
from flask import current_app

def send_urgent_email(recipients, subject, html_body):
    """
    Sends an email to the specified recipients with the given subject and HTML content.
    """
    msg = Message(subject, recipients=recipients, body=html_body)
    msg.html = html_body  # Set the HTML content for the email.
    current_app.extensions['mail'].send(msg)